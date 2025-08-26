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
    final media = MediaQuery.of(context);
    final width = media.size.width;
    final topInset = media.padding.top; // iOS notch/dynamic island safe area
    final horizontalPadding = width < 600 ? 16.0 : (width < 1024 ? 24.0 : 64.0);
    final isNarrow = width < 600;
    final baseHeight = isNarrow ? 44.0 : 72.0; // slightly taller on mobile

    return Container(
      height: topInset + baseHeight,
      decoration: BoxDecoration(
        // Use original white theme color
        color: AppTheme.surfaceWhite,
        border: Border(
          bottom: BorderSide(
            color: const Color(0xFFE0EAFF),
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
        // push content below the safe area; move text up a bit
        padding: EdgeInsets.only(
          top: topInset + (isNarrow ? -2.0 : 0.0),
          left: horizontalPadding,
          right: width < 600 ? horizontalPadding : 16.0, 
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,  
          children: [
            Expanded(
              child: Text(
                title,
                overflow: TextOverflow.ellipsis,
                maxLines: 1,
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.darkGray,
                ),
              ),
            ),
            if (actions != null)
              Flexible(
                child: SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(children: actions!),
                ),
              ),
          ],
        ),
      ),
    );
  }
} 