import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:sign_in_with_apple/sign_in_with_apple.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../config/api_config.dart';
import '../data/mock_data.dart';

class AuthService extends ChangeNotifier {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final GoogleSignIn _googleSignIn = GoogleSignIn(
    clientId: kIsWeb
        ? '1022761324834-ma82nm7e3cvck3bgv2k6rjnlakn33flm.apps.googleusercontent.com'
        : null,
    scopes: ['email', 'profile'],
  );

  User? _user;
  bool _isLoading = false;
  String? _error;
  Map<String, dynamic>? _userProfile; // store user profile from backend

  // Getters
  User? get currentUser => _user;
  bool get isLoggedIn => _user != null;
  bool get isLoading => _isLoading;
  String? get error => _error;
  String? get userEmail => _user?.email;
  String? get userName => _user?.displayName;
  String? get userPhotoURL => _user?.photoURL;
  Map<String, dynamic>? get userProfile => _userProfile;

  AuthService() {
    // listen Firebase auth state changes
    _auth.authStateChanges().listen((User? user) {
      _user = user;
      if (user != null) {
        _initializeUser(); // user login, call backend to initialize
      } else {
        _userProfile = null; // user logout, clear profile
      }
      notifyListeners();
    });
  }

  // get current user's ID Token
  Future<String?> _getIdToken() async {
    try {
      final user = _auth.currentUser;
      if (user != null) {
        return await user.getIdToken();
      }
      return null;
    } catch (e) {
      debugPrint('Failed to get ID token: $e');
      return null;
    }
  }

