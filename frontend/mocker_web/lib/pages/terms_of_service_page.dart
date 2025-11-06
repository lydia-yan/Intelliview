import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class TermsOfServicePage extends StatelessWidget {
  const TermsOfServicePage({super.key});

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isMobile = screenWidth < 600;

    return Scaffold(
      backgroundColor: AppTheme.lightGray,
      appBar: AppBar(
        title: const Text('Terms of Service'),
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
                  'Terms of Service',
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
                  'Agreement to Terms',
                  'By accessing and using Intelliview ("Service", "Platform", "we", "us", or "our"), you agree to be bound by these Terms of Service. If you disagree with any part of these terms, you may not access the Service.',
                  isMobile,
                ),

                _buildSection(
                  '1. Description of Service',
                  'Intelliview is an AI-powered interview preparation platform that provides:\n\n'
                      '• Mock interview practice sessions\n'
                      '• AI-generated interview questions and feedback\n'
                      '• Resume analysis and optimization suggestions\n'
                      '• Interview performance tracking and analytics\n'
                      '• Resource recommendations for skill improvement',
                  isMobile,
                ),

                _buildSection(
                  '2. User Accounts',
                  'To use our Service, you must:\n\n'
                      '• Provide accurate and complete registration information\n'
                      '• Maintain the security of your account credentials\n'
                      '• Be at least 13 years of age\n'
                      '• Not use the Service for any illegal or unauthorized purpose\n'
                      '• Not attempt to gain unauthorized access to any part of the Service\n\n'
                      'You are responsible for all activities that occur under your account.',
                  isMobile,
                ),

                _buildSection(
                  '3. User Content',
                  'You retain ownership of any content you submit to the Service, including resumes, responses, and other materials. By submitting content, you grant us a license to:\n\n'
                      '• Store and process your content to provide the Service\n'
                      '• Use your content to improve our AI models and features (anonymized)\n'
                      '• Display your content back to you through the platform\n\n'
                      'You are responsible for ensuring you have the right to submit any content.',
                  isMobile,
                ),

                _buildSection(
                  '4. Acceptable Use',
                  'You agree not to:\n\n'
                      '• Use the Service in any way that violates laws or regulations\n'
                      '• Impersonate any person or entity\n'
                      '• Interfere with or disrupt the Service or servers\n'
                      '• Attempt to access data not intended for you\n'
                      '• Use automated systems to access the Service without permission\n'
                      '• Upload malicious code or content\n'
                      '• Harass, abuse, or harm other users',
                  isMobile,
                ),

                _buildSection(
                  '5. AI-Generated Content',
                  'Our Service uses artificial intelligence to generate interview questions, feedback, and recommendations. You acknowledge that:\n\n'
                      '• AI-generated content is provided for educational purposes only\n'
                      '• We do not guarantee the accuracy or completeness of AI suggestions\n'
                      '• AI feedback should be used as guidance, not absolute truth\n'
                      '• You should use your own judgment when applying AI recommendations',
                  isMobile,
                ),

                _buildSection(
                  '6. Intellectual Property',
                  'The Service, including all content, features, and functionality, is owned by Intelliview and is protected by international copyright, trademark, and other intellectual property laws.\n\n'
                      'You may not:\n'
                      '• Copy, modify, or create derivative works of the Service\n'
                      '• Reverse engineer or decompile any part of the Service\n'
                      '• Remove or modify any copyright notices',
                  isMobile,
                ),

                _buildSection(
                  '7. Free Service',
                  'Intelliview is currently a free service. All features and functionality are provided at no cost to users. We reserve the right to introduce paid features or subscriptions in the future, but will provide advance notice to users before implementing any charges.',
                  isMobile,
                ),

                _buildSection(
                  '8. Termination',
                  'We reserve the right to terminate or suspend your account at any time for:\n\n'
                      '• Violation of these Terms of Service\n'
                      '• Fraudulent or illegal activity\n'
                      '• Extended periods of inactivity\n\n'
                      'You may terminate your account at any time through your account settings. Upon termination, your right to use the Service will immediately cease.',
                  isMobile,
                ),

                _buildSection(
                  '9. Disclaimer of Warranties',
                  'THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND. WE DO NOT WARRANT THAT:\n\n'
                      '• The Service will be uninterrupted or error-free\n'
                      '• Defects will be corrected\n'
                      '• The Service is free of viruses or harmful components\n'
                      '• Results obtained from the Service will be accurate or reliable',
                  isMobile,
                ),

                _buildSection(
                  '10. Limitation of Liability',
                  'TO THE MAXIMUM EXTENT PERMITTED BY LAW, WE SHALL NOT BE LIABLE FOR:\n\n'
                      '• Any indirect, incidental, special, or consequential damages\n'
                      '• Loss of profits, data, or business opportunities\n'
                      '• Damages arising from your use or inability to use the Service\n\n'
                      'As this is a free service, our liability is limited to the maximum extent permitted by law.',
                  isMobile,
                ),

                _buildSection(
                  '11. Changes to Terms',
                  'We reserve the right to modify these Terms of Service at any time. We will notify you of material changes by:\n\n'
                      '• Posting the new terms on the platform\n'
                      '• Sending you an email notification\n'
                      '• Displaying a prominent notice on the Service\n\n'
                      'Your continued use of the Service after changes constitutes acceptance of the new terms.',
                  isMobile,
                ),

                _buildSection(
                  '12. Governing Law',
                  'These Terms shall be governed by and construed in accordance with the laws of the jurisdiction in which we operate, without regard to its conflict of law provisions.',
                  isMobile,
                ),

                _buildSection(
                  '13. Contact Information',
                  'If you have any questions about these Terms of Service, please contact us at:\n\n'
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

