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
  final InterviewPrepareData? data;
  final DateTime timestamp;

  InterviewPrepareResponse({
    required this.success,
    required this.message,
    this.data,
    required this.timestamp,
  });

  factory InterviewPrepareResponse.fromJson(Map<String, dynamic> json) {
    return InterviewPrepareResponse(
      success: json['success'] as bool,
      message: json['message'] as String,
      data: json['data'] != null ? InterviewPrepareData.fromJson(json['data']) : null,
      timestamp: DateTime.parse(json['timestamp'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'success': success,
      'message': message,
      'data': data?.toJson(),
      'timestamp': timestamp.toIso8601String(),
    };
  }
}

class InterviewPrepareData {
  final String workflowId;
  final ResumeAnalysis resumeAnalysis;
  final List<String> preparationTips;

  InterviewPrepareData({
    required this.workflowId,
    required this.resumeAnalysis,
    required this.preparationTips,
  });

  factory InterviewPrepareData.fromJson(Map<String, dynamic> json) {
    return InterviewPrepareData(
      workflowId: json['workflow_id'] as String,
      resumeAnalysis: ResumeAnalysis.fromJson(json['resume_analysis']),
      preparationTips: List<String>.from(json['preparation_tips']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'workflow_id': workflowId,
      'resume_analysis': resumeAnalysis.toJson(),
      'preparation_tips': preparationTips,
    };
  }
}

class ResumeAnalysis {
  final List<String> skillsExtracted;
  final int experienceYears;
  final List<String> keyAchievements;

  ResumeAnalysis({
    required this.skillsExtracted,
    required this.experienceYears,
    required this.keyAchievements,
  });

  factory ResumeAnalysis.fromJson(Map<String, dynamic> json) {
    return ResumeAnalysis(
      skillsExtracted: List<String>.from(json['skills_extracted']),
      experienceYears: json['experience_years'] as int,
      keyAchievements: List<String>.from(json['key_achievements']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'skills_extracted': skillsExtracted,
      'experience_years': experienceYears,
      'key_achievements': keyAchievements,
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