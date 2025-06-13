class ApiConfig {
  // Base API configuration
  //static const String baseUrl = 'http://localhost:8000';
  static const String baseUrl =
      'https://intelliview-1022761324834.europe-west1.run.app';

  // Authentication endpoints
  static const String authInitEndpoint = '/auth/init';

  // User endpoints
  static const String userEndpoint = '/user';
  static const String userAvatarEndpoint = '/user/avatar';

  // Workflow endpoints
  static const String workflowsEndpoint = '/workflows';
  static const String workflowStartWithPdfEndpoint =
      '/workflows/start-with-pdf';
  static String recommendedQAEndpoint(String workflowId) =>
      '/workflows/$workflowId/recommended-qa';

  // Interview endpoints
  static const String interviewsStartEndpoint = '/interviews/start';

  // Interview feedback endpoints
  static String interviewFeedbackEndpoint(
    String workflowId,
    String sessionId,
  ) => '/interviews/$workflowId/$sessionId/feedback';
  static String workflowInterviewsEndpoint(String workflowId) =>
      '/workflows/$workflowId/interviews';

  // WebSocket endpoints
  static String getWebSocketUrl(String sessionId, String parameter) {
    final wsBaseUrl = baseUrl
        .replaceFirst('http://', 'ws://')
        .replaceFirst('https://', 'wss://');
    if (parameter.startsWith('?')) {
      return '$wsBaseUrl/ws/$sessionId$parameter';
    } else {
      return '$wsBaseUrl/ws/$sessionId?$parameter';
    }
  }
}
