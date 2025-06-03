import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class NavBar extends StatelessWidget {
  final String title;
  final Color? backgroundColor;
  final List<Widget>? actions;

  const NavBar({
    super.key,
    required this.title,
    this.backgroundColor,
    this.actions,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 72,
      decoration: BoxDecoration(
        color: AppTheme.surfaceWhite,
        border: Border(
          bottom: BorderSide(
            color: AppTheme.borderGray,
            width: 1,
          ),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 2,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 64.0),
        child: Row(
          children: [
            Text(
              title,
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: AppTheme.darkGray,
              ),
            ),
            const Spacer(),
            if (actions != null) ...actions!,
          ],
        ),
      ),
    );
  }
} 