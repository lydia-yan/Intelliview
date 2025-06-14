import '../models/interview.dart';
import '../data/mock_data.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../config/api_config.dart';
import 'package:http_parser/http_parser.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as ws_status;
import 'package:firebase_auth/firebase_auth.dart' as firebase_auth;

class InterviewService {
  static final InterviewService _instance = InterviewService._internal();
  factory InterviewService() => _instance;
  InterviewService._internal();

  WebSocketChannel? _channel;
  bool _wsConnected = false;
  Function(ChatMessage)? _onMessageReceived;
  Function()? _onDisconnected;
  Function(String)? _onError;

  // Store current streaming message part
  String _currentStreamingMessage = '';
  String _currentMessageId = '';

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

  // Submit interview preparation materials
  Future<InterviewPrepareResponse> submitInterviewPreparation(
    InterviewPrepareRequest request, String idToken) async {
    try {
      final multipart = http.MultipartRequest(
        'POST',
        Uri.parse('${ApiConfig.baseUrl}/workflows/start-with-pdf'),
      );
      multipart.headers['Authorization'] = 'Bearer $idToken';
      multipart.fields['job_description'] = request.jobDescription;
      if (request.linkedinLink != null) multipart.fields['linkedin_link'] = request.linkedinLink!;
      if (request.githubLink != null) multipart.fields['github_link'] = request.githubLink!;
      if (request.portfolioLink != null) multipart.fields['portfolio_link'] = request.portfolioLink!;
      if (request.additionalInfo != null) multipart.fields['additional_info'] = request.additionalInfo!;
      if (request.numQuestions != null) multipart.fields['num_questions'] = request.numQuestions.toString();
      if (request.sessionId != null) multipart.fields['session_id'] = request.sessionId!;
      
      // use bytes property
      if (request.resumeFile.bytes != null) {
        multipart.files.add(http.MultipartFile.fromBytes(
          'file',
          request.resumeFile.bytes!,
          filename: request.resumeFile.name,
          contentType: MediaType('application', 'pdf'),
        ));
      } else if (request.resumeFile.path != null && !kIsWeb) {
        // only use path in non-Web environment
        multipart.files.add(await http.MultipartFile.fromPath('file', request.resumeFile.path!));
      } else {
        throw Exception('Resume file has no accessible content');
      }
      
      final streamed = await multipart.send();
      final respStr = await streamed.stream.bytesToString();
      final respJson = json.decode(respStr);
      return InterviewPrepareResponse.fromJson(respJson);
    } catch (e) {
      throw Exception('Failed to submit interview preparation: $e');
    }
  }

  // Start new interview session
  Future<Map<String, dynamic>> startInterviewSession(String workflowId, int duration, bool isAudio) async {
    try {
      final token = await _getIdToken();
      if (token == null) {
        throw Exception('No authentication token available');
      }

      debugPrint('Calling POST /interviews/start API...');
      
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.interviewsStartEndpoint}'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'workflow_id': workflowId,
          'duration': duration,
          'is_audio': isAudio,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        debugPrint('✅ Real API: Interview session started successfully');
        return data['data']; 
      } else {
        throw Exception('API returned ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      debugPrint('❌ Real API failed: $e');
      debugPrint('🔄 Falling back to mock data...');
      
      try {
        // Mock session data
        await Future.delayed(const Duration(seconds: 1)); 
        final mockSession = {
          'session_id': 'mock_session_${DateTime.now().millisecondsSinceEpoch}',
          'websocket_parameter': 'token=mock_ws_token_${DateTime.now().millisecondsSinceEpoch}',
        };
        debugPrint('✅ Mock API: Interview session started with mock data');
        return mockSession;
      } catch (mockError) {
        debugPrint('❌ Mock data also failed: $mockError');
        throw Exception('Failed to start interview session: Real API failed ($e), Mock data also failed ($mockError)');
      }
    }
  }

  // Get interview feedback
  Future<Map<String, dynamic>> getInterviewFeedback(String workflowId, String sessionId) async {
    try {
      final token = await _getIdToken();
      if (token == null) {
        throw Exception('No authentication token available');
      }

      debugPrint('Calling POST /interviews/$workflowId/$sessionId/feedback API...');
      
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.interviewFeedbackEndpoint(workflowId, sessionId)}'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        debugPrint('✅ Real API: Interview feedback loaded successfully');
        return data; 
      } else {
        throw Exception('API returned ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      debugPrint('❌ Real API failed: $e');
      debugPrint('🔄 Falling back to mock data...');
      
      try {
        // Fallback to mock data
        await Future.delayed(const Duration(milliseconds: 800));
        debugPrint('✅ Mock API: Interview feedback loaded with mock data');
        return MockData.singleInterviewFeedback;
      } catch (mockError) {
        debugPrint('❌ Mock data also failed: $mockError');
        throw Exception('Failed to get interview feedback: Real API failed ($e), Mock data also failed ($mockError)');
      }
    }
  }

