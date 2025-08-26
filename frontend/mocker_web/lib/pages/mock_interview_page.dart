import 'package:flutter/material.dart';
import '../models/workflow.dart';
import '../models/interview.dart';
import '../services/workflow_service.dart';
import '../services/interview_service.dart';
import '../widgets/navbar.dart';
import '../theme/app_theme.dart';
import 'dart:convert';
import 'dart:async';
import 'package:url_launcher/url_launcher.dart';

// interview state enum
enum InterviewState {
  selectWorkflow,    // select workflow
  interviewing,      // interviewing
  showingFeedback    // showing feedback
}

class MockInterviewPage extends StatefulWidget {
  const MockInterviewPage({super.key});

  @override
  State<MockInterviewPage> createState() => _MockInterviewPageState();
}

class _MockInterviewPageState extends State<MockInterviewPage> {
  final WorkflowService _workflowService = WorkflowService();
  final InterviewService _interviewService = InterviewService();
  
  // Interview state management
  InterviewState _currentState = InterviewState.selectWorkflow;
  
  // Workflow selection state
  Workflow? _selectedWorkflow;
  List<Workflow> _availableWorkflows = [];
  bool _loadingWorkflows = true;
  String? _workflowsError;
  
  // Interview duration selection
  int _selectedDuration = 15; // default 15 minutes
  final List<int> _durationOptions = [5, 10, 15, 20, 30, 45, 60];
  
  // Interview state
  List<ChatMessage> _messages = [];
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  bool _sending = false;
  bool _loadingChat = false;
  String? _sessionId;
  bool _wsConnected = false;
  bool _interviewActuallyStarted = false; // Flag to track if interview actually started

  // Real-time timer state
  DateTime? _interviewStartTime;
  Timer? _interviewTimer;
  Duration _elapsedTime = Duration.zero;
  
  // Feedback state
  Map<String, dynamic>? _feedbackData;
  bool _loadingFeedback = false;
  String? _feedbackError;
  bool _feedbackRequested = false;
  
  // Polling state
  Timer? _feedbackPollingTimer;
  int _pollingAttempts = 0;
  static const int _maxPollingAttempts = 30; 
  static const Duration _pollingInterval = Duration(seconds: 2);

  @override
  void initState() {
    super.initState();
    _loadAvailableWorkflows();
  }

  Future<void> _loadAvailableWorkflows() async {
    try {
      setState(() {
        _loadingWorkflows = true;
        _workflowsError = null;
      });
      
      // get all workflows, then filter out the ones that are not prepared (have personalExperience)
      final allWorkflows = await _workflowService.getWorkflows();
      final availableWorkflows = allWorkflows
          .where((workflow) => workflow.personalExperience != null)
          .toList();
      
      setState(() {
        _availableWorkflows = availableWorkflows;
        _loadingWorkflows = false;
      });
    } catch (e) {
      setState(() {
        _workflowsError = e.toString();
        _loadingWorkflows = false;
      });
    }
  }

  Future<void> _selectWorkflow(Workflow workflow) async {
    setState(() {
      _selectedWorkflow = workflow;
      _currentState = InterviewState.interviewing;
      _loadingChat = true;
    });

    try {
      // 1. first call /interviews/start API
      final sessionData = await _interviewService.startInterviewSession(
        workflow.id,
        _selectedDuration, // use user selected duration
        false, // is_audio
      );

      // 2. get connection information from API response
      final sessionId = sessionData['session_id'];
      final websocketParameter = sessionData['websocket_parameter'];

      // 3. set WebSocket listener
      _interviewService.setWebSocketListeners(
        onMessageReceived: (message) {
          setState(() {
            _messages.add(message);
            // Mark interview as actually started when first message is received
            if (!_interviewActuallyStarted) {
              _interviewActuallyStarted = true;
            }
          });
          WidgetsBinding.instance.addPostFrameCallback((_) => _scrollToBottom());
        },
        onDisconnected: () async {
          setState(() => _wsConnected = false);
          _stopInterviewTimer(); // stop timer when disconnected
          // Only trigger feedback flow if interview actually started and not already requested
          if (_feedbackRequested || !_interviewActuallyStarted) return;
          _feedbackRequested = true;
          if (_sessionId != null && _selectedWorkflow != null) {
            setState(() => _loadingFeedback = true);
            _startFeedbackPolling();
          }
        },
        onError: (error) {
          setState(() => _wsConnected = false);
          _stopInterviewTimer(); // stop timer on error
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('WebSocket error: $error')),
          );
        },
      );

