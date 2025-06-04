import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../models/interview.dart';
import '../services/interview_service.dart';
import '../widgets/navbar.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import '../theme/app_theme.dart';

class InterviewPreparePage extends StatefulWidget {
  final VoidCallback? onNavigateToDashboard;
  
  const InterviewPreparePage({super.key, this.onNavigateToDashboard});

  @override
  State<InterviewPreparePage> createState() => _InterviewPreparePageState();
}

class _InterviewPreparePageState extends State<InterviewPreparePage> {
  final InterviewService _interviewService = InterviewService();
  
  PlatformFile? _resumeFile;
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _linkedinController = TextEditingController();
  final TextEditingController _githubController = TextEditingController();
  final TextEditingController _portfolioController = TextEditingController();
  final TextEditingController _additionalController = TextEditingController();
  final TextEditingController _jobDescController = TextEditingController();

  bool _submitting = false;

  Future<void> _pickResume() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
    );
    if (result != null && result.files.isNotEmpty) {
      setState(() {
        _resumeFile = result.files.first;
      });
    }
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate() || _resumeFile == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please complete all required fields and upload your resume PDF.')),
      );
      return;
    }
    
    // prevent duplicate submission
    if (_submitting) return;
    
    setState(() => _submitting = true);
    
    // show loading dialog
    _showLoadingDialog();
    
    try {
      final request = InterviewPrepareRequest(
        resumeFile: _resumeFile!,
        jobDescription: _jobDescController.text,
        linkedinLink: _linkedinController.text,
        githubLink: _githubController.text,
        portfolioLink: _portfolioController.text.isEmpty ? null : _portfolioController.text,
        additionalInfo: _additionalController.text.isEmpty ? null : _additionalController.text,
      );
      // get idToken
      final authService = Provider.of<AuthService>(context, listen: false);
      final idToken = await authService.currentUser?.getIdToken();
      if (idToken == null) {
        if (mounted) {
          setState(() => _submitting = false);
          Navigator.of(context).pop(); // close loading dialog
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('User not authenticated. Please login again.')),
          );
        }
        return;
      }
      final response = await _interviewService.submitInterviewPreparation(request, idToken);
      if (mounted) {
        setState(() => _submitting = false);
        Navigator.of(context).pop(); // close loading dialog
        if (response.success) {
          _showSuccessDialog(response);
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error: ${response.message}')),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() => _submitting = false);
        Navigator.of(context).pop(); // close loading dialog
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to submit: $e')),
        );
      }
    }
  }

  void _showLoadingDialog() {
    showDialog(
      context: context,
      barrierDismissible: false, // disable clicking outside to close
      builder: (ctx) => PopScope(
        canPop: false, // disable back button
        child: AlertDialog(
          backgroundColor: Colors.white, 
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          contentPadding: const EdgeInsets.all(32), 
          content: Container(
            width: 500, 
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const SizedBox(
                  width: 50,
                  height: 50,
                  child: CircularProgressIndicator(
                    strokeWidth: 4,
                    color: Color(0xFF263238),
                  ),
                ),
                const SizedBox(height: 24),
                const Text(
                  'Generating interview preparation materials...',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF263238),
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                Text(
                  'It usually takes 2-3 minutes to generate the materials. Once completed, they will automatically appear in the dashboard.',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                Text(
                  'You can exit this page and come back later to view the results.',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 32),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () => _goToDashboard(),
                    icon: const Icon(Icons.dashboard),
                    label: const Text('Back to Dashboard'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF263238),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: TextButton(
                    onPressed: () => Navigator.of(ctx).pop(),
                    child: Text(
                      'Continue waiting',
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 14,
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

  void _goToDashboard() {
    Navigator.of(context).pop(); // close dialog
    
    widget.onNavigateToDashboard?.call();
  }

  void _showSuccessDialog(InterviewPrepareResponse response) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            Icon(Icons.check_circle, color: Colors.green, size: 28),
            const SizedBox(width: 12),
            const Text('Interview preparation completed', style: TextStyle(color: Color(0xFF263238))),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Status: ${response.success ? "Success" : "Failed"}'),
              if (response.message.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text('Message: ${response.message}'),
              ],
              if (response.sessionId != null) ...[
                const SizedBox(height: 8),
                Text('Session ID: ${response.sessionId}'),
              ],
              if (response.workflowId != null) ...[
                const SizedBox(height: 8),
                Text('Workflow ID: ${response.workflowId}'),
              ],
              if (response.completedAgents != null && response.completedAgents!.isNotEmpty) ...[
                const SizedBox(height: 12),
                const Text('Completed steps:', style: TextStyle(fontWeight: FontWeight.bold)),
                ...response.completedAgents!.map((agent) => Text('• $agent')),
              ],
              if (response.processingTime != null) ...[
                const SizedBox(height: 8),
                Text('Processing time: ${response.processingTime!.toStringAsFixed(1)} seconds'),
              ],
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green[50],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green[200]!),
                ),
                child: const Text(
                  'Interview preparation materials have been generated! You can now view them in the dashboard and start the mock interview.',
                  style: TextStyle(color: Color(0xFF2E7D32)),
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('View Later'),
          ),
          ElevatedButton.icon(
            onPressed: () {
              Navigator.of(ctx).pop();
              _goToDashboard();
            },
            icon: const Icon(Icons.dashboard),
            label: const Text('Go to Dashboard'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF263238),
              foregroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _linkedinController.dispose();
    _githubController.dispose();
    _portfolioController.dispose();
    _additionalController.dispose();
    _jobDescController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // NavBar
        NavBar(
          title: 'Prepare Interview',
        ),
        
        // Main content
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 32.0, vertical: 32.0),
            child: Center(
              child: Container(
                constraints: const BoxConstraints(maxWidth: 1200),
                child: Card(
                  elevation: 8,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                  color: Colors.white,
                  shadowColor: Colors.black.withValues(alpha: 0.1),
                  child: Container(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: AppTheme.borderGray, width: 1.5),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(48.0),
                      child: Form(
                        key: _formKey,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // Header section
                            const Text(
                              'Interview Preparation',
                              style: TextStyle(
                                fontSize: 28,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF263238),
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'Upload your resume and provide additional information to prepare for your interview',
                              style: TextStyle(
                                fontSize: 16,
                                color: Colors.grey[600],
                              ),
                            ),
                            const SizedBox(height: 40),
                            
                            // Two-column layout
                            IntrinsicHeight(
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.stretch,
                                children: [
                                  // Left column: Resume + Professional Links
                                  Expanded(
                                    flex: 1,
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        // Resume upload section
                                        _buildSection(
                                          title: 'Resume',
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              OutlinedButton.icon(
                                                icon: Icon(
                                                  _resumeFile == null ? Icons.upload_file : Icons.check_circle,
                                                  color: _resumeFile == null ? const Color(0xFF263238) : Colors.green,
                                                ),
                                                label: Text(
                                                  _resumeFile == null ? 'Upload Resume PDF' : _resumeFile!.name,
                                                  style: TextStyle(
                                                    color: _resumeFile == null ? const Color(0xFF263238) : Colors.green,
                                                    fontWeight: FontWeight.w500,
                                                  ),
                                                ),
                                                style: OutlinedButton.styleFrom(
                                                  side: BorderSide(
                                                    color: _resumeFile == null ? const Color(0xFF263238) : Colors.green,
                                                  ),
                                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                                  padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 20),
                                                  minimumSize: const Size(double.infinity, 56),
                                                ),
                                                onPressed: _pickResume,
                                              ),
                                              if (_resumeFile == null)
                                                const Padding(
                                                  padding: EdgeInsets.only(top: 8),
                                                  child: Text(
                                                    '* Required - Please upload your resume in PDF format',
                                                    style: TextStyle(color: Colors.red, fontSize: 14),
                                                  ),
                                                ),
                                            ],
                                          ),
                                        ),
                                        
                                        const SizedBox(height: 32),
                                        
                                        // Professional Links section
                                        _buildSection(
                                          title: 'Professional Links',
                                          child: Column(
                                            children: [
                                              _buildFormField(
                                                controller: _linkedinController,
                                                label: 'LinkedIn URL (Optional)',
                                                icon: Icons.work,
                                              ),
                                              const SizedBox(height: 20),
                                              _buildFormField(
                                                controller: _githubController,
                                                label: 'GitHub URL (Optional)',
                                                icon: Icons.code,
                                              ),
                                              const SizedBox(height: 20),
                                              _buildFormField(
                                                controller: _portfolioController,
                                                label: 'Portfolio URL (Optional)',
                                                icon: Icons.web,
                                              ),
                                            ],
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                  
                                  // Vertical divider
                                  Container(
                                    width: 1,
                                    margin: const EdgeInsets.symmetric(horizontal: 32),
                                    decoration: BoxDecoration(
                                      color: Colors.grey[300],
                                    ),
                                  ),
                                  
                                  // Right column: Additional Info + Job Description
                                  Expanded(
                                    flex: 1,
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        // Additional info section
                                        _buildSection(
                                          title: 'Additional Information',
                                          child: _buildFormField(
                                            controller: _additionalController,
                                            label: 'Tell us more about yourself, your projects, achievements, etc.',
                                            icon: Icons.info_outline,
                                            maxLines: 5,
                                          ),
                                        ),
                                        
                                        const SizedBox(height: 32),
                                        
                                        // Job description section
                                        _buildSection(
                                          title: 'Job Description',
                                          child: _buildFormField(
                                            controller: _jobDescController,
                                            label: 'Paste the job description here',
                                            icon: Icons.description,
                                            maxLines: 6,
                                            validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            
                            const SizedBox(height: 40),
                            
                            // Submit button (centered)
                            Center(
                              child: SizedBox(
                                width: 300,
                                child: ElevatedButton(
                                  onPressed: _submitting ? null : _submit,
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: const Color(0xFF263238),
                                    foregroundColor: Colors.white,
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                    padding: const EdgeInsets.symmetric(vertical: 18),
                                    elevation: 2,
                                  ),
                                  child: _submitting
                                      ? Row(
                                          mainAxisAlignment: MainAxisAlignment.center,
                                          children: const [
                                            SizedBox(
                                              width: 16,
                                              height: 16,
                                              child: CircularProgressIndicator(
                                                strokeWidth: 2,
                                                color: Colors.white,
                                              ),
                                            ),
                                            SizedBox(width: 12),
                                            Text(
                                              'Processing...',
                                              style: TextStyle(fontSize: 16),
                                            ),
                                          ],
                                        )
                                      : const Text(
                                          'Submit Interview Preparation',
                                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                                        ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSection({required String title, required Widget child}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w600,
            color: Color(0xFF263238),
          ),
        ),
        const SizedBox(height: 12),
        child,
      ],
    );
  }

  Widget _buildFormField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    String? Function(String?)? validator,
    int maxLines = 1,
  }) {
    return TextFormField(
      controller: controller,
      validator: validator,
      maxLines: maxLines,
      style: const TextStyle(
        fontSize: 15,
        color: Color(0xFF263238),
      ),
      decoration: InputDecoration(
        labelText: label,
        labelStyle: TextStyle(
          fontSize: 14,
          color: Colors.grey[600],
        ),
        prefixIcon: Container(
          margin: const EdgeInsets.all(12),
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: const Color(0xFF263238).withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: const Color(0xFF263238), size: 18),
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.grey[300]!),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFF263238), width: 2),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.grey[300]!),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Colors.red, width: 1),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Colors.red, width: 2),
        ),
        filled: true,
        fillColor: Colors.grey[50],
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        floatingLabelBehavior: FloatingLabelBehavior.auto,
      ),
    );
  }
} 