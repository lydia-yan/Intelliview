// Workflow model representing a job application workflow
class Workflow {
  final String id; 
  final String title; // Format: "company, position"
  final PersonalExperience? personalExperience;
  final String createAt;


  String get workflowId => id;

  Workflow({
    required this.id,
    required this.title,
    this.personalExperience,
    required this.createAt,
  });

  // Extract company from title
  String get company {
    final parts = title.split(', ');
    return parts.isNotEmpty ? parts[0] : '';
  }

  // Extract position from title
  String get position {
    final parts = title.split(', ');
    return parts.length > 1 ? parts[1] : '';
  }

  factory Workflow.fromJson(Map<String, dynamic> json) {
    return Workflow(
      id: json['id'] ?? json['workflowId'] ?? '',
      title: json['title'] ?? '',
      personalExperience: json['personalExperience'] != null
          ? PersonalExperience.fromJson(json['personalExperience'])
          : null,
      createAt: json['createAt'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'personalExperience': personalExperience?.toJson(),
      'createAt': createAt,
    };
  }

  @override
  String toString() {
    return 'Workflow(id: $id, title: $title, company: $company, position: $position)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Workflow && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}

// Personal experience data for interview preparation
class PersonalExperience {
  final String? resumeInfo;
  final String? linkedinInfo;
  final String? githubInfo;
  final String? portfolioInfo;
  final String? additionalInfo;
  final String? jobDescription;

  PersonalExperience({
    this.resumeInfo,
    this.linkedinInfo,
    this.githubInfo,
    this.portfolioInfo,
    this.additionalInfo,
    this.jobDescription,
  });

  factory PersonalExperience.fromJson(Map<String, dynamic> json) {
    return PersonalExperience(
      resumeInfo: json['resumeInfo'],
      linkedinInfo: json['linkedinInfo'],
      githubInfo: json['githubInfo'],
      portfolioInfo: json['portfolioInfo'],
      additionalInfo: json['additionalInfo'],
      jobDescription: json['jobDescription'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'resumeInfo': resumeInfo,
      'linkedinInfo': linkedinInfo,
      'githubInfo': githubInfo,
      'portfolioInfo': portfolioInfo,
      'additionalInfo': additionalInfo,
      'jobDescription': jobDescription,
    };
  }
}

// Recommended Q&A for specific workflow
class RecommendedQA {
  final String question;
  final String answer;
  final List<String> tags;

  RecommendedQA({
    required this.question,
    required this.answer,
    required this.tags,
  });

  factory RecommendedQA.fromJson(Map<String, dynamic> json) {
    return RecommendedQA(
      question: json['question'] ?? '',
      answer: json['answer'] ?? '',
      tags: List<String>.from(json['tags'] ?? []),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'question': question,
      'answer': answer,
      'tags': tags,
    };
  }

  @override
  String toString() {
    return 'RecommendedQA(question: $question, tags: $tags)';
  }
} 