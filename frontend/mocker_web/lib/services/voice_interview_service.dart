import 'dart:typed_data';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';

class VoiceInterviewService {
  static const String _baseUrl = ApiConfig.baseUrl;

  /// Send audio data to backend for processing
  /// This method sends the recorded audio to the backend for Google Live API integration
  /// Note: Session management and feedback are handled by the existing InterviewService
  static Future<Map<String, dynamic>> sendAudioToBackend({
    required Uint8List audioData,
    required String sessionId,
    required String workflowId,
  }) async {
    try {
      final url = Uri.parse('$_baseUrl/voice-interview/process');
      
      final request = http.MultipartRequest('POST', url);
      
      // Add audio file
      request.files.add(
        http.MultipartFile.fromBytes(
          'audio',
          audioData,
          filename: 'voice_interview_${DateTime.now().millisecondsSinceEpoch}.m4a',
        ),
      );
      
      // Add metadata
      request.fields['session_id'] = sessionId;
      request.fields['workflow_id'] = workflowId;
      request.fields['timestamp'] = DateTime.now().toIso8601String();
      
      final response = await request.send();
      final responseBody = await response.stream.bytesToString();
      
      if (response.statusCode == 200) {
        return {
          'success': true,
          'data': responseBody,
          'status_code': response.statusCode,
        };
      } else {
        return {
          'success': false,
          'error': 'HTTP ${response.statusCode}: $responseBody',
          'status_code': response.statusCode,
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
        'status_code': null,
      };
    }
  }
} 