import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // color scheme
  static const Color primaryBlue = Color(0xFF2563EB);      
  static const Color lightBlue = Color(0xFFE6F0FF);        
  static const Color darkGray = Color(0xFF1F2937);        
  static const Color mediumGray = Color(0xFF6B7280);      
  static const Color lightGray = Color(0xFFF9FAFB);       
  static const Color borderGray = Color(0xFFE5E7EB);       
  static const Color surfaceWhite = Color(0xFFFFFFFF);    

  static ThemeData get lightTheme => ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: primaryBlue,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        scaffoldBackgroundColor: lightGray,
        textTheme: GoogleFonts.notoSansTextTheme().apply(
          bodyColor: darkGray,
          displayColor: darkGray,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: surfaceWhite,
          foregroundColor: darkGray,
          elevation: 0,
        ),
        cardTheme: const CardThemeData(
          color: surfaceWhite,
          elevation: 2,
          shadowColor: Colors.black12,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(12)),
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: primaryBlue,
            foregroundColor: surfaceWhite,
            elevation: 2,
            shadowColor: primaryBlue.withValues(alpha: 0.3),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
      );
} 