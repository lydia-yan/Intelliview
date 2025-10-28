class User {
  final String? userId;
  final String name;
  final String email;
  final String? photoURL;
  final String? linkedinLink;
  final String? githubLink;
  final String? portfolioLink;
  final String? additionalInfo;
  final DateTime? createAt;

  String? get id => userId;

  User({
    this.userId,
    required this.name,
    required this.email,
    this.photoURL,
    this.linkedinLink,
    this.githubLink,
    this.portfolioLink,
    this.additionalInfo,
    this.createAt,
  });

  factory User.fromJson(Map<String, dynamic>? json) {
    if (json == null) {
      throw Exception('Cannot create User from null data');
    }
    
    return User(
      userId: json['userId'] ?? json['id'],
      name: (json['name'] as String?) ?? '',
      email: (json['email'] as String?) ?? '',
      photoURL: json['photoURL'] as String?,
      linkedinLink: json['linkedinLink'] as String?,
      githubLink: json['githubLink'] as String?,
      portfolioLink: json['portfolioLink'] as String?,
      additionalInfo: json['additionalInfo'] as String?,
      createAt: json['createAt'] != null ? DateTime.parse(json['createAt'] as String) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'userId': userId,
      'name': name,
      'email': email,
      'photoURL': photoURL,
      'linkedinLink': linkedinLink,
      'githubLink': githubLink,
      'portfolioLink': portfolioLink,
      'additionalInfo': additionalInfo,
      'createAt': createAt?.toIso8601String(),
    };
  }

  User copyWith({
    String? userId,
    String? name,
    String? email,
    String? photoURL,
    String? linkedinLink,
    String? githubLink,
    String? portfolioLink,
    String? additionalInfo,
    DateTime? createAt,
  }) {
    return User(
      userId: userId ?? this.userId,
      name: name ?? this.name,
      email: email ?? this.email,
      photoURL: photoURL ?? this.photoURL,
      linkedinLink: linkedinLink ?? this.linkedinLink,
      githubLink: githubLink ?? this.githubLink,
      portfolioLink: portfolioLink ?? this.portfolioLink,
      additionalInfo: additionalInfo ?? this.additionalInfo,
      createAt: createAt ?? this.createAt,
    );
  }

  @override
  String toString() {
    return 'User(userId: $userId, name: $name, email: $email)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is User && other.userId == userId;
  }

  @override
  int get hashCode => userId.hashCode;
} 