"""
Custom exceptions for PDF processing operations
"""


class PDFProcessingError(Exception):
    """Base exception for PDF processing errors"""
    def __init__(self, message: str = "PDF processing failed"):
        super().__init__(message)


class FileTooLargeError(PDFProcessingError):
    """Raised when file exceeds size limit"""
    def __init__(self, message: str = "File size exceeds limit"):
        super().__init__(message)


class InvalidFileTypeError(PDFProcessingError):
    """Raised when file type is not supported"""
    def __init__(self, message: str = "File type is not supported"):
        super().__init__(message)


class InvalidPDFError(PDFProcessingError):
    """Raised when PDF file is corrupted or invalid"""
    def __init__(self, message: str = "PDF file is corrupted or invalid"):
        super().__init__(message)


class EmptyPDFError(PDFProcessingError):
    """Raised when PDF file contains no extractable text"""
    def __init__(self, message: str = "PDF file is empty or contains no text"):
        super().__init__(message) 