  // Get interview history for a workflow
  Future<List<Map<String, dynamic>>> getInterviewHistory(String workflowId) async {
    try {
      final token = await _getIdToken();
      if (token == null) {
        throw Exception('No authentication token available');
      }

      final apiUrl = '${ApiConfig.baseUrl}${ApiConfig.workflowInterviewsEndpoint(workflowId)}';
        debugPrint('Calling GET /workflows/$workflowId/interviews API...');
      
      final response = await http.get(
        Uri.parse(apiUrl),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final interviews = (data['data'] as List).cast<Map<String, dynamic>>();
        debugPrint('✅ Real API: Interview history loaded successfully (${interviews.length} items)');
        return interviews;
      } else {
        throw Exception('API returned ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      debugPrint('❌ Real API failed: $e');
      debugPrint('🔄 Falling back to mock data...');
      
      try {
        await Future.delayed(const Duration(milliseconds: 600));
        
          final filteredHistory = MockData.interviewHistory
              .where((interview) => interview['workflowId'] == workflowId)
              .toList();
          debugPrint('✅ Mock API: Interview history loaded with mock data (${filteredHistory.length} items)');
          return filteredHistory;
      } catch (mockError) {
        debugPrint('❌ Mock data also failed: $mockError');
        throw Exception('Failed to get interview history: Real API failed ($e), Mock data also failed ($mockError)');
      }
    }
  }

  // connect WebSocket
  Future<void> connectWebSocket(String sessionId, String websocketParameter) async {
    try {
      final wsUrl = ApiConfig.getWebSocketUrl(sessionId, websocketParameter);
      debugPrint('Connecting to WebSocket: $wsUrl');
      
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      _wsConnected = true;

      _channel!.stream.listen(
        (message) {
          try {
            final data = json.decode(message);
            
            // only keep the latest text/plain content
            if (data.containsKey('mime_type') && data['mime_type'] == 'text/plain') {
              _currentStreamingMessage = data['data'] ?? '';
              if (_currentMessageId.isEmpty) {
                _currentMessageId = DateTime.now().millisecondsSinceEpoch.toString();
              }
              return;
            }
            
            // render the latest text/plain content when turn_complete
            if (data.containsKey('turn_complete') && data['turn_complete'] == true) {
              if (_currentStreamingMessage.isNotEmpty) {
                final chatMessage = ChatMessage(
                  id: _currentMessageId,
                  role: 'ai',
                  content: _currentStreamingMessage,
                  timestamp: DateTime.now(),
                );
                _onMessageReceived?.call(chatMessage);
                _currentStreamingMessage = '';
                _currentMessageId = '';
              }
              return;
            }
            
            // Handle other types of messages (like status updates)
            if (data.containsKey('messageId') || data.containsKey('role')) {
            final chatMessage = ChatMessage(
              id: data['messageId'] ?? DateTime.now().millisecondsSinceEpoch.toString(),
              role: data['role'] ?? 'ai',
              content: data['message'] ?? data['content'] ?? '',
              timestamp: DateTime.tryParse(data['createAt'] ?? '') ?? DateTime.now(),
            );
            _onMessageReceived?.call(chatMessage);
            }
          } catch (e) {
            // Fallback: treat as plain text message
            final chatMessage = ChatMessage(
              id: DateTime.now().millisecondsSinceEpoch.toString(),
              role: 'ai',
              content: message.toString(),
              timestamp: DateTime.now(),
            );
            _onMessageReceived?.call(chatMessage);
          }
        },
        onDone: () {
          _wsConnected = false;
          _onDisconnected?.call();
        },
        onError: (error) {
          _wsConnected = false;
          _onError?.call(error.toString());
        },
      );
      
      debugPrint('✅ WebSocket connected successfully');
    } catch (e) {
      _wsConnected = false;
      debugPrint('❌ WebSocket connection failed: $e');
      throw Exception('Failed to connect WebSocket: $e');
    }
  }

  // send message to WebSocket
  void sendMessage(String message) {
    if (_wsConnected && _channel != null) {
      // Send message in the correct format expected by backend
      final messageData = {
        'mime_type': 'text/plain',
        'data': message,
      };
      _channel!.sink.add(json.encode(messageData));
      debugPrint('📤 Message sent via WebSocket: $message');
    } else {
      throw Exception('WebSocket not connected');
    }
  }

  // disconnect WebSocket connection
  void disconnectWebSocket() {
    if (_channel != null) {
      if (kIsWeb) {
        _channel!.sink.close();
      } else {
        _channel!.sink.close(1000);
      }
      _channel = null;
    }
    _wsConnected = false;
    debugPrint('🔌 WebSocket disconnected');
  }

  // set WebSocket event listeners
  void setWebSocketListeners({
    Function(ChatMessage)? onMessageReceived,
    Function()? onDisconnected,
    Function(String)? onError,
  }) {
    _onMessageReceived = onMessageReceived;
    _onDisconnected = onDisconnected;
    _onError = onError;
  }

  // check WebSocket connection status
  bool get isWebSocketConnected => _wsConnected;
} 