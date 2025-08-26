import 'package:flutter/material.dart';
import '../models/workflow.dart';
import '../services/workflow_service.dart';
import '../widgets/navbar.dart';
import '../theme/app_theme.dart';

class QAPage extends StatefulWidget {
  final String? preSelectedWorkflowId;
  
  const QAPage({super.key, this.preSelectedWorkflowId});

  @override
  State<QAPage> createState() => _QAPageState();
}

class _QAPageState extends State<QAPage> {
  final WorkflowService _workflowService = WorkflowService();
  
  List<Workflow> workflows = [];
  List<RecommendedQA> recommendedQAs = [];
  
  Workflow? selectedWorkflow;
  String mode = 'review'; // 'review' or 'quiz'
  
  bool _loadingWorkflows = true;
  bool _loadingQAs = false;
  String? _error;

  // expanded QA indexes
  final Set<int> _expandedQAIndexes = {};

  // selected tags
  final Set<String> _selectedTags = {};

  // tag filter collapsed state
  bool _isTagFilterCollapsed = false;

  // tag color mapping
  final Map<String, Color> _tagColors = {};
  final List<Color> _availableColors = [
    const Color(0xFFE6CFE6), 
    const Color(0xFFE1F5FE), 
    const Color(0xFFE8F5E8), 
    const Color(0xFFFFF3E0), 
    const Color(0xFFFCE4EC), 
    const Color(0xFFF3E5F5), 
    const Color(0xFFE0F2F1), 
    const Color(0xFFFFF8E1), 
    const Color(0xFFEFEBE9), 
    const Color(0xFFECEFF1), 
  ];

  // get tag color
  Color _getTagColor(String tag) {
    if (!_tagColors.containsKey(tag)) {
      final colorIndex = _tagColors.length % _availableColors.length;
      _tagColors[tag] = _availableColors[colorIndex];
    }
    return _tagColors[tag]!;
  }

  // get categorized tags
  Map<String, List<String>> _getCategorizedTags() {
    final allTags = <String>{};
    for (final qa in recommendedQAs) {
      allTags.addAll(qa.tags);
    }
    
    // Define tag categories and their order
    final questionTypes = ['Technical', 'Behavioral', 'Situational', 'CompanySpecific'];
    final coreSkills = [
      'Programming', 'SystemDesign', 'Database', 'Security', 'DevOps', 
      'Frontend', 'Backend', 'Mobile', 'DataScience', 'CloudComputing',
      'Strategy', 'Analytics', 'Marketing', 'Finance', 'ProjectManagement', 
      'ProductManagement', 'Leadership', 'Design', 'UXResearch',
      'Healthcare', 'Education', 'Engineering', 'Research'
    ];
    final experienceLevels = ['Entry', 'Mid', 'Senior'];
    
    return {
      'QuestionType': questionTypes.where((tag) => allTags.contains(tag)).toList(),
      'CoreSkill': coreSkills.where((tag) => allTags.contains(tag)).toList(),
      'DifficultyLevel': experienceLevels.where((tag) => allTags.contains(tag)).toList(),
    };
  }

  @override
  void initState() {
    super.initState();
    _loadWorkflows();
  }

  Future<void> _loadWorkflows() async {
    try {
      setState(() {
        _loadingWorkflows = true;
        _error = null;
      });
      
      final loadedWorkflows = await _workflowService.getWorkflows();
      
      setState(() {
        workflows = loadedWorkflows;
        _loadingWorkflows = false;
        
        // if there is a pre-selected workflow ID, set it as selected
        if (widget.preSelectedWorkflowId != null) {
          selectedWorkflow = workflows.where((w) => w.id == widget.preSelectedWorkflowId).firstOrNull;
          if (selectedWorkflow != null) {
            _loadQAs();
          }
        }
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loadingWorkflows = false;
      });
    }
  }

