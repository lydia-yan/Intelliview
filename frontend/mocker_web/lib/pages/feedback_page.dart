import 'package:flutter/material.dart';
import '../services/interview_service.dart';
import '../services/workflow_service.dart';
import '../models/workflow.dart';
import '../widgets/navbar.dart';
import '../theme/app_theme.dart';
import 'package:url_launcher/url_launcher.dart';


enum ContentType {
  list,        
  transcript,  
  feedback     
}

class FeedbackPage extends StatefulWidget {
  const FeedbackPage({super.key});

  @override
  State<FeedbackPage> createState() => _FeedbackPageState();
}

class _FeedbackPageState extends State<FeedbackPage> {
  final InterviewService _interviewService = InterviewService();
  final WorkflowService _workflowService = WorkflowService();
  
  ContentType _currentContentType = ContentType.list;
  
  List<Map<String, dynamic>> _interviewHistory = [];
  List<Workflow> _workflows = [];
  Workflow? _selectedWorkflow;
  Map<String, dynamic>? _selectedInterview;
  bool _loadingInterviews = true;
  bool _loadingWorkflows = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadWorkflows();
  }

  Future<void> _loadWorkflows() async {
    try {
      setState(() {
        _loadingWorkflows = true;
        _error = null;
      });

      final workflows = await _workflowService.getWorkflows();
      
      setState(() {
        _workflows = workflows;
        _loadingWorkflows = false;
        
        // If there are workflows, select the first one by default
        if (workflows.isNotEmpty) {
          _selectedWorkflow = workflows.first;
          _loadInterviewHistory(_selectedWorkflow!.workflowId);
        } else {
          _loadingInterviews = false;
        }
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loadingWorkflows = false;
        _loadingInterviews = false;
      });
    }
  }

  Future<void> _loadInterviewHistory(String workflowId) async {
    try {
      setState(() {
        _loadingInterviews = true;
        _error = null;
      });

      final history = await _interviewService.getInterviewHistory(workflowId);
      
      setState(() {
        _interviewHistory = history;
        _loadingInterviews = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loadingInterviews = false;
      });
    }
  }

  void _selectWorkflow(Workflow workflow) {
    setState(() {
      _selectedWorkflow = workflow;
      _loadInterviewHistory(workflow.workflowId);
    });
  }

  void _viewTranscript(Map<String, dynamic> interview) {
    setState(() {
      _selectedInterview = interview;
      _currentContentType = ContentType.transcript;
    });
  }

  void _viewFeedback(Map<String, dynamic> interview) {
    setState(() {
      _selectedInterview = interview;
      _currentContentType = ContentType.feedback;
    });
  }

  void _backToList() {
    setState(() {
      _currentContentType = ContentType.list;
      _selectedInterview = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // NavBar
        NavBar(
          title: _getPageTitle(),
          actions: _currentContentType != ContentType.list ? [
            TextButton.icon(
              onPressed: _backToList,
              icon: const Icon(Icons.arrow_back, size: 18),
              label: const Text('Back to History'),
              style: TextButton.styleFrom(
                foregroundColor: AppTheme.darkGray,
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              ),
            ),
          ] : null,
        ),
        
        // Main content
        Expanded(
          child: _buildCurrentContent(),
        ),
      ],
    );
  }

  String _getPageTitle() {
    switch (_currentContentType) {
      case ContentType.list:
        return 'Interview Feedback History';
      case ContentType.transcript:
        return 'Interview Transcript';
      case ContentType.feedback:
        return 'Interview Feedback';
    }
  }

  Widget _buildCurrentContent() {
    switch (_currentContentType) {
      case ContentType.list:
        return _buildHistoryList();
      case ContentType.transcript:
        return _buildTranscriptView();
      case ContentType.feedback:
        return _buildFeedbackView();
    }
  }

  Widget _buildHistoryList() {
    if (_loadingWorkflows) {
      return const Center(
        child: SizedBox(
          width: 32,
          height: 32,
          child: CircularProgressIndicator(
            strokeWidth: 3,
            color: Color(0xFF263238),
          ),
        ),
      );
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: Colors.red[300]),
            const SizedBox(height: 16),
            Text(
              'Failed to load data',
              style: TextStyle(
                fontSize: MediaQuery.of(context).size.width < 600 ? 18 : 20,
                fontWeight: FontWeight.bold,
                color: Colors.red[700],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              _error!,
              style: const TextStyle(color: Colors.red),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _loadWorkflows,
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF263238),
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      );
    }

    if (_workflows.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.work_outline, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              'No interview positions yet',
              style: TextStyle(
                fontSize: MediaQuery.of(context).size.width < 600 ? 16 : 18, 
                color: Colors.grey[600]
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Prepare for an interview first to see your feedback history',
              style: TextStyle(
                fontSize: MediaQuery.of(context).size.width < 600 ? 12 : 14, 
                color: Colors.grey[500]
              ),
            ),
          ],
        ),
      );
    }

    return Padding(
      padding: EdgeInsets.symmetric(
        horizontal: MediaQuery.of(context).size.width < 600 ? 16.0 : 64.0, 
        vertical: MediaQuery.of(context).size.width < 600 ? 16.0 : 32.0
      ),
      child: Center(
        child: Container(
          constraints: const BoxConstraints(maxWidth: 1000),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Interview History',
                style: TextStyle(
                  fontSize: MediaQuery.of(context).size.width < 600 ? 20 : 24,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF263238),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'View your past interview transcripts and feedback',
                style: TextStyle(
                  fontSize: MediaQuery.of(context).size.width < 600 ? 14 : 16,
                  color: Colors.grey[600],
                ),
              ),
              SizedBox(height: MediaQuery.of(context).size.width < 600 ? 16 : 24),
              
              // Workflow selector
              Container(
                padding: EdgeInsets.all(MediaQuery.of(context).size.width < 600 ? 12 : 16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.grey[200]!),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 10,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.work, size: 20, color: Colors.grey[700]),
                        const SizedBox(width: 8),
                        Text(
                          'Select Position',
                          style: TextStyle(
                            fontSize: MediaQuery.of(context).size.width < 600 ? 14 : 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.grey[800],
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: MediaQuery.of(context).size.width < 600 ? 12 : 16),
                    Align(
                      alignment: Alignment.centerLeft,
                      child: ConstrainedBox(
                        constraints: BoxConstraints(
                          maxWidth: MediaQuery.of(context).size.width < 600 ? double.infinity : 300
                        ),
                        child: PopupMenuButton<Workflow>(
                          onSelected: (workflow) {
                            _selectWorkflow(workflow);
                          },
                          color: Colors.white,
                          elevation: 8,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                            side: BorderSide(color: Colors.grey[300]!),
                          ),
                          itemBuilder: (context) => _workflows.map((workflow) {
                            return PopupMenuItem<Workflow>(
                              value: workflow,
                              child: Text(
                                '${workflow.company} - ${workflow.position}',
                                style: TextStyle(
                                  fontSize: MediaQuery.of(context).size.width < 600 ? 12 : 14, 
                                  color: Colors.grey[800]
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                            );
                          }).toList(),
                          child: Container(
                            height: MediaQuery.of(context).size.width < 600 ? 40 : 48,
                            padding: EdgeInsets.symmetric(
                              horizontal: MediaQuery.of(context).size.width < 600 ? 12 : 16
                            ),
                            decoration: BoxDecoration(
                              border: Border.all(color: Colors.grey[300]!, width: 1.5),
                              borderRadius: BorderRadius.circular(8),
                              color: Colors.white,
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withValues(alpha: 0.05),
                                  blurRadius: 4,
                                  offset: const Offset(0, 2),
                                ),
                              ],
                            ),
                            child: Row(
                              children: [
                                Expanded(
                                  child: Text(
                                    _selectedWorkflow == null
                                        ? 'Select a workflow'
                                        : '${_selectedWorkflow!.company} - ${_selectedWorkflow!.position}',
                                    style: TextStyle(
                                      fontSize: MediaQuery.of(context).size.width < 600 ? 12 : 14,
                                      color: _selectedWorkflow == null ? Colors.grey[500] : Colors.grey[800],
                                    ),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                                Icon(Icons.keyboard_arrow_down, size: 18, color: Colors.grey[700]),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              
              SizedBox(height: MediaQuery.of(context).size.width < 600 ? 16 : 24),
              
              // Interview history list
              _loadingInterviews
                ? const Center(
                    child: Padding(
                      padding: EdgeInsets.all(32.0),
                      child: CircularProgressIndicator(
                        strokeWidth: 3,
                        color: Color(0xFF263238),
                      ),
                    ),
                  )
                : _interviewHistory.isEmpty
                  ? Center(
                      child: Padding(
                        padding: const EdgeInsets.all(32.0),
                        child: Column(
                          children: [
                            Icon(Icons.history, size: 48, color: Colors.grey[400]),
                            const SizedBox(height: 16),
                            Text(
                              'No interviews for this position yet',
                              style: TextStyle(
                                fontSize: MediaQuery.of(context).size.width < 600 ? 14 : 16, 
                                color: Colors.grey[600]
                              ),
                            ),
                          ],
                        ),
                      ),
                    )
                  : Expanded(
                child: ListView.builder(
                  padding: EdgeInsets.zero,
                  itemCount: _interviewHistory.length,
                  itemBuilder: (context, index) {
                    final interview = _interviewHistory[index];
                    return _InterviewHistoryCard(
                      interview: interview,
                            selectedWorkflow: _selectedWorkflow,
                      onViewTranscript: () => _viewTranscript(interview),
                      onViewFeedback: () => _viewFeedback(interview),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTranscriptView() {
    if (_selectedInterview == null) {
      return const Center(child: Text('No interview selected'));
    }

    final transcript = _selectedInterview!['transcript'] as List<dynamic>? ?? [];
    final position = _selectedWorkflow?.position ?? _selectedInterview!['position'] ?? 'Unknown Position';
    final company = _selectedWorkflow?.company ?? _selectedInterview!['company'] ?? 'Unknown Company';
    final duration = _selectedInterview!['duration_minutes'] ?? 0;
    final createAt = _selectedInterview!['createAt'] ?? '';

    return Padding(
      padding: EdgeInsets.symmetric(
        horizontal: MediaQuery.of(context).size.width < 600 ? 16.0 : 64.0, 
        vertical: MediaQuery.of(context).size.width < 600 ? 16.0 : 32.0
      ),
      child: Center(
        child: Container(
          constraints: const BoxConstraints(maxWidth: 1000),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header info
              Container(
                width: double.infinity,
                padding: EdgeInsets.all(MediaQuery.of(context).size.width < 600 ? 16 : 24),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.grey[200]!),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.05),
                      blurRadius: 10,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '$position at $company',
                      style: TextStyle(
                        fontSize: MediaQuery.of(context).size.width < 600 ? 16 : 20,
                        fontWeight: FontWeight.bold,
                        color: const Color(0xFF263238),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Icon(Icons.access_time, size: 16, color: Colors.grey[600]),
                        const SizedBox(width: 4),
                        Text(
                          'Duration: ${duration}m',
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: MediaQuery.of(context).size.width < 600 ? 12 : 14,
                          ),
                        ),
                        const SizedBox(width: 16),
                        Icon(Icons.calendar_today, size: 16, color: Colors.grey[600]),
                        const SizedBox(width: 4),
                        Text(
                          _formatDate(createAt),
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: MediaQuery.of(context).size.width < 600 ? 12 : 14,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              
              SizedBox(height: MediaQuery.of(context).size.width < 600 ? 16 : 24),
              
              // Transcript
              Expanded(
                child: Container(
                  width: double.infinity,
                  padding: EdgeInsets.all(MediaQuery.of(context).size.width < 600 ? 16 : 24),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.grey[200]!),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.05),
                        blurRadius: 10,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.chat, color: Colors.grey[700], size: 20),
                          const SizedBox(width: 8),
                          Text(
                            'Interview Conversation',
                            style: TextStyle(
                              fontSize: MediaQuery.of(context).size.width < 600 ? 16 : 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.grey[800],
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: MediaQuery.of(context).size.width < 600 ? 12 : 16),
                      Expanded(
                        child: transcript.isEmpty
                            ? Center(
                                child: Text(
                                  'No transcript available',
                                  style: TextStyle(
                                    fontSize: MediaQuery.of(context).size.width < 600 ? 14 : 16,
                                    color: Colors.grey[500],
                                  ),
                                ),
                              )
                            : ListView.builder(
                                padding: EdgeInsets.zero,
                                itemCount: transcript.length,
                                itemBuilder: (context, index) {
                                  final message = transcript[index];
                                  final role = message['role'] ?? '';
                                  final content = message['message'] ?? message['content'] ?? '';
                                  final isUser = role == 'user';
                                  
                                  return Container(
                                    margin: EdgeInsets.only(bottom: MediaQuery.of(context).size.width < 600 ? 12 : 16),
                                    child: Row(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Container(
                                          width: MediaQuery.of(context).size.width < 600 ? 28 : 32,
                                          height: MediaQuery.of(context).size.width < 600 ? 28 : 32,
                                          decoration: BoxDecoration(
                                            color: isUser ? const Color(0xFF263238) : const Color(0xFFe6cfe6),
                                            borderRadius: BorderRadius.circular(MediaQuery.of(context).size.width < 600 ? 14 : 16),
                                          ),
                                          child: Icon(
                                            isUser ? Icons.person : Icons.smart_toy,
                                            color: isUser ? Colors.white : const Color(0xFF263238),
                                            size: MediaQuery.of(context).size.width < 600 ? 14 : 16,
                                          ),
                                        ),
                                        SizedBox(width: MediaQuery.of(context).size.width < 600 ? 8 : 12),
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              Text(
                                                isUser ? 'You' : 'AI Interviewer',
                                                style: TextStyle(
                                                  fontSize: MediaQuery.of(context).size.width < 600 ? 10 : 12,
                                                  fontWeight: FontWeight.bold,
                                                  color: Colors.grey[600],
                                                ),
                                              ),
                                              const SizedBox(height: 4),
                                              Text(
                                                content,
                                                style: TextStyle(
                                                  fontSize: MediaQuery.of(context).size.width < 600 ? 12 : 14,
                                                  color: Colors.grey[800],
                                                  height: 1.4,
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),
                                      ],
                                    ),
                                  );
                                },
                              ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFeedbackView() {
    if (_selectedInterview == null) {
      return const Center(child: Text('No interview selected'));
    }

    final feedback = _selectedInterview!['feedback'];
    if (feedback == null) {
      return const Center(child: Text('No feedback available'));
    }

    final position = _selectedWorkflow?.position ?? _selectedInterview!['position'] ?? 'Unknown Position';
    final company = _selectedWorkflow?.company ?? _selectedInterview!['company'] ?? 'Unknown Company';
    final positives = feedback['positives'] as List<dynamic>? ?? [];
    final improvementAreas = feedback['improvementAreas'] as List<dynamic>? ?? [];
    final resources = feedback['resources'] as List<dynamic>? ?? [];
    final reflectionPrompt = feedback['reflectionPrompt'] as List<dynamic>? ?? [];
    final overallRating = feedback['overallRating'] ?? 0;
    final focusTags = feedback['focusTags'] as List<dynamic>? ?? [];

    return Padding(
      padding: EdgeInsets.symmetric(
        horizontal: MediaQuery.of(context).size.width < 600 ? 16.0 : 64.0, 
        vertical: MediaQuery.of(context).size.width < 600 ? 16.0 : 32.0
      ),
      child: Center(
        child: Container(
          constraints: const BoxConstraints(maxWidth: 1000),
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header section
                Container(
                  width: double.infinity,
                  padding: EdgeInsets.all(MediaQuery.of(context).size.width < 600 ? 16 : 24),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        const Color(0xFF263238),
                        const Color(0xFF263238).withValues(alpha: 0.8),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.1),
                        blurRadius: 15,
                        offset: const Offset(0, 6),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(
                            Icons.assessment,
                            size: MediaQuery.of(context).size.width < 600 ? 24 : 32,
                            color: Colors.white,
                          ),
                          const SizedBox(width: 12),
                          Text(
                            'Interview Feedback',
                            style: TextStyle(
                              fontSize: MediaQuery.of(context).size.width < 600 ? 18 : 24,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '$position at $company',
                        style: TextStyle(
                          fontSize: MediaQuery.of(context).size.width < 600 ? 12 : 14,
                          color: Colors.white.withValues(alpha: 0.9),
                        ),
                      ),
                      SizedBox(height: MediaQuery.of(context).size.width < 600 ? 12 : 16),
                      
                      // Rating and tags
                      Row(
                        children: [
                          // Overall Rating
                          Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(
                                'Rating: ',
                                style: TextStyle(
                                  fontSize: MediaQuery.of(context).size.width < 600 ? 12 : 14,
                                  color: Colors.white.withValues(alpha: 0.9),
                                ),
                              ),
                              Row(
                                mainAxisSize: MainAxisSize.min,
                                children: List.generate(5, (index) {
                                  return Icon(
                                    index < overallRating ? Icons.star : Icons.star_border,
                                    color: Colors.amber,
                                    size: MediaQuery.of(context).size.width < 600 ? 16 : 20,
                                  );
                                }),
                              ),
                              const SizedBox(width: 4),
                              Text(
                                '$overallRating/5',
                                style: TextStyle(
                                  fontSize: MediaQuery.of(context).size.width < 600 ? 12 : 14,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                              ),
                            ],
                          ),
                          
                          // Focus Tags
                          if (focusTags.isNotEmpty) ...[
                            const Spacer(),
                            Wrap(
                              alignment: WrapAlignment.end,
                              spacing: 6,
                              runSpacing: 6,
                              children: focusTags.take(3).map((tag) => Container(
                                padding: EdgeInsets.symmetric(
                                  horizontal: MediaQuery.of(context).size.width < 600 ? 6 : 8, 
                                  vertical: MediaQuery.of(context).size.width < 600 ? 2 : 4
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.white.withValues(alpha: 0.2),
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(
                                    color: Colors.white.withValues(alpha: 0.3),
                                    width: 1,
                                  ),
                                ),
                                child: Text(
                                  tag.toString(),
                                  style: TextStyle(
                                    fontSize: MediaQuery.of(context).size.width < 600 ? 9 : 11,
                                    color: Colors.white.withValues(alpha: 0.9),
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              )).toList(),
                            ),
                          ],
                        ],
                      ),
                    ],
                  ),
                ),
                
                SizedBox(height: MediaQuery.of(context).size.width < 600 ? 16 : 24),

                // Positives section
                if (positives.isNotEmpty) ...[
                  _buildFeedbackSection(
                    title: 'What You Did Well',
                    icon: Icons.thumb_up,
                    color: Colors.green,
                    items: positives.cast<String>(),
                  ),
                  SizedBox(height: MediaQuery.of(context).size.width < 600 ? 16 : 24),
                ],

                // Improvement areas section
                if (improvementAreas.isNotEmpty) ...[
                  _buildImprovementSection(improvementAreas),
                  SizedBox(height: MediaQuery.of(context).size.width < 600 ? 16 : 24),
                ],

                // Resources section
                if (resources.isNotEmpty) ...[
                  _buildResourcesSection(resources),
                  SizedBox(height: MediaQuery.of(context).size.width < 600 ? 16 : 24),
                ],

                // Reflection prompts section
                if (reflectionPrompt.isNotEmpty) ...[
                  _buildReflectionSection(reflectionPrompt.cast<String>()),
                  SizedBox(height: MediaQuery.of(context).size.width < 600 ? 24 : 32),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildFeedbackSection({
    required String title,
    required IconData icon,
    required Color color,
    required List<String> items,
  }) {
    return Container(
      width: double.infinity,
      padding: EdgeInsets.all(MediaQuery.of(context).size.width < 600 ? 16 : 24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey[200]!),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: EdgeInsets.all(MediaQuery.of(context).size.width < 600 ? 6 : 8),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, color: color, size: MediaQuery.of(context).size.width < 600 ? 20 : 24),
              ),
              const SizedBox(width: 12),
              Text(
                title,
                style: TextStyle(
                  fontSize: MediaQuery.of(context).size.width < 600 ? 16 : 20,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF263238),
                ),
              ),
            ],
          ),
          SizedBox(height: MediaQuery.of(context).size.width < 600 ? 12 : 16),
          ...items.map((item) => Padding(
            padding: EdgeInsets.only(bottom: MediaQuery.of(context).size.width < 600 ? 8 : 12),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 6,
                  height: 6,
                  margin: EdgeInsets.only(
                    top: MediaQuery.of(context).size.width < 600 ? 6 : 8, 
                    right: MediaQuery.of(context).size.width < 600 ? 8 : 12
                  ),
                  decoration: BoxDecoration(
                    color: color,
                    shape: BoxShape.circle,
                  ),
                ),
                Expanded(
                  child: Text(
                    item,
                    style: TextStyle(
                      fontSize: MediaQuery.of(context).size.width < 600 ? 14 : 16,
                      color: Colors.grey[700],
                      height: 1.5,
                    ),
                  ),
                ),
              ],
            ),
          )),
        ],
      ),
    );
  }

  Widget _buildImprovementSection(List<dynamic> improvementAreas) {
    return Container(
      width: double.infinity,
      padding: EdgeInsets.all(MediaQuery.of(context).size.width < 600 ? 16 : 24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey[200]!),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: EdgeInsets.all(MediaQuery.of(context).size.width < 600 ? 6 : 8),
                decoration: BoxDecoration(
                  color: Colors.orange.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(Icons.trending_up, color: Colors.orange, size: MediaQuery.of(context).size.width < 600 ? 20 : 24),
              ),
              const SizedBox(width: 12),
              Text(
                'Areas for Improvement',
                style: TextStyle(
                  fontSize: MediaQuery.of(context).size.width < 600 ? 16 : 20,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF263238),
                ),
              ),
            ],
          ),
          SizedBox(height: MediaQuery.of(context).size.width < 600 ? 12 : 16),
          ...improvementAreas.map((area) {
            final topic = area['topic'] ?? '';
            final example = area['example'] ?? '';
            final suggestion = area['suggestion'] ?? '';
            
            return Container(
              margin: EdgeInsets.only(bottom: MediaQuery.of(context).size.width < 600 ? 12 : 16),
              padding: EdgeInsets.all(MediaQuery.of(context).size.width < 600 ? 12 : 16),
              decoration: BoxDecoration(
                color: Colors.orange.withValues(alpha: 0.05),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.orange.withValues(alpha: 0.2)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    topic,
                    style: TextStyle(
                      fontSize: MediaQuery.of(context).size.width < 600 ? 14 : 16,
                      fontWeight: FontWeight.bold,
                      color: const Color(0xFF263238),
                    ),
                  ),
                  SizedBox(height: MediaQuery.of(context).size.width < 600 ? 6 : 8),
                  Text(
                    'Example: $example',
                    style: TextStyle(
                      fontSize: MediaQuery.of(context).size.width < 600 ? 12 : 14,
                      color: Colors.grey[700],
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                  SizedBox(height: MediaQuery.of(context).size.width < 600 ? 6 : 8),
                  Text(
                    'Suggestion: $suggestion',
                    style: TextStyle(
                      fontSize: MediaQuery.of(context).size.width < 600 ? 12 : 14,
                      color: Colors.grey[800],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildResourcesSection(List<dynamic> resources) {
    return Container(
      width: double.infinity,
      padding: EdgeInsets.all(MediaQuery.of(context).size.width < 600 ? 16 : 24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey[200]!),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: EdgeInsets.all(MediaQuery.of(context).size.width < 600 ? 6 : 8),
                decoration: BoxDecoration(
                  color: Colors.blue.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(Icons.library_books, color: Colors.blue, size: MediaQuery.of(context).size.width < 600 ? 20 : 24),
              ),
              const SizedBox(width: 12),
              Text(
                'Recommended Resources',
                style: TextStyle(
                  fontSize: MediaQuery.of(context).size.width < 600 ? 16 : 20,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF263238),
                ),
              ),
            ],
          ),
          SizedBox(height: MediaQuery.of(context).size.width < 600 ? 12 : 16),
          ...resources.map((resource) {
            final title = resource['title'] ?? '';
            final link = resource['link'] ?? '';
            
            return Container(
              margin: EdgeInsets.only(bottom: MediaQuery.of(context).size.width < 600 ? 8 : 12),
              child: InkWell(
                onTap: () async {
                  try {
                    final uri = Uri.parse(link);
                    if (await canLaunchUrl(uri)) {
                      await launchUrl(uri, mode: LaunchMode.externalApplication);
                    } else {
                      if (mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Unable to open link: $link')),
                        );
                      }
                    }
                  } catch (e) {
                    if (mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Invalid link format: $link')),
                      );
                    }
                  }
                },
                child: Container(
                  padding: EdgeInsets.all(MediaQuery.of(context).size.width < 600 ? 12 : 16),
                  decoration: BoxDecoration(
                    color: Colors.blue.withValues(alpha: 0.05),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.blue.withValues(alpha: 0.2)),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.link, color: Colors.blue, size: MediaQuery.of(context).size.width < 600 ? 18 : 20),
                      SizedBox(width: MediaQuery.of(context).size.width < 600 ? 8 : 12),
                      Expanded(
                        child: Text(
                          title,
                          style: TextStyle(
                            fontSize: MediaQuery.of(context).size.width < 600 ? 14 : 16,
                            color: Colors.blue,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                      Icon(Icons.arrow_forward_ios, color: Colors.blue, size: MediaQuery.of(context).size.width < 600 ? 14 : 16),
                    ],
                  ),
                ),
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildReflectionSection(List<String> prompts) {
    return Container(
      width: double.infinity,
      padding: EdgeInsets.all(MediaQuery.of(context).size.width < 600 ? 16 : 24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey[200]!),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: EdgeInsets.all(MediaQuery.of(context).size.width < 600 ? 6 : 8),
                decoration: BoxDecoration(
                  color: Colors.purple.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(Icons.psychology, color: Colors.purple, size: MediaQuery.of(context).size.width < 600 ? 20 : 24),
              ),
              const SizedBox(width: 12),
              Text(
                'Reflection Questions',
                style: TextStyle(
                  fontSize: MediaQuery.of(context).size.width < 600 ? 16 : 20,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF263238),
                ),
              ),
            ],
          ),
          SizedBox(height: MediaQuery.of(context).size.width < 600 ? 12 : 16),
          Text(
            'Take some time to reflect on these questions:',
            style: TextStyle(
              fontSize: MediaQuery.of(context).size.width < 600 ? 14 : 16,
              color: Colors.grey[700],
              fontStyle: FontStyle.italic,
            ),
          ),
          SizedBox(height: MediaQuery.of(context).size.width < 600 ? 12 : 16),
          ...prompts.map((prompt) => Padding(
            padding: EdgeInsets.only(bottom: MediaQuery.of(context).size.width < 600 ? 8 : 12),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '• ',
                  style: TextStyle(
                    fontSize: MediaQuery.of(context).size.width < 600 ? 16 : 18,
                    color: Colors.purple,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Expanded(
                  child: Text(
                    prompt,
                    style: TextStyle(
                      fontSize: MediaQuery.of(context).size.width < 600 ? 14 : 16,
                      color: Colors.grey[700],
                      height: 1.5,
                    ),
                  ),
                ),
              ],
            ),
          )),
        ],
      ),
    );
  }

  String _formatDate(String dateString) {
    try {
      final date = DateTime.parse(dateString);
      final now = DateTime.now();
      final difference = now.difference(date);
      
      if (difference.inDays == 0) {
        return 'Today';
      } else if (difference.inDays == 1) {
        return 'Yesterday';
      } else if (difference.inDays < 7) {
        return '${difference.inDays} days ago';
      } else {
        return '${date.month}/${date.day}/${date.year}';
      }
    } catch (e) {
      return dateString;
    }
  }
}

class _InterviewHistoryCard extends StatelessWidget {
  final Map<String, dynamic> interview;
  final Workflow? selectedWorkflow;
  final VoidCallback onViewTranscript;
  final VoidCallback onViewFeedback;

  const _InterviewHistoryCard({
    required this.interview,
    required this.selectedWorkflow,
    required this.onViewTranscript,
    required this.onViewFeedback,
  });

  @override
  Widget build(BuildContext context) {
    final position = selectedWorkflow?.position ?? interview['position'] ?? 'Unknown Position';
    final company = selectedWorkflow?.company ?? interview['company'] ?? 'Unknown Company';
    final duration = interview['duration_minutes'] ?? 0;
    final createAt = interview['createAt'] ?? '';
    final overallRating = interview['feedback']?['overallRating'] ?? 0;

    return Container(
      margin: EdgeInsets.only(bottom: MediaQuery.of(context).size.width < 600 ? 12 : 16),
      padding: EdgeInsets.all(MediaQuery.of(context).size.width < 600 ? 16 : 24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey[200]!),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      position,
                      style: TextStyle(
                        fontSize: MediaQuery.of(context).size.width < 600 ? 16 : 18,
                        fontWeight: FontWeight.bold,
                        color: const Color(0xFF263238),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      company,
                      style: TextStyle(
                        fontSize: MediaQuery.of(context).size.width < 600 ? 14 : 16,
                        color: Colors.grey[600],
                      ),
                    ),
                    SizedBox(height: MediaQuery.of(context).size.width < 600 ? 6 : 8),
                    Row(
                      children: [
                        Icon(Icons.access_time, size: 14, color: Colors.grey[500]),
                        const SizedBox(width: 4),
                        Text(
                          '${duration}m',
                          style: TextStyle(
                            fontSize: MediaQuery.of(context).size.width < 600 ? 10 : 12,
                            color: Colors.grey[500],
                          ),
                        ),
                        const SizedBox(width: 12),
                        Icon(Icons.calendar_today, size: 14, color: Colors.grey[500]),
                        const SizedBox(width: 4),
                        Text(
                          _formatDate(createAt),
                          style: TextStyle(
                            fontSize: MediaQuery.of(context).size.width < 600 ? 10 : 12,
                            color: Colors.grey[500],
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              // Rating
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: List.generate(5, (index) {
                      return Icon(
                        index < overallRating ? Icons.star : Icons.star_border,
                        color: Colors.amber,
                        size: MediaQuery.of(context).size.width < 600 ? 14 : 16,
                      );
                    }),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '$overallRating/5',
                    style: TextStyle(
                      fontSize: MediaQuery.of(context).size.width < 600 ? 10 : 12,
                      color: Colors.grey[600],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ],
          ),
          
          SizedBox(height: MediaQuery.of(context).size.width < 600 ? 12 : 16),
          
          // Action buttons
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: onViewTranscript,
                  icon: Icon(Icons.chat, size: MediaQuery.of(context).size.width < 600 ? 14 : 16),
                  label: Text(
                    'View Transcript',
                    style: TextStyle(
                      fontSize: MediaQuery.of(context).size.width < 600 ? 11 : 12,
                    ),
                  ),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF263238),
                    side: const BorderSide(color: Color(0xFF263238)),
                    padding: EdgeInsets.symmetric(
                      vertical: MediaQuery.of(context).size.width < 600 ? 8 : 12
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                ),
              ),
              SizedBox(width: MediaQuery.of(context).size.width < 600 ? 8 : 12),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: onViewFeedback,
                  icon: Icon(Icons.assessment, size: MediaQuery.of(context).size.width < 600 ? 14 : 16),
                  label: Text(
                    'View Feedback',
                    style: TextStyle(
                      fontSize: MediaQuery.of(context).size.width < 600 ? 11 : 12,
                    ),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF263238),
                    foregroundColor: Colors.white,
                    padding: EdgeInsets.symmetric(
                      vertical: MediaQuery.of(context).size.width < 600 ? 8 : 12
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _formatDate(String dateString) {
    try {
      final date = DateTime.parse(dateString);
      final now = DateTime.now();
      final difference = now.difference(date);
      
      if (difference.inDays == 0) {
        return 'Today';
      } else if (difference.inDays == 1) {
        return 'Yesterday';
      } else if (difference.inDays < 7) {
        return '${difference.inDays} days ago';
      } else {
        return '${date.month}/${date.day}/${date.year}';
      }
    } catch (e) {
      return dateString;
    }
  }
} 