      // 4. connect WebSocket
      await _interviewService.connectWebSocket(sessionId, websocketParameter);
      
      setState(() {
        _sessionId = sessionId;
        _wsConnected = _interviewService.isWebSocketConnected;
        _messages.clear();
        _loadingChat = false;
      });

      // 5. Start the interview timer
      _startInterviewTimer();

    } catch (e) {
      setState(() {
        _loadingChat = false;
        _wsConnected = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to start interview: $e')),
      );
    }
  }

  void _goBackToWorkflowSelection() {
    setState(() {
      _currentState = InterviewState.selectWorkflow;
      _selectedWorkflow = null;
      _messages.clear();
      _wsConnected = false;
      _feedbackData = null;
      _feedbackError = null;
      _feedbackRequested = false;
      _pollingAttempts = 0;
      _elapsedTime = Duration.zero;
      _interviewStartTime = null;
      _interviewActuallyStarted = false; // Reset the interview started flag
    });
    _feedbackPollingTimer?.cancel();
    _stopInterviewTimer();
    _interviewService.disconnectWebSocket();
  }

  // end interview method
  Future<void> _endInterview() async {
    if (_sessionId == null) return;

    _stopInterviewTimer(); // stop timer when ending interview

    setState(() {
      _loadingFeedback = true;
      _feedbackError = null;
    });

    try {
      // 1. send end signal through WebSocket 
      if (_wsConnected) {
        _interviewService.sendMessage(json.encode({
          'type': 'control',
          'action': 'end_interview',
          'reason': 'user_stopped'
        }));
      }

      // 2. disconnect WebSocket
      _interviewService.disconnectWebSocket();
    } catch (e) {
      setState(() {
        _feedbackError = e.toString();
        _loadingFeedback = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to end interview: $e')),
      );
    }
  }

  Future<void> _sendMessage() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _selectedWorkflow == null || !_interviewService.isWebSocketConnected) return;
    
    final userMessage = ChatMessage(
      id: 'temp_${DateTime.now().millisecondsSinceEpoch}',
      role: 'user',
      content: text,
      timestamp: DateTime.now(),
    );
    
    setState(() {
      _messages.add(userMessage);
      _controller.clear();
      _sending = true;
    });
    
    WidgetsBinding.instance.addPostFrameCallback((_) => _scrollToBottom());
    
    try {
      // send to WebSocket
      _interviewService.sendMessage(text);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to send message: $e')),
      );
    } finally {
      setState(() => _sending = false);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _feedbackPollingTimer?.cancel();
    _stopInterviewTimer();
    _interviewService.disconnectWebSocket();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // NavBar
        NavBar(
          title: 'Mock Interview',
          actions: _buildNavBarActions(),
        ),
        
        // Main content
        Expanded(
          child: _buildCurrentPage(),
        ),
      ],
    );
  }

  // build NavBar actions
  List<Widget>? _buildNavBarActions() {
    switch (_currentState) {
      case InterviewState.interviewing:
        return [
          // STOP Interview button - responsive size
          Container(
            margin: const EdgeInsets.only(right: 0),  
            height: MediaQuery.of(context).size.width < 600 ? 28 : null,  
            child: ElevatedButton.icon(
              onPressed: _loadingFeedback ? null : _endInterview,
              icon: _loadingFeedback 
                ? SizedBox(
                    width: MediaQuery.of(context).size.width < 600 ? 14 : 16,
                    height: MediaQuery.of(context).size.width < 600 ? 14 : 16,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  )
                : Icon(Icons.stop, size: MediaQuery.of(context).size.width < 600 ? 16 : 18),
              label: Text(
                _loadingFeedback ? 'Ending...' : 'STOP Interview',
                style: TextStyle(
                  fontSize: MediaQuery.of(context).size.width < 600 ? 12 : 14,
                ),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red[600],
                foregroundColor: Colors.white,
                padding: EdgeInsets.symmetric(
                  horizontal: MediaQuery.of(context).size.width < 600 ? 10 : 16, 
                  vertical: MediaQuery.of(context).size.width < 600 ? 0 : 12
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
            ),
          ),
          // Back button - only show on desktop
          if (MediaQuery.of(context).size.width >= 600)
            TextButton.icon(
              onPressed: _loadingFeedback ? null : _goBackToWorkflowSelection,
              icon: const Icon(Icons.arrow_back, size: 18),
              label: const Text('Back to Selection'),
              style: TextButton.styleFrom(
                foregroundColor: AppTheme.darkGray,
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              ),
            ),
        ];
      case InterviewState.showingFeedback:
        return [
          TextButton.icon(
            onPressed: _goBackToWorkflowSelection,
            icon: const Icon(Icons.refresh, size: 18),
            label: const Text('New Interview'),
            style: TextButton.styleFrom(
              foregroundColor: AppTheme.darkGray,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            ),
          ),
        ];
      default:
        return null;
    }
  }

  // build the page according to the current state
  Widget _buildCurrentPage() {
    switch (_currentState) {
      case InterviewState.selectWorkflow:
        return _buildWorkflowSelectionPage();
      case InterviewState.interviewing:
        return _buildChatPage();
      case InterviewState.showingFeedback:
        return _buildFeedbackPage();
    }
  }

  Widget _buildWorkflowSelectionPage() {
    return Padding(
      padding: EdgeInsets.symmetric(
        horizontal: MediaQuery.of(context).size.width < 600 ? 16.0 : 48.0, 
        vertical: 32.0
      ),
      child: Container(
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width < 600 ? double.infinity : 1100
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Select a Position for Mock Interview',
              style: TextStyle(
                fontSize: MediaQuery.of(context).size.width < 600 ? 20 : 25,
                fontWeight: FontWeight.bold,
                color: const Color(0xFF263238),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Choose one of your prepared workflows to start the mock interview',
              style: TextStyle(
                fontSize: MediaQuery.of(context).size.width < 600 ? 14 : 16,
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 32),
            
            // Interview Duration Selection - Responsive
            Container(
              width: double.infinity,
              padding: EdgeInsets.all(MediaQuery.of(context).size.width < 600 ? 20 : 24),
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
              child: MediaQuery.of(context).size.width < 600
                  ? Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(
                              Icons.timer,
                              color: const Color(0xFF263238),
                              size: 24,
                            ),
                            const SizedBox(width: 12),
                            const Text(
                              'Interview Duration',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.w600,
                                color: Color(0xFF263238),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          decoration: BoxDecoration(
                            color: Colors.grey[50],
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: Colors.grey[300]!),
                          ),
                          child: DropdownButton<int>(
                            value: _selectedDuration,
                            underline: const SizedBox(),
                            icon: const Icon(Icons.keyboard_arrow_down, color: Color(0xFF263238)),
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w500,
                              color: Color(0xFF263238),
                            ),
                            items: _durationOptions.map((duration) {
                              return DropdownMenuItem<int>(
                                value: duration,
                                child: Text('${duration} minutes'),
                              );
                            }).toList(),
                            onChanged: (value) {
                              if (value != null) {
                                setState(() {
                                  _selectedDuration = value;
                                });
                              }
                            },
                          ),
                        ),
                      ],
                    )
                  : Row(
                      children: [
                        Icon(
                          Icons.timer,
                          color: const Color(0xFF263238),
                          size: 24,
                        ),
                        const SizedBox(width: 12),
                        const Text(
                          'Interview Duration',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF263238),
                          ),
                        ),
                        const Spacer(),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          decoration: BoxDecoration(
                            color: Colors.grey[50],
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: Colors.grey[300]!),
                          ),
                          child: DropdownButton<int>(
                            value: _selectedDuration,
                            underline: const SizedBox(),
                            icon: const Icon(Icons.keyboard_arrow_down, color: Color(0xFF263238)),
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w500,
                              color: Color(0xFF263238),
                            ),
                            items: _durationOptions.map((duration) {
                              return DropdownMenuItem<int>(
                                value: duration,
                                child: Text('${duration} minutes'),
                              );
                            }).toList(),
                            onChanged: (value) {
                              if (value != null) {
                                setState(() {
                                  _selectedDuration = value;
                                });
                              }
                            },
                          ),
                        ),
                      ],
                    ),
            ),
            
            const SizedBox(height: 32),
            
            Expanded(
              child: _loadingWorkflows
                  ? const Center(
                      child: SizedBox(
                        width: 32,
                        height: 32,
                        child: CircularProgressIndicator(
                          strokeWidth: 3,
                          color: Color(0xFF263238),
                        ),
                      ),
                    )
                  : _availableWorkflows.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.work_off, size: 64, color: Colors.grey[400]),
                              const SizedBox(height: 16),
                              Text(
                                _workflowsError ?? 'No workflows available',
                                style: TextStyle(fontSize: 18, color: Colors.grey[600]),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                'Please complete workflow preparation in the Prepare section first',
                                style: TextStyle(fontSize: 14, color: Colors.grey[500]),
                              ),
                            ],
                          ),
                        )
                      : GridView.builder(
                          padding: EdgeInsets.zero,
                          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: MediaQuery.of(context).size.width < 600 ? 1 : 3,
                            mainAxisSpacing: 20,
                            crossAxisSpacing: 20,
                            childAspectRatio: MediaQuery.of(context).size.width < 600 ? 2.5 : 1.3,
                          ),
                          itemCount: _availableWorkflows.length,
                          itemBuilder: (context, index) {
                            final workflow = _availableWorkflows[index];
                            return _WorkflowCard(
                              workflow: workflow,
                              onTap: () => _selectWorkflow(workflow),
                            );
                          },
                        ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChatPage() {
    return Padding(
      padding: EdgeInsets.symmetric(
        horizontal: MediaQuery.of(context).size.width < 600 ? 16.0 : 64.0, 
        vertical: 32.0
      ),
      child: Center(
        child: Container(
          constraints: BoxConstraints(
            maxWidth: MediaQuery.of(context).size.width < 600 ? double.infinity : 1000
          ),
          child: Column(
            children: [
              // Top info bar - redesigned
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(24),
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
                                child: MediaQuery.of(context).size.width < 600
                    ? Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: const Color(0xFFe6cfe6).withOpacity(0.3),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: const Icon(
                                  Icons.record_voice_over,
                                  color: Color(0xFF263238),
                                  size: 24,
                                ),
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      _selectedWorkflow?.position ?? '',
                                      style: const TextStyle(
                                        fontSize: 18,
                                        fontWeight: FontWeight.bold,
                                        color: Color(0xFF263238),
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      'Company: ${_selectedWorkflow?.company}',
                                      style: TextStyle(
                                        fontSize: 13,
                                        color: Colors.grey[600],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              // Back button for mobile
                              TextButton.icon(
                                onPressed: _loadingFeedback ? null : _goBackToWorkflowSelection,
                                icon: const Icon(Icons.arrow_back, size: 16),
                                label: const Text('Back'),
                                style: TextButton.styleFrom(
                                  foregroundColor: AppTheme.darkGray,
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                ),
                              ),
                            ],
                          ),
                          if (_interviewStartTime != null) ...[
                            const SizedBox(height: 16),
                            Container(
                              width: double.infinity,
                              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                              decoration: BoxDecoration(
                                color: Colors.grey[50],
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(color: Colors.grey[200]!),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Icon(
                                        Icons.access_time,
                                        size: 16,
                                        color: Colors.grey[600],
                                      ),
                                      const SizedBox(width: 6),
                                      Text(
                                        'Elapsed time: ${_formatDuration(_elapsedTime)}',
                                        style: TextStyle(
                                          fontSize: 14,
                                          fontWeight: FontWeight.w600,
                                          color: const Color(0xFF263238),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    _formatRemainingTime(),
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: _elapsedTime.inMinutes >= _selectedDuration 
                                          ? Colors.red[600]
                                          : Colors.grey[600],
                                      fontWeight: _elapsedTime.inMinutes >= _selectedDuration 
                                          ? FontWeight.w600
                                          : FontWeight.normal,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ],
                      )
                    : Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: const Color(0xFFe6cfe6).withOpacity(0.3),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Icon(
                              Icons.record_voice_over,
                              color: Color(0xFF263238),
                              size: 24,
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Mock Interview: ${_selectedWorkflow?.position}',
                                  style: const TextStyle(
                                    fontSize: 20,
                                    fontWeight: FontWeight.bold,
                                    color: Color(0xFF263238),
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  'Company: ${_selectedWorkflow?.company}',
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.grey[600],
                                  ),
                                ),
                              ],
                            ),
                          ),
                          // Timer display section
                          if (_interviewStartTime != null) Container(
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                            decoration: BoxDecoration(
                              color: Colors.grey[50],
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(color: Colors.grey[200]!),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.end,
                              children: [
                                Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(
                                      Icons.access_time,
                                      size: 16,
                                      color: Colors.grey[600],
                                    ),
                                    const SizedBox(width: 6),
                                    Text(
                                      'Elapsed time: ${_formatDuration(_elapsedTime)}',
                                      style: TextStyle(
                                        fontSize: 14,
                                        fontWeight: FontWeight.w600,
                                        color: const Color(0xFF263238),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  _formatRemainingTime(),
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: _elapsedTime.inMinutes >= _selectedDuration 
                                        ? Colors.red[600]
                                        : Colors.red[600],
                                    fontWeight: _elapsedTime.inMinutes >= _selectedDuration 
                                        ? FontWeight.w600
                                        : FontWeight.normal,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
              ),
              const SizedBox(height: 24),
              
              // Chat area - redesigned
              Expanded(
                child: Container(
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
                    children: [
                      // Chat messages area
                      Expanded(
                        child: _loadingChat
                            ? Center(
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    const SizedBox(
                                      width: 32,
                                      height: 32,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 3,
                                        color: Color(0xFF263238),
                                      ),
                                    ),
                                    const SizedBox(height: 16),
                                    Text(
                                      'Starting interview session...',
                                      style: TextStyle(
                                        fontSize: 16,
                                        color: Colors.grey[600],
                                      ),
                                    ),
                                  ],
                                ),
                              )
                            : _messages.isEmpty
                                ? Center(
                                    child: Text(
                                      'Interview will start once connected',
                                      style: TextStyle(
                                        fontSize: 16,
                                        color: Colors.grey[500],
                                      ),
                                    ),
                                  )
                                : ListView.builder(
                                    controller: _scrollController,
                                    padding: const EdgeInsets.all(20),
                                    itemCount: _messages.length,
                                    itemBuilder: (context, idx) {
                                      final msg = _messages[idx];
                                      final isUser = msg.role == 'user';
                                      return Align(
                                        alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                                        child: Container(
                                          constraints: BoxConstraints(
                                            maxWidth: MediaQuery.of(context).size.width * 0.7,
                                          ),
                                          margin: const EdgeInsets.symmetric(vertical: 8),
                                          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                                          decoration: BoxDecoration(
                                            color: isUser ? AppTheme.primaryBlue : AppTheme.surfaceWhite,
                                            border: isUser ? null : Border.all(color: AppTheme.borderGray),
                                            borderRadius: BorderRadius.only(
                                              topLeft: const Radius.circular(18),
                                              topRight: const Radius.circular(18),
                                              bottomLeft: Radius.circular(isUser ? 18 : 6),
                                              bottomRight: Radius.circular(isUser ? 6 : 18),
                                            ),
                                            boxShadow: [
                                              BoxShadow(
                                                color: Colors.black.withValues(alpha: 0.06),
                                                blurRadius: 6,
                                                offset: const Offset(0, 2),
                                              ),
                                            ],
                                          ),
                                          child: Text(
                                            msg.content,
                                            style: TextStyle(
                                              color: isUser ? Colors.white : AppTheme.darkGray,
                                              fontSize: 15,
                                              height: 1.4,
                                            ),
                                          ),
                                        ),
                                      );
                                    },
                                  ),
                      ),
                      
                      // Input area
                      Container(
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          border: Border(
                            top: BorderSide(color: AppTheme.borderGray),
                          ),
                        ),
                        child: Row(
                          children: [
                            Expanded(
                              child: Container(
                                decoration: BoxDecoration(
                                  color: AppTheme.surfaceWhite,
                                  borderRadius: BorderRadius.circular(24),
                                  border: Border.all(color: AppTheme.borderGray),
                                ),
                                child: TextField(
                                  controller: _controller,
                                  minLines: 1,
                                  maxLines: 4,
                                  style: TextStyle(
                                    fontSize: 15,
                                    color: AppTheme.darkGray,
                                  ),
                                  decoration: const InputDecoration(
                                    hintText: 'Type your answer...',
                                    hintStyle: TextStyle(color: Colors.grey),
                                    border: InputBorder.none,
                                    contentPadding: EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                                  ),
                                  onSubmitted: (_) => _sendMessage(),
                                ),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Container(
                              decoration: BoxDecoration(
                                color: AppTheme.primaryBlue,
                                borderRadius: BorderRadius.circular(24),
                                boxShadow: [
                                  BoxShadow(
                                    color: AppTheme.primaryBlue.withValues(alpha: 0.3),
                                    blurRadius: 6,
                                    offset: const Offset(0, 2),
                                  ),
                                ],
                              ),
                              child: IconButton(
                                onPressed: _sending ? null : _sendMessage,
                                icon: _sending
                                    ? const SizedBox(
                                        width: 16,
                                        height: 16,
                                        child: CircularProgressIndicator(
                                          strokeWidth: 2,
                                          color: Colors.white,
                                        ),
                                      )
                                    : const Icon(
                                        Icons.send,
                                        color: Colors.white,
                                        size: 20,
                                      ),
                                padding: const EdgeInsets.all(12),
                              ),
                            ),
                          ],
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

  Widget _buildFeedbackPage() {
    if (_loadingFeedback) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const SizedBox(
              width: 48,
              height: 48,
              child: CircularProgressIndicator(
                strokeWidth: 4,
                color: Color(0xFF263238),
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'Generating your interview feedback...',
              style: TextStyle(
                fontSize: 18,
                color: Color(0xFF263238),
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'AI is analyzing your interview performance',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[600],
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Text(
              'Checking for feedback... (${_pollingAttempts}/${_maxPollingAttempts})',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[500],
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ),
      );
    }

    if (_feedbackError != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: Colors.red[300]),
            const SizedBox(height: 16),
            Text(
              'Failed to load feedback',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.red[700],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              _feedbackError!,
              style: const TextStyle(color: Colors.red),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _endInterview,
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

    if (_feedbackData == null) {
      return const Center(child: Text('No feedback available'));
    }

    final feedbackContent = _feedbackData!['data'];
    if (feedbackContent == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const SizedBox(
              width: 48,
              height: 48,
              child: CircularProgressIndicator(
                strokeWidth: 4,
                color: Color(0xFF263238),
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'Generating your interview feedback...',
              style: TextStyle(
                fontSize: 18,
                color: Color(0xFF263238),
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'AI is analyzing your interview performance',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[600],
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Text(
              'Checking for feedback... (${_pollingAttempts}/${_maxPollingAttempts})',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[500],
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ),
      );
    }

    final positives = feedbackContent['positives'] as List<dynamic>? ?? [];
    final improvementAreas = feedbackContent['improvementAreas'] as List<dynamic>? ?? [];
    final resources = feedbackContent['resources'] as List<dynamic>? ?? [];
    final reflectionPrompt = feedbackContent['reflectionPrompt'] as List<dynamic>? ?? [];
    final overallRating = feedbackContent['overallRating'] ?? 0;
    final focusTags = feedbackContent['focusTags'] as List<dynamic>? ?? [];

    return Padding(
      padding: EdgeInsets.symmetric(
        horizontal: MediaQuery.of(context).size.width < 600 ? 16.0 : 64.0, 
        vertical: 32.0
      ),
      child: Center(
        child: Container(
          constraints: BoxConstraints(
            maxWidth: MediaQuery.of(context).size.width < 600 ? double.infinity : 1000
          ),
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(24), 
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        const Color(0xFF263238),
                        const Color(0xFF263238).withOpacity(0.8),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(16), 
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.1),
                        blurRadius: 15, 
                        offset: const Offset(0, 6), 
                      ),
                    ],
                  ),
                  child: Row( 
                    children: [
                      Expanded(
                        flex: 2,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(
                                  Icons.assessment,
                                  size: 32, 
                                  color: Colors.white,
                                ),
                                const SizedBox(width: 12),
                                const Text(
                                  'Interview Feedback',
                                  style: TextStyle(
                                    fontSize: 24, 
                                    fontWeight: FontWeight.bold,
                                    color: Colors.white,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text(
                              '${_selectedWorkflow?.position} at ${_selectedWorkflow?.company}',
                              style: TextStyle(
                                fontSize: 14, 
                                color: Colors.white.withOpacity(0.9),
                              ),
                            ),
                          ],
                        ),
                      ),
                      
                      Expanded(
                        flex: 1,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            // Overall Rating
                            Row(
                              mainAxisAlignment: MainAxisAlignment.end,
                              children: [
                                Text(
                                  'Rating: ',
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.white.withOpacity(0.9),
                                  ),
                                ),
                                Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: List.generate(5, (index) {
                                    return Icon(
                                      index < overallRating ? Icons.star : Icons.star_border,
                                      color: Colors.amber,
                                      size: 20, 
                                    );
                                  }),
                                ),
                                const SizedBox(width: 4),
                                Text(
                                  '$overallRating/5',
                                  style: const TextStyle(
                                    fontSize: 14,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.white,
                                  ),
                                ),
                              ],
                            ),
                            
                            // Focus Tags
                            if (focusTags.isNotEmpty) ...[
                              const SizedBox(height: 12),
                              Wrap(
                                alignment: WrapAlignment.end,
                                spacing: 6,
                                runSpacing: 6,
                                children: focusTags.take(3).map((tag) => Container( 
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: Colors.white.withOpacity(0.2),
                                    borderRadius: BorderRadius.circular(12),
                                    border: Border.all(
                                      color: Colors.white.withOpacity(0.3),
                                      width: 1,
                                    ),
                                  ),
                                  child: Text(
                                    tag.toString(),
                                    style: TextStyle(
                                      fontSize: 11,
                                      color: Colors.white.withOpacity(0.9),
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                )).toList(),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 24), 

                // Positives section
                if (positives.isNotEmpty) ...[
                  _buildFeedbackSection(
                    title: 'What You Did Well',
                    icon: Icons.thumb_up,
                    color: Colors.green,
                    items: positives.cast<String>(),
                  ),
                  const SizedBox(height: 24),
                ],

                // Improvement areas section
                if (improvementAreas.isNotEmpty) ...[
                  _buildImprovementSection(improvementAreas),
                  const SizedBox(height: 24),
                ],

                // Resources section
                if (resources.isNotEmpty) ...[
                  _buildResourcesSection(resources),
                  const SizedBox(height: 24),
                ],

                // Reflection prompts section
                if (reflectionPrompt.isNotEmpty) ...[
                  _buildReflectionSection(reflectionPrompt.cast<String>()),
                  const SizedBox(height: 32),
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
      padding: const EdgeInsets.all(24),
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
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, color: color, size: 24),
              ),
              const SizedBox(width: 12),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF263238),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ...items.map((item) => Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 6,
                  height: 6,
                  margin: const EdgeInsets.only(top: 8, right: 12),
                  decoration: BoxDecoration(
                    color: color,
                    shape: BoxShape.circle,
                  ),
                ),
                Expanded(
                  child: Text(
                    item,
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey[700],
                      height: 1.5,
                    ),
                  ),
                ),
              ],
            ),
          )).toList(),
        ],
      ),
    );
  }

  Widget _buildImprovementSection(List<dynamic> improvementAreas) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
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
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.orange.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.trending_up, color: Colors.orange, size: 24),
              ),
              const SizedBox(width: 12),
              const Text(
                'Areas for Improvement',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF263238),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ...improvementAreas.map((area) {
            final topic = area['topic'] ?? '';
            final example = area['example'] ?? '';
            final suggestion = area['suggestion'] ?? '';
            
            return Container(
              margin: const EdgeInsets.only(bottom: 16),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.orange.withOpacity(0.05),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.orange.withOpacity(0.2)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    topic,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF263238),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Example: $example',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[700],
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Suggestion: $suggestion',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[800],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
        ],
      ),
    );
  }

  Widget _buildResourcesSection(List<dynamic> resources) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
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
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.blue.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.library_books, color: Colors.blue, size: 24),
              ),
              const SizedBox(width: 12),
              const Text(
                'Recommended Resources',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF263238),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ...resources.map((resource) {
            final title = resource['title'] ?? '';
            final link = resource['link'] ?? '';
            
            return Container(
              margin: const EdgeInsets.only(bottom: 12),
              child: InkWell(
                onTap: () async {
                  try {
                    final uri = Uri.parse(link);
                    if (await canLaunchUrl(uri)) {
                      await launchUrl(uri, mode: LaunchMode.externalApplication);
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('cannot open link: $link')),
                      );
                    }
                  } catch (e) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('link format error: $link')),
                    );
                  }
                },
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.blue.withOpacity(0.05),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.blue.withOpacity(0.2)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.link, color: Colors.blue, size: 20),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          title,
                          style: const TextStyle(
                            fontSize: 16,
                            color: Colors.blue,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                      const Icon(Icons.arrow_forward_ios, color: Colors.blue, size: 16),
                    ],
                  ),
                ),
              ),
            );
          }).toList(),
        ],
      ),
    );
  }

  Widget _buildReflectionSection(List<String> prompts) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
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
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.purple.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.psychology, color: Colors.purple, size: 24),
              ),
              const SizedBox(width: 12),
              const Text(
                'Reflection Questions',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF263238),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            'Take some time to reflect on these questions:',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey[700],
              fontStyle: FontStyle.italic,
            ),
          ),
          const SizedBox(height: 16),
          ...prompts.map((prompt) => Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '• ',
                  style: TextStyle(
                    fontSize: 18,
                    color: Colors.purple,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Expanded(
                  child: Text(
                    prompt,
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey[700],
                      height: 1.5,
                    ),
                  ),
                ),
              ],
            ),
          )).toList(),
        ],
      ),
    );
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      Future.delayed(const Duration(milliseconds: 100), () {
        if (_scrollController.hasClients) {
          _scrollController.animateTo(
            _scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOut,
          );
        }
      });
    }
  }

  void _startFeedbackPolling() {
    _pollingAttempts = 0;
    _feedbackPollingTimer = Timer.periodic(
      _pollingInterval,
      (Timer timer) async {
        _pollingAttempts++;
        
        try {
          final feedbackResponse = await _interviewService.getInterviewFeedback(_selectedWorkflow!.id, _sessionId!);
          final feedbackContent = feedbackResponse['data'];
          
          if (feedbackContent != null) {
            // get valid feedback, stop polling
            timer.cancel();
            setState(() {
              _feedbackData = feedbackResponse;
              _currentState = InterviewState.showingFeedback;
              _loadingFeedback = false;
            });
          } else if (_pollingAttempts >= _maxPollingAttempts) {
            // reach max attempts, stop polling and show error
            timer.cancel();
            setState(() {
              _feedbackError = 'Feedback generation timed out after ${_maxPollingAttempts * 2} seconds';
              _loadingFeedback = false;
            });
          }
          // if feedbackContent is null and not reached max attempts, continue polling
        } catch (e) {
          if (_pollingAttempts >= _maxPollingAttempts) {
            timer.cancel();
            setState(() {
              _feedbackError = e.toString();
              _loadingFeedback = false;
            });
          }
        }
      },
    );
  }

  void _startInterviewTimer() {
    _interviewStartTime = DateTime.now();
    _interviewTimer = Timer.periodic(
      const Duration(seconds: 1),
      (Timer timer) {
        final currentTime = DateTime.now();
        final elapsedTime = currentTime.difference(_interviewStartTime!);
        setState(() => _elapsedTime = elapsedTime);
      },
    );
  }

  void _stopInterviewTimer() {
    _interviewTimer?.cancel();
  }

  // Format duration to MM:SS format
  String _formatDuration(Duration duration) {
    final minutes = duration.inMinutes.remainder(60);
    final seconds = duration.inSeconds.remainder(60);
    return '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
  }

  // Format remaining time
  String _formatRemainingTime() {
    final totalDuration = Duration(minutes: _selectedDuration);
    final remaining = totalDuration - _elapsedTime;
    if (remaining.isNegative) {
      return 'Time out: ${_formatDuration(_elapsedTime - totalDuration)}';
    }
    return 'Remaining time: ${_formatDuration(remaining)}';
  }
}

