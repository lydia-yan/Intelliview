import 'package:flutter/material.dart';
import '../models/workflow.dart';
import '../services/workflow_service.dart';
import '../widgets/navbar.dart';
import 'interview_prepare_page.dart';
import 'mock_interview_page.dart';
import 'profile_page.dart';
import 'qa_page.dart';
import 'feedback_page.dart';
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../theme/app_theme.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  int _selectedIndex = 0;
  String? _selectedWorkflowId; // for passing selected workflow to QA page

  final List<_NavItem> _navItems = const [
    _NavItem(icon: Icons.dashboard, label: 'Dashboard'),
    _NavItem(icon: Icons.upload_file, label: 'Prepare'),
    _NavItem(icon: Icons.record_voice_over, label: 'Mock Interview'),
    _NavItem(icon: Icons.quiz, label: 'Q&A'),
    _NavItem(icon: Icons.assessment, label: 'Feedback'),
    _NavItem(icon: Icons.person, label: 'Profile'),
  ];

  List<Widget> get _pages => [
    _WorkbenchPage(onViewQA: (workflowId) {
      setState(() {
        _selectedIndex = 3; // QA page index
        _selectedWorkflowId = workflowId;
      });
    }),
    InterviewPreparePage(onNavigateToDashboard: () {
      setState(() {
        _selectedIndex = 0; 
      });
    }),
    const MockInterviewPage(),
    QAPage(preSelectedWorkflowId: _selectedWorkflowId),
    const FeedbackPage(),
    const ProfilePage(),
  ];

  @override
  Widget build(BuildContext context) {
    // Responsive layout
    final screenWidth = MediaQuery.of(context).size.width;
    final isNarrow = screenWidth < 900;

    return Scaffold(
          body: isNarrow
              ? Column(
                  children: [
                    // Top app bar height spacer to match existing navbar spacing if used elsewhere
                    const SizedBox(height: 0),
                    Expanded(
                      child: _pages[_selectedIndex],
                    ),
                  ],
                )
              : Row(
                  children: [
              // Sidebar
              Material(
                elevation: 0,
                child: Container(
                  width: 220,
                  decoration: BoxDecoration(
                    color: AppTheme.surfaceWhite,
                    border: Border(
                      right: BorderSide(
                        color: AppTheme.borderGray,
                        width: 1,
                      ),
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SizedBox(height: 72),
                      // Logo/app name
                      Padding(
                        padding: const EdgeInsets.only(left: 24.0),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            Icon(Icons.bubble_chart, color: AppTheme.primaryBlue, size: 32),
                            const SizedBox(width: 10),
                            Text('Intelliview', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20, color: AppTheme.darkGray)),
                          ],
                        ),
                      ),
                      const SizedBox(height: 60),
                      // Nav items
                      Expanded(
                        child: ListView.builder(
                          itemCount: _navItems.length - 1,
                          itemBuilder: (context, idx) {
                            final item = _navItems[idx];
                            final selected = _selectedIndex == idx;
                            return _SidebarButton(
                              icon: item.icon,
                              label: item.label,
                              selected: selected,
                              onTap: () => setState(() => _selectedIndex = idx),
                            );
                          },
                        ),
                      ),
                      
                      // Avatar (profile)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 40.0, top: 8, left: 24.0),
                        child: InkWell(
                          borderRadius: BorderRadius.circular(28),
                          onTap: () => setState(() => _selectedIndex = 5),
                          child: CircleAvatar(
                            radius: 28,
                            backgroundColor: _selectedIndex == 5 ? AppTheme.primaryBlue : AppTheme.borderGray,
                            child: Icon(Icons.person, color: _selectedIndex == 5 ? AppTheme.surfaceWhite : AppTheme.mediumGray, size: 32),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              // Main content
              Expanded(
                child: Container(
                  color: AppTheme.lightGray,
                  child: _pages[_selectedIndex],
                ),
              ),
            ],
          ),
         bottomNavigationBar: isNarrow
              ? Container(
                  color: const Color(0xFFF3F7FF),
                  child: SafeArea(
                                         child: Container(
                       height: 80,
                       padding: const EdgeInsets.symmetric(horizontal: 8),
                       child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: _navItems.asMap().entries.map((entry) {
                          final idx = entry.key;
                          final item = entry.value;
                          final isSelected = _selectedIndex == idx;
                          return Expanded(
                            child: GestureDetector(
                              onTap: () => setState(() => _selectedIndex = idx),
                              child: Container(
                                margin: const EdgeInsets.symmetric(horizontal: 1),
                                padding: const EdgeInsets.symmetric(vertical: 8),
                                decoration: BoxDecoration(
                                  color: isSelected ? const Color(0xFFE0EAFF) : Colors.transparent,
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Column(
                                  mainAxisSize: MainAxisSize.min,
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(
                                      item.icon,
                                      color: isSelected ? AppTheme.primaryBlue : AppTheme.mediumGray,
                                      size: 22,
                                    ),
                                    const SizedBox(height: 2),
                                    Text(
                                      (isNarrow && item.label == 'Mock Interview') ? 'Mock' : item.label,
                                      style: TextStyle(
                                        fontSize: 10,
                                        color: isSelected ? AppTheme.primaryBlue : AppTheme.mediumGray,
                                        fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                                      ),
                                      textAlign: TextAlign.center,
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          );
                        }).toList(),
                      ),
                    ),
                  ),
                )
              : null,
    );
  }
}

class _SidebarButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool selected;
  final VoidCallback onTap;
  const _SidebarButton({required this.icon, required this.label, required this.selected, required this.onTap});
  
  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
      decoration: BoxDecoration(
        color: selected ? AppTheme.lightBlue : Colors.transparent,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(8),
          child: Container(
            padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 16),
            child: Row(
              children: [
                Icon(
                  icon, 
                  color: selected ? AppTheme.primaryBlue : AppTheme.mediumGray, 
                  size: 22
                ),
                const SizedBox(width: 16),
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 15,
                    color: selected ? AppTheme.primaryBlue : AppTheme.darkGray,
                    fontWeight: selected ? FontWeight.bold : FontWeight.w500,
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

class _NavItem {
  final IconData icon;
  final String label;
  const _NavItem({required this.icon, required this.label});
}

// Workbench page (keep original content, but all text in English)
class _WorkbenchPage extends StatefulWidget {
  final Function(String workflowId)? onViewQA;
  
  const _WorkbenchPage({this.onViewQA});
  
  @override
  State<_WorkbenchPage> createState() => _WorkbenchPageState();
}

class _WorkbenchPageState extends State<_WorkbenchPage> {
  final WorkflowService _workflowService = WorkflowService();
  List<Workflow> workflows = [];
  bool _loading = true;
  String? _error;
  
  // Local state management - track workflow status (frontend UI only, not synced with backend)
  Map<String, String> _workflowStates = {};

  static const String _localStorageKey = 'workflow_status_map';

  @override
  void initState() {
    super.initState();
    _loadWorkflows();
  }

  // Load status from local storage (auto-restore after page refresh)
  Future<Map<String, String>> _loadStatusFromLocal() async {
    final prefs = await SharedPreferences.getInstance();
    final jsonStr = prefs.getString(_localStorageKey);
    if (jsonStr == null) return {};
    try {
      final map = Map<String, dynamic>.from(jsonDecode(jsonStr));
      return map.map((k, v) => MapEntry(k, v as String));
    } catch (_) {
      return {};
    }
  }

  // Save status to local storage (frontend UI only, doesn't affect backend)
  Future<void> _saveStatusToLocal() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_localStorageKey, jsonEncode(_workflowStates));
  }

  // Initialize: all workflows default to 'In Progress'
  Future<void> _loadWorkflows() async {
    try {
      if (!mounted) return;
      setState(() {
        _loading = true;
        _error = null;
      });
      final loadedWorkflows = await _workflowService.getWorkflows();
      final localStatus = await _loadStatusFromLocal();
      if (!mounted) return;
      setState(() {
        workflows = loadedWorkflows;
        _loading = false;
        _workflowStates = {
          for (var workflow in workflows)
            workflow.id: localStatus[workflow.id] ?? 'In Progress'
        };
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  // User toggles status - only affects local UI and localStorage
  void _toggleWorkflowState(String workflowId) {
    setState(() {
      final currentState = _workflowStates[workflowId] ?? 'In Progress';
      _workflowStates[workflowId] = currentState == 'In Progress' ? 'Complete' : 'In Progress';
      _saveStatusToLocal();
    });
  }

  void _showWorkflowDetail(Workflow workflow) {
    final currentState = _workflowStates[workflow.id] ?? 'In Progress';
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.surfaceWhite,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        elevation: 8,
        title: Text(
          workflow.position,
          style: TextStyle(
            color: AppTheme.darkGray,
            fontWeight: FontWeight.bold,
          ),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Company: ${workflow.company}',
              style: TextStyle(color: AppTheme.darkGray),
            ),
            Text(
              'Status: $currentState',
              style: TextStyle(color: AppTheme.darkGray),
            ),
            if (workflow.personalExperience != null) ...[
              const SizedBox(height: 8),
              const Text('Preparation completed', style: TextStyle(color: Colors.green)),
            ],
          ],
        ),
        actions: [
          if (workflow.personalExperience != null)
            TextButton.icon(
              onPressed: () {
                Navigator.of(ctx).pop();
                // Use callback to notify parent to switch to QA page
                widget.onViewQA?.call(workflow.id);
              },
              icon: Icon(Icons.quiz, color: AppTheme.primaryBlue),
              label: Text('View Q&A', style: TextStyle(color: AppTheme.primaryBlue)),
            ),
          TextButton(
            onPressed: () {
              Navigator.of(ctx).pop();
              _toggleWorkflowState(workflow.id);
            },
            child: Text(
              'Mark as ${currentState == 'In Progress' ? 'Complete' : 'In Progress'}',
              style: TextStyle(color: AppTheme.primaryBlue),
            ),
          ),
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: Text('Close', style: TextStyle(color: AppTheme.mediumGray)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('Error: $_error', style: const TextStyle(color: Colors.red)),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadWorkflows,
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    return Column(
      children: [
        // NavBar
        const NavBar(
          title: 'Dashboard',
        ),
        
        // Main content
        Expanded(
          child: Padding(
            padding: EdgeInsets.symmetric(
              horizontal: MediaQuery.of(context).size.width < 600 ? 16.0 : 64.0, 
              vertical: 32.0
            ),
            child: workflows.isEmpty
                ? const Center(child: Text('No workflows found. Please prepare for interviews first.'))
                : Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // My Interviews title
                      Text(
                        'My Interviews',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: AppTheme.darkGray,
                        ),
                      ),
                      const SizedBox(height: 24),
                      // Grid of workflow cards
                      Expanded(
                        child: GridView.builder(
                          padding: const EdgeInsets.only(bottom: 24),
                          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: MediaQuery.of(context).size.width < 600
                                ? 1
                                : (MediaQuery.of(context).size.width < 1000 ? 2 : 3),
                            mainAxisSpacing: 20,
                            crossAxisSpacing: 20,
                            childAspectRatio: MediaQuery.of(context).size.width < 600 ? 3.5 : 1.8,
                          ),
                          itemCount: workflows.length,
                          itemBuilder: (context, idx) {
                            final workflow = workflows[idx];
                            final currentState = _workflowStates[workflow.id] ?? 'In Progress';
                            return GestureDetector(
                              onTap: () => _showWorkflowDetail(workflow),
                              child: Container(
                                decoration: BoxDecoration(
                                  color: AppTheme.surfaceWhite,
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(color: AppTheme.borderGray, width: 1),
                                  boxShadow: [
                                    BoxShadow(
                                      color: Colors.black.withValues(alpha: 0.04),
                                      blurRadius: 8,
                                      offset: const Offset(0, 2),
                                    ),
                                  ],
                                ),
                                child: Padding(
                                  padding: EdgeInsets.all(MediaQuery.of(context).size.width < 600 ? 12 : 14),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    mainAxisAlignment: MainAxisAlignment.start,
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Text(
                                        workflow.position, 
                                        style: TextStyle(
                                          fontSize: MediaQuery.of(context).size.width < 600 ? 14 : 15, 
                                          fontWeight: FontWeight.w600,
                                          color: AppTheme.darkGray,
                                        ),
                                        maxLines: 2,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                      SizedBox(height: MediaQuery.of(context).size.width < 600 ? 4 : 5),
                                      Text(
                                        workflow.company, 
                                        style: TextStyle(
                                          fontSize: MediaQuery.of(context).size.width < 600 ? 12 : 13, 
                                          color: AppTheme.mediumGray
                                        ),
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                      SizedBox(height: MediaQuery.of(context).size.width < 600 ? 8 : 8),
                                      Container(
                                        padding: EdgeInsets.symmetric(
                                          horizontal: MediaQuery.of(context).size.width < 600 ? 8 : 10, 
                                          vertical: MediaQuery.of(context).size.width < 600 ? 3 : 4
                                        ),
                                        decoration: BoxDecoration(
                                          color: currentState == 'Complete' 
                                            ? AppTheme.borderGray 
                                            : AppTheme.lightBlue,
                                          borderRadius: BorderRadius.circular(6),
                                        ),
                                        child: Text(
                                          currentState,
                                          style: TextStyle(
                                            color: currentState == 'Complete' 
                                              ? AppTheme.mediumGray 
                                              : AppTheme.primaryBlue,
                                            fontWeight: FontWeight.w500,
                                            fontSize: MediaQuery.of(context).size.width < 600 ? 10 : 11,
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            );
                          },
                        ),
                      ),
                    ],
                  ),
          ),
        ),
      ],
    );
  }
} 