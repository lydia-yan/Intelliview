import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class PrivacyPolicyPage extends StatelessWidget {
  const PrivacyPolicyPage({super.key});

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isMobile = screenWidth < 600;

    return Scaffold(
      backgroundColor: AppTheme.lightGray,
      appBar: AppBar(
        title: const Text('Privacy Policy'),
        backgroundColor: AppTheme.surfaceWhite,
        foregroundColor: AppTheme.darkGray,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: AppTheme.darkGray),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: Center(
        child: Container(
          constraints: const BoxConstraints(maxWidth: 800),
          margin: EdgeInsets.all(isMobile ? 16 : 32),
          padding: EdgeInsets.all(isMobile ? 24 : 40),
          decoration: BoxDecoration(
            color: AppTheme.surfaceWhite,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppTheme.borderGray),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.05),
                blurRadius: 10,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Privacy Policy',
                  style: TextStyle(
                    fontSize: isMobile ? 28 : 32,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.darkGray,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Last updated: ${DateTime.now().year}-${DateTime.now().month.toString().padLeft(2, '0')}-${DateTime.now().day.toString().padLeft(2, '0')}',
                  style: TextStyle(
                    fontSize: 14,
                    color: AppTheme.mediumGray,
                  ),
                ),
                const SizedBox(height: 32),

                _buildSection(
                  'Introduction',
                  'Welcome to Intelliview. We respect your privacy and are committed to protecting your personal data. This privacy policy will inform you about how we look after your personal data and tell you about your privacy rights.',
                  isMobile,
                ),

                _buildSection(
                  '1. Information We Collect',
                  'We collect and process the following types of information:\n\n'
                      '• Account Information: Name, email address, and profile information when you register\n'
                      '• Usage Data: Information about how you use our service, including interview sessions, transcripts, and feedback\n'
                      '• Technical Data: IP address, browser type, device information, and operating system\n'
                      '• Resume Data: Information you provide through resume uploads for interview preparation',
                  isMobile,
                ),

                _buildSection(
                  '2. How We Use Your Information',
                  'We use your personal data for the following purposes:\n\n'
                      '• To provide and maintain our service\n'
                      '• To personalize your interview preparation experience\n'
                      '• To generate AI-powered interview feedback and recommendations\n'
                      '• To improve our services and develop new features\n'
                      '• To communicate with you about updates and support\n'
                      '• To ensure the security and integrity of our platform',
                  isMobile,
                ),

                _buildSection(
                  '3. Data Storage and Security',
                  'We implement appropriate technical and organizational measures to protect your personal data:\n\n'
                      '• Data is stored securely using Firebase and Google Cloud Platform\n'
                      '• We use encryption for data transmission and storage\n'
                      '• Access to personal data is restricted to authorized personnel only\n'
                      '• We regularly review and update our security measures',
                  isMobile,
                ),

                _buildSection(
                  '4. Third-Party Services',
                  'We use the following third-party services:\n\n'
                      '• Firebase Authentication: For secure user authentication\n'
                      '• Google Cloud AI: For AI-powered interview features\n'
                      '• Firebase Firestore: For secure data storage\n\n'
                      'These services have their own privacy policies governing the use of your information.',
                  isMobile,
                ),

                _buildSection(
                  '5. Your Rights',
                  'You have the following rights regarding your personal data:\n\n'
                      '• Access: Request copies of your personal data\n'
                      '• Correction: Request correction of inaccurate data\n'
                      '• Deletion: Request deletion of your personal data\n'
                      '• Restriction: Request restriction of processing your data\n'
                      '• Portability: Request transfer of your data to another service\n'
                      '• Objection: Object to our processing of your data',
                  isMobile,
                ),

                _buildSection(
                  '6. Data Retention',
                  'We retain your personal data only for as long as necessary to fulfill the purposes outlined in this privacy policy. You can request deletion of your account and associated data at any time through your profile settings.',
                  isMobile,
                ),

                _buildSection(
                  '7. Children\'s Privacy',
                  'Our service is not intended for children under 13 years of age. We do not knowingly collect personal information from children under 13. If you are a parent or guardian and believe your child has provided us with personal information, please contact us.',
                  isMobile,
                ),

                _buildSection(
                  '8. Changes to This Policy',
                  'We may update this privacy policy from time to time. We will notify you of any changes by posting the new privacy policy on this page and updating the "Last updated" date.',
                  isMobile,
                ),

                _buildSection(
                  '9. Contact Us',
                  'If you have any questions about this privacy policy or our data practices, please contact us at:\n\n'
                      'Email: intelliview3@gmail.com',
                  isMobile,
                ),

                const SizedBox(height: 40),

                // Back Button
                Center(
                  child: SizedBox(
                    width: isMobile ? double.infinity : 300,
                    child: ElevatedButton(
                      onPressed: () => Navigator.of(context).pop(),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.primaryBlue,
                        foregroundColor: AppTheme.surfaceWhite,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 32,
                          vertical: 16,
                        ),
                        elevation: 0,
                      ),
                      child: const Text(
                        'Close',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSection(String title, String content, bool isMobile) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: isMobile ? 18 : 20,
              fontWeight: FontWeight.bold,
              color: AppTheme.darkGray,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            content,
            style: TextStyle(
              fontSize: 15,
              color: AppTheme.darkGray,
              height: 1.6,
            ),
          ),
        ],
      ),
    );
  }
}