class _WorkflowCard extends StatelessWidget {
  final Workflow workflow;
  final VoidCallback onTap;

  const _WorkflowCard({required this.workflow, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 6,
      shadowColor: Colors.black.withValues(alpha: 0.1),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppTheme.borderGray, width: 1.5),
        ),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(16),
                      child: Padding(
              padding: EdgeInsets.all(MediaQuery.of(context).size.width < 600 ? 16 : 20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          workflow.position,
                          style: TextStyle(
                            fontSize: MediaQuery.of(context).size.width < 600 ? 16 : 18,
                            fontWeight: FontWeight.bold,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      Icon(
                        Icons.arrow_forward_ios,
                        size: MediaQuery.of(context).size.width < 600 ? 14 : 16,
                        color: const Color(0xFF263238),
                      ),
                    ],
                  ),
                  SizedBox(height: MediaQuery.of(context).size.width < 600 ? 6 : 8),
                  Text(
                    workflow.company,
                    style: TextStyle(
                      fontSize: MediaQuery.of(context).size.width < 600 ? 14 : 16,
                      color: const Color(0xFF263238),
                    ),
                  ),
                  SizedBox(height: MediaQuery.of(context).size.width < 600 ? 10 : 12),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: AppTheme.lightBlue,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      'Start Interview',
                      style: TextStyle(
                        fontSize: MediaQuery.of(context).size.width < 600 ? 11 : 12,
                        fontWeight: FontWeight.w500,
                        color: AppTheme.primaryBlue,
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
} 