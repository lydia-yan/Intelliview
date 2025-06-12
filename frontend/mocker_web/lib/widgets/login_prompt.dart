import 'package:flutter/material.dart';
import '../services/auth_service.dart';

class LoginPrompt extends StatelessWidget {
  final AuthService authService;

  const LoginPrompt({super.key, required this.authService});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Container(
        constraints: const BoxConstraints(maxWidth: 500),
        padding: const EdgeInsets.all(48),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: Colors.grey[200]!),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 20,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Logo
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: const Color(0xFFE6CFE6),
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Icon(
                Icons.lock_outline,
                size: 40,
                color: Color(0xFF263238),
              ),
            ),
            
            const SizedBox(height: 32),
            
            // title
            const Text(
              'Welcome to Intelliview',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: Color(0xFF263238),
              ),
              textAlign: TextAlign.center,
            ),
            
            const SizedBox(height: 16),
            
            // description
            Text(
              'Please sign in with your Google account to access your interview preparation dashboard and start practicing.',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[600],
                height: 1.5,
              ),
              textAlign: TextAlign.center,
            ),
            
            const SizedBox(height: 40),
            
            // Google login button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: authService.isLoading ? null : () async {
                  final success = await authService.signInWithGoogle();
                  if (!success && authService.error != null) {
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(authService.error!),
                          backgroundColor: Colors.red,
                        ),
                      );
                    }
                  }
                },
                icon: authService.isLoading 
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : Image.asset(
                        'assets/images/google_logo.png',
                        width: 20,
                        height: 20,
                        errorBuilder: (context, error, stackTrace) {
                          return const Icon(Icons.login, color: Colors.white, size: 20);
                        },
                      ),
                label: Text(
                  authService.isLoading ? 'Signing in...' : 'Sign in with Google',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF263238),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                  elevation: 2,
                ),
              ),
            ),
            
            const SizedBox(height: 24),
            
            // privacy statement
            Text(
              'By signing in, you agree to our terms of service and privacy policy.',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[500],
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
} 