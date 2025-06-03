import '../models/workflow.dart';
import '../data/mock_data.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../config/api_config.dart';
import 'package:firebase_auth/firebase_auth.dart' as firebase_auth;
import 'package:flutter/foundation.dart';

class WorkflowService {
  static final WorkflowService _instance = WorkflowService._internal();
  factory WorkflowService() => _instance;
  WorkflowService._internal();

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

  // Get workflows for a user
  Future<List<Workflow>> getWorkflows() async {
    try {
      final token = await _getIdToken();
      if (token == null) {
        throw Exception('No authentication token available');
      }

      debugPrint('Calling GET /workflows API...');
      
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.workflowsEndpoint}'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final workflows = (data['data'] as List)
            .map((json) => Workflow.fromJson(json))
            .toList();
        debugPrint('✅ Real API: Workflows loaded successfully (${workflows.length} items)');
        return workflows;
      } else {
        throw Exception('API returned ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      debugPrint('❌ Real API failed: $e');
      debugPrint('🔄 Falling back to mock data...');
      
      try {
        // Fallback to mock data
        final workflows = MockData.workflows.map((workflowData) => Workflow.fromJson(workflowData)).toList();
        debugPrint('✅ Mock API: Workflows loaded with mock data (${workflows.length} items)');
        return workflows;
      } catch (mockError) {
        debugPrint('❌ Mock data also failed: $mockError');
        throw Exception('Failed to load workflows: Real API failed ($e), Mock data also failed ($mockError)');
      }
    }
  }

  // Get recommended Q&As for a workflow
  Future<List<RecommendedQA>> getRecommendedQAs(String workflowId) async {
    try {
      final token = await _getIdToken();
      if (token == null) {
        throw Exception('No authentication token available');
      }

      debugPrint('Calling GET /workflows/$workflowId/recommended-qa API...');
      
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.recommendedQAEndpoint(workflowId)}'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final qas = (data['data'] as List)
            .map((json) => RecommendedQA.fromJson(json))
            .toList();
        debugPrint('✅ Real API: Recommended QAs loaded successfully (${qas.length} items)');
        return qas;
      } else {
        throw Exception('API returned ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      debugPrint('❌ Real API failed: $e');
      debugPrint('🔄 Falling back to mock data...');
      
      try {
        // Fallback to mock data
        final qasData = MockData.recommendedQAs[workflowId] ?? [];
        final qas = qasData.map((qaData) => RecommendedQA.fromJson(qaData)).toList();
        debugPrint('✅ Mock API: Recommended QAs loaded with mock data (${qas.length} items)');
        return qas;
      } catch (mockError) {
        debugPrint('❌ Mock data also failed: $mockError');
        throw Exception('Failed to load recommended QAs: Real API failed ($e), Mock data also failed ($mockError)');
      }
    }
  }
} 