  Future<void> _loadQAs() async {
    if (selectedWorkflow == null) return;
    
    try {
      setState(() {
        _loadingQAs = true;
      });
      
      final qas = await _workflowService.getRecommendedQAs(selectedWorkflow!.id);
      
      setState(() {
        recommendedQAs = qas;
        _loadingQAs = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loadingQAs = false;
      });
    }
  }

  void _onWorkflowSelected(Workflow workflow) {
    setState(() {
      selectedWorkflow = workflow;
      recommendedQAs = [];
    });
    _loadQAs();
  }

  @override
  Widget build(BuildContext context) {
    if (_loadingWorkflows) {
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
        NavBar(
          title: 'Q&A',
        ),
        
        // Main content
        Expanded(
          child: Padding(
            padding: EdgeInsets.symmetric(
              horizontal: MediaQuery.of(context).size.width < 600 ? 16.0 : 64.0, 
              vertical: 32.0
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Workflow selector
                if (workflows.isNotEmpty) _buildWorkflowPopupSelector(),
                const SizedBox(height: 16),
                // mode switch tab
                _buildModeTab(),
                const SizedBox(height: 16),
                // tag filter
                if (recommendedQAs.isNotEmpty) _buildTagFilter(),
                const SizedBox(height: 16),
                // content area
                Expanded(
                  child: _buildRecommendedQAs(),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildWorkflowPopupSelector() {
    return Align(
      alignment: Alignment.centerLeft,
      child: ConstrainedBox(
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width < 600 ? double.infinity : 300
        ),
        child: PopupMenuButton<Workflow>(
          onSelected: (workflow) {
            _onWorkflowSelected(workflow);
          },
          color: AppTheme.surfaceWhite,
          elevation: 8,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(color: AppTheme.borderGray),
          ),
          itemBuilder: (context) => workflows.map((workflow) {
            return PopupMenuItem<Workflow>(
              value: workflow,
              child: Text(
                '${workflow.company} - ${workflow.position}',
                style: TextStyle(fontSize: 14, color: AppTheme.darkGray),
                overflow: TextOverflow.ellipsis,
              ),
            );
          }).toList(),
          child: Container(
            height: 36,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            decoration: BoxDecoration(
              border: Border.all(color: AppTheme.borderGray, width: 1.5),
              borderRadius: BorderRadius.circular(8),
              color: AppTheme.surfaceWhite,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.05),
                  blurRadius: 4,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Expanded(
                  child: Text(
                    selectedWorkflow == null
                        ? 'Select a workflow'
                        : '${selectedWorkflow!.company} - ${selectedWorkflow!.position}',
                    style: TextStyle(
                      fontSize: 14,
                      color: selectedWorkflow == null ? AppTheme.mediumGray : AppTheme.darkGray,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Icon(Icons.keyboard_arrow_down, size: 18, color: AppTheme.darkGray),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildModeTab() {
    return Row(
      children: [
        _buildModeButton('Review Mode', 'review'),
        SizedBox(width: MediaQuery.of(context).size.width < 600 ? 8 : 12),
        _buildModeButton('Quiz Mode', 'quiz'),
      ],
    );
  }

  Widget _buildModeButton(String title, String value) {
    final isSelected = mode == value;
    return GestureDetector(
      onTap: () {
        setState(() {
          mode = value;
          _expandedQAIndexes.clear();
        });
      },
      child: Container(
        padding: EdgeInsets.symmetric(
          horizontal: MediaQuery.of(context).size.width < 600 ? 14 : 18, 
          vertical: MediaQuery.of(context).size.width < 600 ? 6 : 8
        ),
        decoration: BoxDecoration(
          color: isSelected ? AppTheme.lightBlue : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isSelected ? const Color.fromARGB(255, 202, 214, 243) : Colors.grey[300]!,
          ),
        ),
        child: Text(
          title,
          style: TextStyle(
            color: isSelected ? const Color.fromARGB(255, 72, 74, 77) : Colors.grey[600],
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
          ),
        ),
      ),
    );
  }

  Widget _buildTagFilter() {
    final categorizedTags = _getCategorizedTags();
    if (categorizedTags.values.every((tags) => tags.isEmpty)) return const SizedBox.shrink();
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        MediaQuery.of(context).size.width < 600
            ? Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(
                        'Filter by tags:', 
                        style: TextStyle(
                          fontSize: MediaQuery.of(context).size.width < 600 ? 13 : 14, 
                          fontWeight: FontWeight.w500
                        )
                      ),
                      const Spacer(),
                      TextButton.icon(
                        onPressed: () {
                          setState(() {
                            _isTagFilterCollapsed = !_isTagFilterCollapsed;
                          });
                        },
                        icon: Icon(
                          _isTagFilterCollapsed ? Icons.keyboard_arrow_down : Icons.keyboard_arrow_up,
                          size: 16,
                        ),
                        label: Text(
                          _isTagFilterCollapsed ? 'Expand' : 'Collapse',
                          style: const TextStyle(fontSize: 12),
                        ),
                      ),
                    ],
                  ),
                  if (_selectedTags.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Align(
                      alignment: Alignment.centerLeft,
                      child: TextButton(
                        onPressed: () {
                          setState(() {
                            _selectedTags.clear();
                          });
                        },
                        child: const Text('Clear all', style: TextStyle(fontSize: 12)),
                      ),
                    ),
                  ],
                ],
              )
            : Row(
                children: [
                  Text(
                    'Filter by tags:', 
                    style: TextStyle(
                      fontSize: 14, 
                      fontWeight: FontWeight.w500
                    )
                  ),
                  const SizedBox(width: 8),
                  if (_selectedTags.isNotEmpty)
                    TextButton(
                      onPressed: () {
                        setState(() {
                          _selectedTags.clear();
                        });
                      },
                      child: const Text('Clear all', style: TextStyle(fontSize: 12)),
                    ),
                  const Spacer(),
                  TextButton.icon(
                    onPressed: () {
                      setState(() {
                        _isTagFilterCollapsed = !_isTagFilterCollapsed;
                      });
                    },
                    icon: Icon(
                      _isTagFilterCollapsed ? Icons.keyboard_arrow_down : Icons.keyboard_arrow_up,
                      size: 16,
                    ),
                    label: Text(
                      _isTagFilterCollapsed ? 'Expand' : 'Collapse',
                      style: const TextStyle(fontSize: 12),
                    ),
                  ),
                ],
              ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey[300]!),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Always show QuestionType row
              _buildTagRow('Question Type', categorizedTags['QuestionType'] ?? []),
              
              // Show CoreSkill and DifficultyLevel only when expanded
              if (!_isTagFilterCollapsed) ...[
                if (categorizedTags['CoreSkill']?.isNotEmpty ?? false) ...[
                  const SizedBox(height: 8),
                  _buildTagRow('Core Skill', categorizedTags['CoreSkill']!),
                ],
                if (categorizedTags['DifficultyLevel']?.isNotEmpty ?? false) ...[
                  const SizedBox(height: 8),
                  _buildTagRow('Difficulty Level', categorizedTags['DifficultyLevel']!),
                ],
              ],
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildTagRow(String categoryName, List<String> tags) {
    if (tags.isEmpty) return const SizedBox.shrink();
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          categoryName,
          style: TextStyle(
            fontSize: MediaQuery.of(context).size.width < 600 ? 11 : 12,
            fontWeight: FontWeight.w600,
            color: const Color(0xFF555555),
          ),
        ),
        const SizedBox(height: 4),
        Wrap(
          spacing: 6,
          runSpacing: 4,
          children: tags.map((tag) {
            final isSelected = _selectedTags.contains(tag);
            return GestureDetector(
              onTap: () {
                setState(() {
                  if (isSelected) {
                    _selectedTags.remove(tag);
                  } else {
                    _selectedTags.add(tag);
                  }
                });
              },
              child: Chip(
                label: Text(tag),
                backgroundColor: isSelected ? _getTagColor(tag) : Colors.grey[100],
                labelStyle: TextStyle(
                  fontSize: 11, 
                  color: isSelected ? const Color(0xFF263238) : Colors.grey[600],
                  fontWeight: isSelected ? FontWeight.w500 : FontWeight.normal,
                ),
                shape: StadiumBorder(
                  side: BorderSide(
                    color: isSelected ? Colors.transparent : Colors.grey[300]!,
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildRecommendedQAs() {
    if (selectedWorkflow == null) {
      return const Center(
        child: Text('Please select a workflow to view recommended Q&A'),
      );
    }

    if (_loadingQAs) {
      return const Center(child: CircularProgressIndicator());
    }

    if (recommendedQAs.isEmpty) {
      return const Center(
        child: Text('No recommended Q&A available for this workflow'),
      );
    }

    final filteredQAs = _getFilteredQAs();
    
    if (filteredQAs.isEmpty && _selectedTags.isNotEmpty) {
      return const Center(
        child: Text('No Q&A found matching the selected tags'),
      );
    }

    return ListView.builder(
      padding: EdgeInsets.zero,  
      itemCount: filteredQAs.length,
      itemBuilder: (context, index) {
        final qa = filteredQAs[index];
        // need to use original index to manage expanded state
        final originalIndex = recommendedQAs.indexOf(qa);
        final isExpanded = _expandedQAIndexes.contains(originalIndex);
        return Card(
          color: Colors.white,
          elevation: 4,
          margin: const EdgeInsets.only(bottom: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(color: AppTheme.borderGray, width: 1.5),
          ),
          shadowColor: Colors.black.withValues(alpha: 0.1),
          child: Padding(
            padding: EdgeInsets.all(MediaQuery.of(context).size.width < 600 ? 16 : 20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (qa.tags.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Wrap(
                      spacing: 8,
                      children: qa.tags.map((tag) {
                        return Chip(
                          label: Text(tag),
                          backgroundColor: _getTagColor(tag),
                          labelStyle: const TextStyle(fontSize: 12, color: Color(0xFF263238)),
                          shape: StadiumBorder(side: BorderSide(color: Colors.transparent)),
                        );
                      }).toList(),
                    ),
                  ),
                Text(
                  qa.question,
                  style: TextStyle(
                    fontSize: MediaQuery.of(context).size.width < 600 ? 15 : 16, 
                    fontWeight: FontWeight.bold
                  ),
                ),
                if (mode == 'review' || isExpanded) ...[
                  const SizedBox(height: 8),
                  Text(
                    qa.answer,
                    style: TextStyle(
                      fontSize: MediaQuery.of(context).size.width < 600 ? 13 : 14, 
                      color: Colors.black87
                    ),
                  ),
                  if (mode == 'quiz' && isExpanded) ...[
                    const SizedBox(height: 8),
                    TextButton.icon(
                      onPressed: () {
                        setState(() {
                          _expandedQAIndexes.remove(originalIndex);
                        });
                      },
                      icon: const Icon(Icons.keyboard_arrow_up_rounded),
                      label: const Text(
                        'Hide Answer',
                        style: TextStyle(fontWeight: FontWeight.normal),
                      ),
                      style: TextButton.styleFrom(
                        foregroundColor: const Color.fromARGB(255, 97, 97, 97),
                      ),
                    ),
                  ],
                ] else ...[
                  const SizedBox(height: 8),
                  TextButton.icon(
                    onPressed: () {
                      setState(() {
                        _expandedQAIndexes.add(originalIndex);
                      });
                    },
                    icon: const Icon(Icons.keyboard_arrow_down_rounded),
                    label: const Text(
                      'Show Answer',
                      style: TextStyle(fontWeight: FontWeight.normal),
                    ),
                    style: TextButton.styleFrom(
                      foregroundColor: const Color.fromARGB(255, 91, 90, 90),
                    ),
                  ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  // filter QA list
  List<RecommendedQA> _getFilteredQAs() {
    if (_selectedTags.isEmpty) {
      return recommendedQAs;
    }
    return recommendedQAs.where((qa) {
      return qa.tags.any((tag) => _selectedTags.contains(tag));
    }).toList();
  }
} 