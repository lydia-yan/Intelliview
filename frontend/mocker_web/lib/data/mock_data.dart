class MockData {
  // Workflows data
  static List<Map<String, dynamic>> workflows = [
    {
      'id': 'workflow_001',
      'title': 'TechX, Backend Engineer',
      'personalExperience': {
        'resumeInfo': 'Strong backend development experience with Python and Django',
        'linkedinInfo': 'Senior developer at tech companies',
        'githubInfo': 'Active contributor with 50+ repositories',
        'portfolioInfo': 'Built scalable microservices architecture',
        'additionalInfo': 'Led a team of 5 developers',
        'jobDescription': 'Backend Engineer role at TechX focusing on scalable systems',
      },
      'recommendedQAs': [
        {
          'question': 'Tell me about your experience with microservices architecture',
          'answer': 'I have designed and implemented microservices...',
          'tags': ['architecture', 'microservices', 'backend']
        }
      ],
      'createAt': '2024-01-15T10:30:00Z',
    },
    {
      'id': 'workflow_002',
      'title': 'DataCorp, Data Analyst',
      'personalExperience': null, // Not yet prepared
      'recommendedQAs': null,
      'createAt': '2024-01-10T14:20:00Z',
    },
    {
      'id': 'workflow_003',
      'title': 'WebTech, Frontend Developer',
      'personalExperience': {
        'resumeInfo': 'Expert in React and modern frontend technologies',
        'linkedinInfo': 'Frontend specialist with UI/UX experience',
        'githubInfo': 'Created popular React components library',
        'portfolioInfo': 'Built responsive web applications',
        'additionalInfo': 'Mentored junior developers',
        'jobDescription': 'Frontend Developer role focusing on user experience',
      },
      'recommendedQAs': [
        {
          'question': 'How do you handle state management in large React applications?',
          'answer': 'I prefer using Redux Toolkit for complex state...',
          'tags': ['react', 'state-management', 'frontend']
        }
      ],
      'createAt': '2024-01-20T09:15:00Z',
    },
    {
      'id': 'workflow_004',
      'title': 'CloudFirst, DevOps Engineer',
      'personalExperience': {
        'resumeInfo': 'Experienced in AWS, Docker, and Kubernetes deployment',
        'linkedinInfo': 'DevOps specialist with cloud infrastructure expertise',
        'githubInfo': 'Maintained CI/CD pipelines for enterprise applications',
        'portfolioInfo': 'Automated deployment processes reducing downtime by 85%',
        'additionalInfo': 'Certified AWS Solutions Architect',
        'jobDescription': 'DevOps Engineer role focusing on cloud infrastructure and automation',
      },
      'recommendedQAs': [
        {
          'question': 'Describe your experience with containerization and orchestration',
          'answer': 'I have extensive experience with Docker and Kubernetes...',
          'tags': ['docker', 'kubernetes', 'devops', 'cloud']
        }
      ],
      'createAt': '2024-01-22T11:45:00Z',
    },
    {
      'id': 'workflow_005',
      'title': 'InnovateLabs, Full Stack Developer',
      'personalExperience': {
        'resumeInfo': 'Full stack development with MEAN/MERN stack expertise',
        'linkedinInfo': 'Full stack developer with startup experience',
        'githubInfo': 'Built end-to-end web applications and APIs',
        'portfolioInfo': 'Developed e-commerce platform serving 10k+ users',
        'additionalInfo': 'Experience with agile development and startup culture',
        'jobDescription': 'Full Stack Developer role building modern web applications',
      },
      'recommendedQAs': [
        {
          'question': 'How do you approach full stack application architecture?',
          'answer': 'I start by designing a scalable API architecture...',
          'tags': ['fullstack', 'architecture', 'api', 'database']
        }
      ],
      'createAt': '2024-01-25T14:30:00Z',
    },
    {
      'id': 'workflow_006',
      'title': 'FinanceCorpAI, Machine Learning Engineer',
      'personalExperience': null, // Not yet prepared
      'recommendedQAs': null,
      'createAt': '2024-01-28T16:20:00Z',
    },
  ];

  // Recommended QA data (grouped by workflow ID)
  static Map<String, List<Map<String, dynamic>>> recommendedQAs = {
    'workflow_001': [
      {
        'question': 'Tell me about your experience with microservices architecture',
        'answer': 'I have designed and implemented microservices using Docker and Kubernetes...',
        'tags': ['architecture', 'microservices', 'backend']
      },
      {
        'question': 'How do you handle database optimization?',
        'answer': 'I focus on query optimization, indexing, and caching strategies...',
        'tags': ['database', 'optimization', 'performance']
      },
      {
        'question': 'Describe your experience with CI/CD pipelines',
        'answer': 'I have set up automated pipelines using Jenkins and GitHub Actions...',
        'tags': ['devops', 'ci-cd', 'automation']
      },
    ],
    'workflow_003': [
      {
        'question': 'How do you handle state management in large React applications?',
        'answer': 'I prefer using Redux Toolkit for complex state management...',
        'tags': ['react', 'state-management', 'frontend']
      },
      {
        'question': 'What is your approach to responsive design?',
        'answer': 'I use CSS Grid and Flexbox with mobile-first methodology...',
        'tags': ['css', 'responsive-design', 'mobile']
      },
    ],
    'workflow_004': [
      {
        'question': 'Describe your experience with containerization and orchestration',
        'answer': 'I have extensive experience with Docker and Kubernetes, managing container deployments...',
        'tags': ['docker', 'kubernetes', 'devops', 'cloud']
      },
      {
        'question': 'How do you implement monitoring and alerting in production?',
        'answer': 'I use Prometheus and Grafana for monitoring, with PagerDuty for alerting...',
        'tags': ['monitoring', 'alerting', 'observability']
      },
      {
        'question': 'What is your approach to infrastructure as code?',
        'answer': 'I prefer Terraform for infrastructure management with proper state management...',
        'tags': ['terraform', 'iac', 'automation']
      },
    ],
    'workflow_005': [
      {
        'question': 'How do you approach full stack application architecture?',
        'answer': 'I start by designing a scalable API architecture with proper separation of concerns...',
        'tags': ['fullstack', 'architecture', 'api', 'database']
      },
      {
        'question': 'What is your experience with both frontend and backend testing?',
        'answer': 'I implement unit tests, integration tests, and end-to-end tests using Jest and Cypress...',
        'tags': ['testing', 'jest', 'cypress', 'quality']
      },
      {
        'question': 'How do you ensure application performance across the stack?',
        'answer': 'I optimize database queries, implement caching, and use performance monitoring tools...',
        'tags': ['performance', 'optimization', 'caching']
      },
    ],
  };

  // User profile data (updated field names to match backend)
  static Map<String, dynamic> userProfile = {
    'userId': 'user_001',
    'name': 'May Yan',
    'email': 'may.yan@example.com',
    'photoURL': '',
    'linkedinLink': 'https://www.linkedin.com/in/mayyan/',
    'githubLink': 'https://github.com/lydia-yan',
    'portfolioLink': 'https://jenny-cheng.dev',
    'additionalInfo': 'Gave presentations at university AI club, mentored junior developers. Skilled at solving complex problems.',
    'createAt': '2024-01-01T00:00:00Z',
  };

  // Interview chat data (updated to use workflow ID)
  static Map<String, List<Map<String, dynamic>>> interviewChats = {
    'workflow_001': [
      {
        'messageId': 'msg_001',
        'role': 'ai',
        'message': 'Hello! I\'m your AI interviewer for the Backend Engineer position at TechX. Let\'s begin with a brief introduction about yourself.',
        'createAt': '2024-01-15T10:30:00Z',
      },
      {
        'messageId': 'msg_002',
        'role': 'user',
        'message': 'Hi, I am May, a backend engineer with 3 years of experience.',
        'createAt': '2024-01-15T10:31:00Z',
      },
    ],
    'workflow_002': [
      {
        'messageId': 'msg_003',
        'role': 'ai',
        'message': 'Hello! I\'m your AI interviewer for the Data Analyst position at DataCorp. Let\'s begin with a brief introduction about yourself.',
        'createAt': '2024-01-10T14:20:00Z',
      },
    ],
    'workflow_003': [
      {
        'messageId': 'msg_004',
        'role': 'ai',
        'message': 'Hello! I\'m your AI interviewer for the Frontend Developer position at WebTech. Let\'s begin with a brief introduction about yourself.',
        'createAt': '2024-01-20T09:15:00Z',
      },
    ],
    'workflow_004': [
      {
        'messageId': 'msg_005',
        'role': 'ai',
        'message': 'Hello! I\'m your AI interviewer for the DevOps Engineer position at CloudFirst. Let\'s begin with a brief introduction about yourself.',
        'createAt': '2024-01-22T11:45:00Z',
      },
    ],
    'workflow_005': [
      {
        'messageId': 'msg_006',
        'role': 'ai',
        'message': 'Hello! I\'m your AI interviewer for the Full Stack Developer position at InnovateLabs. Let\'s begin with a brief introduction about yourself.',
        'createAt': '2024-01-25T14:30:00Z',
      },
    ],
    'workflow_006': [
      {
        'messageId': 'msg_007',
        'role': 'ai',
        'message': 'Hello! I\'m your AI interviewer for the Machine Learning Engineer position at FinanceCorpAI. Let\'s begin with a brief introduction about yourself.',
        'createAt': '2024-01-28T16:20:00Z',
      },
    ],
  };

  // Interview preparation response data (updated to workflow format)
  static Map<String, dynamic> interviewPrepareResponse = {
    'success': true,
    'message': 'Interview preparation data processed successfully',
    'data': {
      'id': 'workflow_new',
      'personalExperience': {
        'skillsExtracted': ['Python', 'Django', 'PostgreSQL', 'AWS'],
        'experienceYears': 3,
        'keyAchievements': [
          'Led development of microservices architecture',
          'Improved system performance by 40%',
        ],
      },
      'preparationTips': [
        'Review system design principles',
        'Practice coding algorithms',
        'Prepare behavioral questions',
      ],
    },
    'createAt': '2024-01-15T10:30:00Z',
  };

  // AI interview response templates
  static List<String> aiInterviewResponses = [
    'Thank you for sharing. Can you tell me why you\'re interested in this role?',
    'That\'s interesting. Can you walk me through a challenging project you\'ve worked on?',
    'Great experience! How do you handle working under pressure?',
    'Can you describe your approach to problem-solving?',
    'What technologies are you most excited to work with?',
    'How do you stay updated with the latest industry trends?',
    'Can you give me an example of how you\'ve collaborated with a team?',
    'What would you say is your greatest strength as a developer?',
  ];

  // Get random AI response
  static String getRandomAiResponse() {
    final random = DateTime.now().millisecondsSinceEpoch % aiInterviewResponses.length;
    return aiInterviewResponses[random];
  }

  // Generate new message ID
  static String generateMessageId() {
    return 'msg_${DateTime.now().millisecondsSinceEpoch}';
  }

  // Generate new workflow ID
  static String generateWorkflowId() {
    return 'workflow_${DateTime.now().millisecondsSinceEpoch}';
  }

  // Interview feedback data (single interview feedback)
  static Map<String, dynamic> singleInterviewFeedback = {
    'success': true,
    'data': {
      'positives': [
        'You presented your experience clearly and stayed focused on key responsibilities.',
        'You demonstrated strong alignment with the role\'s technical requirements, especially in backend system design.',
        'Your communication was professional and well-structured throughout the interview.'
      ],
      'improvementAreas': [
        {
          'topic': 'Quantifying Results',
          'example': 'In your STAR response, you described your actions well but didn\'t share the outcome or measurable impact.',
          'suggestion': 'Try adding metrics like \'improved API response time by 30%\' to emphasize your contribution.'
        },
        {
          'topic': 'Self-Reflection',
          'example': 'When asked about a challenge, you explained the situation but missed reflecting on what you learned.',
          'suggestion': 'Use closing lines like \'What I took away from that experience was...\' to show growth.'
        },
        {
          'topic': 'Technical Depth',
          'example': 'Your answers showed good breadth but could benefit from more technical details.',
          'suggestion': 'When discussing technical solutions, include specific tools, frameworks, or methodologies you used.'
        }
      ],
      'resources': [
        {
          'title': 'Improving Behavioral Interview Answers',
          'link': 'https://example.com/star-tips'
        },
        {
          'title': 'Effective Communication in Interviews',
          'link': 'https://example.com/interview-communication'
        },
        {
          'title': 'Technical Interview Best Practices',
          'link': 'https://example.com/technical-interviews'
        }
      ],
      'reflectionPrompt': [
        'What impact did your actions have in the example you shared?',
        'How would you approach the same situation differently today?',
        'What specific metrics could you use to demonstrate your achievements?'
      ],
      'tone': 'respectful',
      'overallRating': 4,
      'focusTags': ['clarity', 'impact', 'self-reflection', 'technical-depth']
    }
  };

  // Interview history data (for feedback history page)
  static List<Map<String, dynamic>> interviewHistory = [
    {
      'interviewId': 'interview_001',
      'workflowId': 'workflow_001',
      'position': 'Backend Engineer',
      'company': 'TechX',
      'duration_minutes': 25,
      'transcript': [
        {
          'role': 'ai',
          'content': 'Hello! I\'m your AI interviewer for the Backend Engineer position at TechX. Let\'s begin with a brief introduction about yourself.',
          'timestamp': '2024-01-15T10:30:00Z'
        },
        {
          'role': 'user',
          'content': 'Hi, I am May, a backend engineer with 3 years of experience in Python and Django.',
          'timestamp': '2024-01-15T10:30:30Z'
        },
        {
          'role': 'ai',
          'content': 'Great! Can you tell me about a challenging project you\'ve worked on recently?',
          'timestamp': '2024-01-15T10:31:00Z'
        },
        {
          'role': 'user',
          'content': 'I led the development of a microservices architecture that improved our system performance by 40%. The main challenge was ensuring data consistency across services.',
          'timestamp': '2024-01-15T10:31:45Z'
        },
        {
          'role': 'ai',
          'content': 'That sounds impressive! How did you handle the data consistency challenges?',
          'timestamp': '2024-01-15T10:32:15Z'
        },
        {
          'role': 'user',
          'content': 'We implemented distributed transactions using the Saga pattern and used Redis for caching frequently accessed data.',
          'timestamp': '2024-01-15T10:33:00Z'
        }
      ],
      'feedback': {
        'positives': [
          'You presented your experience clearly and stayed focused on key responsibilities.',
          'You demonstrated strong alignment with the role\'s technical requirements, especially in backend system design.'
        ],
        'improvementAreas': [
          {
            'topic': 'Quantifying Results',
            'example': 'In your STAR response, you described your actions well but didn\'t share the outcome or measurable impact.',
            'suggestion': 'Try adding metrics like \'improved API response time by 30%\' to emphasize your contribution.'
          }
        ],
        'resources': [
          {
            'title': 'Improving Behavioral Interview Answers',
            'link': 'https://example.com/star-tips'
          }
        ],
        'reflectionPrompt': [
          'What impact did your actions have in the example you shared?'
        ],
        'tone': 'respectful',
        'overallRating': 4,
        'focusTags': ['clarity', 'impact']
      },
      'createAt': '2024-01-15T10:30:00Z'
    },
    {
      'interviewId': 'interview_002',
      'workflowId': 'workflow_003',
      'position': 'Frontend Developer',
      'company': 'WebTech',
      'duration_minutes': 20,
      'transcript': [
        {
          'role': 'ai',
          'content': 'Hello! I\'m your AI interviewer for the Frontend Developer position at WebTech. Let\'s start!',
          'timestamp': '2024-01-20T09:15:00Z'
        },
        {
          'role': 'user',
          'content': 'Hi! I\'m excited to discuss my frontend development experience with React and TypeScript.',
          'timestamp': '2024-01-20T09:15:30Z'
        }
      ],
      'feedback': {
        'positives': [
          'Strong technical knowledge in modern frontend frameworks',
          'Enthusiasm for the role was clearly communicated'
        ],
        'improvementAreas': [
          {
            'topic': 'Project Examples',
            'example': 'You mentioned experience but didn\'t provide specific project examples.',
            'suggestion': 'Prepare 2-3 concrete projects you can discuss in detail.'
          }
        ],
        'resources': [
          {
            'title': 'Frontend Interview Preparation',
            'link': 'https://example.com/frontend-prep'
          }
        ],
        'reflectionPrompt': [
          'What specific projects best demonstrate your frontend skills?'
        ],
        'tone': 'respectful',
        'overallRating': 3,
        'focusTags': ['technical-knowledge', 'examples']
      },
      'createAt': '2024-01-20T09:15:00Z'
    }
  ];

  // Auth init response (for /auth/init endpoint)
  static Map<String, dynamic> authInitResponse = {
    'success': true,
    'message': 'User initialized successfully',
    'data': {
      'user': {
        'userId': 'user_001',
        'name': 'May Yan',
        'email': 'may.yan@example.com',
        'photoURL': '',
        'isNew': false,
        'createAt': '2024-01-01T00:00:00Z',
      },
      'preferences': {
        'language': 'en',
        'timezone': 'UTC',
        'notifications': true,
      }
    },
  };
} 