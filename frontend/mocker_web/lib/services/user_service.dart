import '../models/user.dart';
import '../data/mock_data.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../config/api_config.dart';
import 'package:firebase_auth/firebase_auth.dart' as firebase_auth;

class UserService extends ChangeNotifier {
  static final UserService _instance = UserService._internal();
  factory UserService() => _instance;
  UserService._internal();

  User? _currentUser;
  User? get currentUser => _currentUser;

  // get current user token
  Future<String?> _getIdToken() async {
    try {
      final user = firebase_auth.FirebaseAuth.instance.currentUser;
      if (user != null) {
        return await user.getIdToken();
      }
      return null;
    } catch (e) {
      debugPrint('Failed to get ID token: $e');
      return null;
    }
  }

  // Get user profile
  Future<User> getUserProfile() async {
    try {
      final token = await _getIdToken();
      if (token == null) {
        throw Exception('No authentication token available');
      }

      debugPrint('Calling GET /user API...');
      
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.userEndpoint}'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final user = User.fromJson(data['data']);
        _currentUser = user;
        debugPrint('✅ Real API: User profile loaded successfully');
        notifyListeners();
        return user;
      } else {
        throw Exception('API returned ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      debugPrint('❌ Real API failed: $e');
      debugPrint('🔄 Falling back to mock data...');
      
      try {
        // Fallback to mock data
        final user = User.fromJson(MockData.userProfile);
        _currentUser = user;
        debugPrint('✅ Mock API: User profile loaded with mock data');
        notifyListeners();
        return user;
      } catch (mockError) {
        debugPrint('❌ Mock data also failed: $mockError');
        throw Exception('Failed to load user profile: Real API failed ($e), Mock data also failed ($mockError)');
      }
    }
  }

  // Update user profile
  Future<User> updateUserProfile(Map<String, dynamic> profileData) async {
    try {
      final token = await _getIdToken();
      if (token == null) {
        throw Exception('No authentication token available');
      }

      debugPrint('Calling PUT /user API...');
      
      final response = await http.put(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.userEndpoint}'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode(profileData),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _currentUser = User.fromJson(data['data']);
        debugPrint('✅ Real API: User profile updated successfully');
        notifyListeners();
        return _currentUser!;
      } else {
        throw Exception('API returned ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      debugPrint('❌ Real API failed: $e');
      debugPrint('🔄 Falling back to mock data...');
      
      try {
        // Mock update (just update local data)
        if (_currentUser != null) {
          // Update local user data for mock using copyWith
          _currentUser = _currentUser!.copyWith(
            name: profileData['name'],
            linkedinLink: profileData['linkedinLink'],
            githubLink: profileData['githubLink'],
            portfolioLink: profileData['portfolioLink'],
            additionalInfo: profileData['additionalInfo'],
          );
          debugPrint('✅ Mock API: User profile updated with mock data');
          notifyListeners();
          return _currentUser!;
        } else {
          throw Exception('No current user data available for mock update');
        }
      } catch (mockError) {
        debugPrint('❌ Mock update also failed: $mockError');
        throw Exception('Failed to update user profile: Real API failed ($e), Mock update also failed ($mockError)');
      }
    }
  }

  // Upload user avatar
  Future<String> uploadAvatar(String imagePath) async {
    try {
      final token = await _getIdToken();
      if (token == null) {
        throw Exception('No authentication token available');
      }

      debugPrint('Calling POST /user/avatar API...');
      
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.userAvatarEndpoint}'),
      );
      
      request.headers['Authorization'] = 'Bearer $token';
      request.files.add(await http.MultipartFile.fromPath('avatar', imagePath));

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final avatarUrl = data['data']['avatarUrl'];
        if (_currentUser != null) {
          _currentUser = _currentUser!.copyWith(
            photoURL: avatarUrl,
          );
        }
        debugPrint('✅ Real API: Avatar uploaded successfully');
        notifyListeners();
        return avatarUrl;
      } else {
        throw Exception('API returned ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      debugPrint('❌ Real API failed: $e');
      debugPrint('🔄 Falling back to mock data...');
      
      try {
        // Mock avatar upload (just simulate success)
        await Future.delayed(Duration(seconds: 1)); // Simulate network delay
        
        final mockAvatarUrl = 'https://via.placeholder.com/150/mock_avatar_${DateTime.now().millisecondsSinceEpoch}';
        
        if (_currentUser != null) {
          // Update with a mock avatar URL
          _currentUser = _currentUser!.copyWith(
            photoURL: mockAvatarUrl,
          );
          debugPrint('✅ Mock API: Avatar uploaded with mock data');
          notifyListeners();
          return mockAvatarUrl;
        } else {
          throw Exception('No current user data available for mock avatar upload');
        }
      } catch (mockError) {
        debugPrint('❌ Mock upload also failed: $mockError');
        throw Exception('Failed to upload avatar: Real API failed ($e), Mock upload also failed ($mockError)');
      }
    }
  }
} 