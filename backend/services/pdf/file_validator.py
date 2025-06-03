"""
File validation utilities for PDF processing
"""

from typing import Optional
from fastapi import UploadFile
from backend.config import PDFConfig
from .exceptions import (
    FileTooLargeError,
    InvalidFileTypeError,
    InvalidPDFError
)


class FileValidator:
    """
    File validation utility using PDFConfig
    """
    
    def __init__(self, config: PDFConfig = None):
        self.config = config or PDFConfig()
    
    async def validate_pdf_file(self, file: UploadFile) -> bool:
        """
        Validate uploaded PDF file
        
        Args:
            file: FastAPI UploadFile object
            
        Returns:
            bool: True if file is valid
        """
        # Check file size
        await self._validate_file_size(file)
        
        # Check file extension
        self._validate_file_extension(file.filename)
        
        # Basic PDF content validation
        await self._validate_pdf_content(file)
        
        return True
    
    async def _validate_file_size(self, file: UploadFile) -> None:
        """Validate file size"""
        if hasattr(file, 'size') and file.size:
            if file.size > self.config.MAX_FILE_SIZE:
                max_size_mb = self.config.MAX_FILE_SIZE / (1024*1024)
                raise FileTooLargeError(f"File size exceeds {max_size_mb:.1f}MB limit")
        else:
            # Read content to check size
            content = await file.read()
            if len(content) > self.config.MAX_FILE_SIZE:
                max_size_mb = self.config.MAX_FILE_SIZE / (1024*1024)
                raise FileTooLargeError(f"File size exceeds {max_size_mb:.1f}MB limit")
            # Reset file pointer
            await file.seek(0)
    
    def _validate_file_extension(self, filename: Optional[str]) -> None:
        """Validate file extension"""
        if not filename:
            raise InvalidFileTypeError("Filename is required")
        
        file_ext = '.' + filename.lower().split('.')[-1] if '.' in filename else ''
        
        if file_ext not in self.config.ALLOWED_EXTENSIONS:
            allowed = ', '.join(self.config.ALLOWED_EXTENSIONS)
            raise InvalidFileTypeError(f"Only {allowed} files are supported, got: {file_ext}")
    
    async def _validate_pdf_content(self, file: UploadFile) -> None:
        """Basic PDF content validation"""
        try:
            # Read first few bytes to check PDF signature
            content_sample = await file.read(8)
            await file.seek(0)  # Reset file pointer
            
            # Check PDF magic number
            if not content_sample.startswith(b'%PDF-'):
                raise InvalidPDFError("File does not appear to be a valid PDF")
                
        except Exception as e:
            if isinstance(e, InvalidPDFError):
                raise
            # If validation fails, continue gracefully
            pass

    def get_file_info(self, file: UploadFile) -> dict:
        """
        Get basic file information
        
        Args:
            file: FastAPI UploadFile object
            
        Returns:
            dict: File information
        """
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": getattr(file, 'size', None),
            "max_allowed_size": self.config.MAX_FILE_SIZE,
            "allowed_extensions": list(self.config.ALLOWED_EXTENSIONS)
        } 