  // call backend /auth/init to initialize user
  Future<void> _initializeUser() async {
    try {
      final token = await _getIdToken();
      if (token == null) {
        throw Exception('No authentication token available');
      }

      debugPrint('Calling /auth/init API...');

      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.authInitEndpoint}'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _userProfile = data['data'];
        debugPrint('✅ Real API: User initialized successfully');
        notifyListeners();
        return;
      } else {
        throw Exception(
          'API returned ${response.statusCode}: ${response.body}',
        );
      }
    } catch (e) {
      debugPrint('❌ Real API failed: $e');
      debugPrint('🔄 Falling back to mock data...');

      // Fallback to mock data
      _userProfile = MockData.authInitResponse['data'];
      debugPrint('✅ Mock API: User initialized with mock data');
      notifyListeners();
    }
  }

  // Google sign in
  Future<bool> signInWithGoogle() async {
    try {
      _setLoading(true);
      _clearError();

      // start Google sign in process
      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();

      if (googleUser == null) {
        // user cancelled sign in
        _setLoading(false);
        return false;
      }

      // get authentication details
      final GoogleSignInAuthentication googleAuth =
          await googleUser.authentication;

      // create Firebase credentials
      final credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      // sign in Firebase with credentials
      final UserCredential userCredential = await _auth.signInWithCredential(
        credential,
      );

      _user = userCredential.user;
      _setLoading(false);

      if (kDebugMode) {
        print('Google sign in successful: ${_user?.email}');
      }

      return true;
    } catch (e) {
      _setError('sign in failed: ${e.toString()}');
      _setLoading(false);
      if (kDebugMode) {
        print('Google sign in error: $e');
      }
      return false;
    }
  }

  // Apple sign in
  Future<bool> signInWithApple() async {
    try {
      _setLoading(true);
      _clearError();

      // Check if Apple Sign In is available
      if (!await SignInWithApple.isAvailable()) {
        _setError('Apple Sign In is not available on this device');
        _setLoading(false);
        return false;
      }

      // Request Apple ID credential
      final appleCredential = await SignInWithApple.getAppleIDCredential(
        scopes: [
          AppleIDAuthorizationScopes.email,
          AppleIDAuthorizationScopes.fullName,
        ],
      );

      // Create OAuth credential for Firebase
      final oauthCredential = OAuthProvider("apple.com").credential(
        idToken: appleCredential.identityToken,
        accessToken: appleCredential.authorizationCode,
      );

      // Sign in to Firebase with Apple credential
      final UserCredential userCredential = await _auth.signInWithCredential(
        oauthCredential,
      );

      _user = userCredential.user;

      // Update display name if available from Apple and not already set
      if (_user != null && appleCredential.givenName != null && appleCredential.familyName != null) {
        final displayName = '${appleCredential.givenName} ${appleCredential.familyName}';
        if (_user!.displayName == null || _user!.displayName!.isEmpty) {
          await _user!.updateDisplayName(displayName);
          await _user!.reload();
          _user = _auth.currentUser;
        }
      }

      _setLoading(false);

      if (kDebugMode) {
        print('Apple sign in successful: ${_user?.email}');
      }

      return true;
    } catch (e) {
      _setError('Apple sign in failed: ${e.toString()}');
      _setLoading(false);
      if (kDebugMode) {
        print('Apple sign in error: $e');
      }
      return false;
    }
  }

  // Email/Password sign up
  Future<bool> signUpWithEmail(String email, String password, String displayName) async {
    try {
      _setLoading(true);
      _clearError();

      // Create user with email and password
      final UserCredential userCredential = await _auth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );

      _user = userCredential.user;

      // Update display name
      if (_user != null) {
        await _user!.updateDisplayName(displayName);
        await _user!.reload();
        _user = _auth.currentUser;
        
        // Send email verification
        await _user!.sendEmailVerification();
        
        if (kDebugMode) {
          print('Email sign up successful: ${_user?.email}');
          print('Verification email sent');
        }
      }

      _setLoading(false);
      return true;
    } on FirebaseAuthException catch (e) {
      String errorMessage = 'Registration failed';
      
      switch (e.code) {
        case 'email-already-in-use':
          errorMessage = 'This email is already registered';
          break;
        case 'invalid-email':
          errorMessage = 'Invalid email address';
          break;
        case 'weak-password':
          errorMessage = 'Password is too weak';
          break;
        case 'operation-not-allowed':
          errorMessage = 'Email/password sign up is not enabled';
          break;
        default:
          errorMessage = 'Registration failed: ${e.message}';
      }
      
      _setError(errorMessage);
      _setLoading(false);
      if (kDebugMode) {
        print('Email sign up error: $e');
      }
      return false;
    } catch (e) {
      _setError('Registration failed: ${e.toString()}');
      _setLoading(false);
      if (kDebugMode) {
        print('Email sign up error: $e');
      }
      return false;
    }
  }

  // Email/Password sign in
  Future<bool> signInWithEmail(String email, String password) async {
    try {
      _setLoading(true);
      _clearError();

      final UserCredential userCredential = await _auth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );

      _user = userCredential.user;
      _setLoading(false);

      if (kDebugMode) {
        print('Email sign in successful: ${_user?.email}');
      }

      return true;
    } on FirebaseAuthException catch (e) {
      String errorMessage = 'Login failed';
      
      switch (e.code) {
        case 'user-not-found':
          errorMessage = 'No account found with this email';
          break;
        case 'wrong-password':
          errorMessage = 'Incorrect password';
          break;
        case 'invalid-email':
          errorMessage = 'Invalid email address';
          break;
        case 'user-disabled':
          errorMessage = 'This account has been disabled';
          break;
        case 'invalid-credential':
          errorMessage = 'Invalid email or password';
          break;
        default:
          errorMessage = 'Login failed: ${e.message}';
      }
      
      _setError(errorMessage);
      _setLoading(false);
      if (kDebugMode) {
        print('Email sign in error: $e');
      }
      return false;
    } catch (e) {
      _setError('Login failed: ${e.toString()}');
      _setLoading(false);
      if (kDebugMode) {
        print('Email sign in error: $e');
      }
      return false;
    }
  }

  // Send email verification
  Future<bool> sendEmailVerification() async {
    try {
      if (_user != null && !_user!.emailVerified) {
        await _user!.sendEmailVerification();
        if (kDebugMode) {
          print('Verification email sent to ${_user?.email}');
        }
        return true;
      }
      return false;
    } catch (e) {
      _setError('Failed to send verification email: ${e.toString()}');
      if (kDebugMode) {
        print('Send verification email error: $e');
      }
      return false;
    }
  }

  // Check if email is verified
  Future<bool> checkEmailVerified() async {
    try {
      await _user?.reload();
      _user = _auth.currentUser;
      notifyListeners();
      return _user?.emailVerified ?? false;
    } catch (e) {
      if (kDebugMode) {
        print('Check email verified error: $e');
      }
      return false;
    }
  }

  // Send password reset email
  Future<bool> sendPasswordResetEmail(String email) async {
    try {
      _setLoading(true);
      _clearError();
      
      await _auth.sendPasswordResetEmail(email: email);
      
      _setLoading(false);
      if (kDebugMode) {
        print('Password reset email sent to $email');
      }
      return true;
    } on FirebaseAuthException catch (e) {
      String errorMessage = 'Failed to send reset email';
      
      switch (e.code) {
        case 'user-not-found':
          errorMessage = 'No account found with this email';
          break;
        case 'invalid-email':
          errorMessage = 'Invalid email address';
          break;
        default:
          errorMessage = 'Failed to send reset email: ${e.message}';
      }
      
      _setError(errorMessage);
      _setLoading(false);
      if (kDebugMode) {
        print('Password reset error: $e');
      }
      return false;
    } catch (e) {
      _setError('Failed to send reset email: ${e.toString()}');
      _setLoading(false);
      if (kDebugMode) {
        print('Password reset error: $e');
      }
      return false;
    }
  }

  // Get email verification status
  bool get isEmailVerified => _user?.emailVerified ?? false;

  // Check if user needs email verification (signed up with email but not verified)
  bool get needsEmailVerification {
    if (_user == null) return false;
    // Check if user signed up with email/password (not Google)
    final providerData = _user!.providerData;
    final hasEmailProvider = providerData.any((info) => info.providerId == 'password');
    return hasEmailProvider && !_user!.emailVerified;
  }

  // sign out
  Future<void> signOut() async {
    try {
      _setLoading(true);
      _clearError();

      // sign out Google and Firebase
      await Future.wait([_auth.signOut(), _googleSignIn.signOut()]);

      _user = null;
      _userProfile = null;
      _setLoading(false);

      if (kDebugMode) {
        print('sign out successful');
      }
    } catch (e) {
      _setError('sign out failed: ${e.toString()}');
      _setLoading(false);
      if (kDebugMode) {
        print('sign out error: $e');
      }
    }
  }

  // Delete user account and all data
  Future<bool> deleteAccount() async {
    try {
      _setLoading(true);
      _clearError();

      if (_user == null) {
        _setError('No user logged in');
        _setLoading(false);
        return false;
      }

      final userId = _user!.uid;

      // Step 1: Delete all Firestore data
      await _deleteUserFirestoreData(userId);

      // Step 2: Delete Firebase Authentication account
      await _user!.delete();

      _user = null;
      _userProfile = null;
      _setLoading(false);

      if (kDebugMode) {
        print('Account deleted successfully');
      }

      return true;
    } on FirebaseAuthException catch (e) {
      String errorMessage = 'Failed to delete account';
      
      if (e.code == 'requires-recent-login') {
        errorMessage = 'For security, please sign out and sign in again before deleting your account.';
      }
      
      _setError(errorMessage);
      _setLoading(false);
      if (kDebugMode) {
        print('Delete account error: $e');
      }
      return false;
    } catch (e) {
      _setError('Failed to delete account: ${e.toString()}');
      _setLoading(false);
      if (kDebugMode) {
        print('Delete account error: $e');
      }
      return false;
    }
  }

  // Helper method to delete all user data from Firestore
  Future<void> _deleteUserFirestoreData(String userId) async {
    try {
      final firestore = FirebaseFirestore.instance;
      
      // Delete workflows collection and its subcollections
      final workflowsRef = firestore.collection('users').doc(userId).collection('workflows');
      final workflowSnapshots = await workflowsRef.get();
      
      for (var doc in workflowSnapshots.docs) {
        await doc.reference.delete();
      }
      
      // Delete interviews collection and its subcollections
      final interviewsRef = firestore.collection('users').doc(userId).collection('interviews');
      final interviewSnapshots = await interviewsRef.get();
      
      for (var interviewDoc in interviewSnapshots.docs) {
        // Delete sessions subcollection
        final sessionsRef = interviewDoc.reference.collection('sessions');
        final sessionSnapshots = await sessionsRef.get();
        
        for (var sessionDoc in sessionSnapshots.docs) {
          await sessionDoc.reference.delete();
        }
        
        await interviewDoc.reference.delete();
      }
      
      // Delete user document (profile)
      await firestore.collection('users').doc(userId).delete();
      
      if (kDebugMode) {
        print('All Firestore data deleted for user: $userId');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error deleting Firestore data: $e');
      }
      // Continue with account deletion even if Firestore cleanup fails
    }
  }

  // get user ID (get from backend profile, if not, use email)
  String? getUserId() {
    if (_userProfile != null && _userProfile!['user'] != null) {
      return _userProfile!['user']['userId'];
    }
    return _user?.email;
  }

  // check if user is authenticated
  bool isAuthenticated() {
    return _user != null;
  }

  // check if user is new
  bool isNewUser() {
    if (_userProfile != null && _userProfile!['user'] != null) {
      return _userProfile!['user']['isNew'] ?? false;
    }
    return false;
  }

  // private method
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  void _setError(String error) {
    _error = error;
    notifyListeners();
  }

  void _clearError() {
    _error = null;
    notifyListeners();
  }
}
