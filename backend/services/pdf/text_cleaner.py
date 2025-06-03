"""
Simple text cleaning utilities for PDF text extraction
"""

import re
from backend.config import PDFConfig


class TextCleaner:
    """
    Simple utility class for basic text cleaning
    """
    
    def __init__(self, config: PDFConfig = None):
        self.config = config or PDFConfig()
    
    def clean_extracted_text(self, raw_text: str) -> str:
        """
        Clean and normalize extracted PDF text
        
        Args:
            raw_text: Raw text extracted from PDF
            
        Returns:
            str: Cleaned text
        """
        if not raw_text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', raw_text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Replace multiple newlines with single newlines
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        
        return text
    
    def analyze_text_quality(self, text: str) -> dict:
        """
        Basic text quality check using configuration thresholds
        
        Args:
            text: Text to analyze
            
        Returns:
            dict: Basic quality metrics
        """
        if not text:
            return {
                "character_count": 0,
                "word_count": 0,
                "is_valid": False,
                "issues": ["Empty text"]
            }
        
        char_count = len(text)
        word_count = len(text.split())
        is_valid = (char_count >= self.config.MIN_TEXT_QUALITY_CHARS and 
                   word_count >= self.config.MIN_TEXT_QUALITY_WORDS)
        
        issues = []
        if char_count < self.config.MIN_TEXT_QUALITY_CHARS:
            issues.append(f"Text too short (less than {self.config.MIN_TEXT_QUALITY_CHARS} characters)")
        if word_count < self.config.MIN_TEXT_QUALITY_WORDS:
            issues.append(f"Too few words (less than {self.config.MIN_TEXT_QUALITY_WORDS} words)")
        
        return {
            "character_count": char_count,
            "word_count": word_count,
            "is_valid": is_valid,
            "issues": issues,
            "min_chars_required": self.config.MIN_TEXT_QUALITY_CHARS,
            "min_words_required": self.config.MIN_TEXT_QUALITY_WORDS
        } 