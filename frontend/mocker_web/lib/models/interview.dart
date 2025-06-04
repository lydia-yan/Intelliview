import 'package:file_picker/file_picker.dart';

class ChatMessage {
  final String id;
  final String role; // 'Interviewer' or 'Candidate'
  final String content;
  final DateTime timestamp;

  ChatMessage({
    required this.id,
    required this.role,
    required this.content,
    required this.timestamp,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] ?? json['interviewId'] ?? json['messageId'] ?? '',
      role: json['role'] as String,
      content: json['content'] ?? json['message'] ?? '',
      timestamp: DateTime.parse(json['timestamp'] ?? json['createAt'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'role': role,
      'content': content,
      'timestamp': timestamp.toIso8601String(),
    };
  }

  @override
  String toString() {
    return 'ChatMessage(id: $id, role: $role, content: $content)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is ChatMessage && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}

class InterviewPrepareRequest {
  final PlatformFile resumeFile;
  final String jobDescription;
  final String? linkedinLink;
  final String? githubLink;
  final String? portfolioLink;
  final String? additionalInfo;
  final int? numQuestions;
  final String? sessionId;

  InterviewPrepareRequest({
    required this.resumeFile,
    required this.jobDescription,
    this.linkedinLink,
    this.githubLink,
    this.portfolioLink,
    this.additionalInfo,
    this.numQuestions,
    this.sessionId,
  });

  Map<String, dynamic> toJson() {
    return {
      'resume_file_name': resumeFile.name,
      'resume_content': resumeFile.bytes,
      'linkedin_url': linkedinLink,
      'github_url': githubLink,
      'portfolio_url': portfolioLink,
      'additional_info': additionalInfo,
      'job_description': jobDescription,
      'num_questions': numQuestions,
      'session_id': sessionId,
    };
  }

  @override
  String toString() {
    return 'InterviewPrepareRequest(resumeFileName: ${resumeFile.name}, linkedinUrl: $linkedinLink, githubUrl: $githubLink)';
  }
}

class InterviewPrepareResponse {
  final bool success;
  final String message;
  final String? sessionId;
  final String? workflowId;
  final String? userId;
  final List<String>? completedAgents;
  final double? processingTime;
  final String? error;

  InterviewPrepareResponse({
    required this.success,
    this.message = '',
    this.sessionId,
    this.workflowId,
    this.userId,
    this.completedAgents,
    this.processingTime,
    this.error,
  });

  factory InterviewPrepareResponse.fromJson(Map<String, dynamic> json) {
    return InterviewPrepareResponse(
      success: json['success'] as bool? ?? false,
      message: json['message'] as String? ?? json['error'] as String? ?? '',
      sessionId: json['session_id'] as String?,
      workflowId: json['workflow_id'] as String?,
      userId: json['user_id'] as String?,
      completedAgents: json['completed_agents'] != null 
          ? List<String>.from(json['completed_agents']) 
          : null,
      processingTime: json['processing_time'] as double?,
      error: json['error'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'success': success,
      'message': message,
      'session_id': sessionId,
      'workflow_id': workflowId,
      'user_id': userId,
      'completed_agents': completedAgents,
      'processing_time': processingTime,
      'error': error,
    };
  }
}

class ChatRequest {
  final String workflowId;
  final String message;

  ChatRequest({
    required this.workflowId,
    required this.message,
  });

  Map<String, dynamic> toJson() {
    return {
      'workflow_id': workflowId,
      'message': message,
    };
  }
}

class ChatResponse {
  final bool success;
  final String message;
  final ChatMessage? data;
  final DateTime timestamp;

  ChatResponse({
    required this.success,
    required this.message,
    this.data,
    required this.timestamp,
  });

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    return ChatResponse(
      success: json['success'] as bool,
      message: json['message'] as String,
      data: json['data'] != null ? ChatMessage.fromJson(json['data']) : null,
      timestamp: DateTime.parse(json['timestamp'] as String),
    );
  }
} 