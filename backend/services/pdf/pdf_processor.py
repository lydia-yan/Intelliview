"""
PDF text extraction processor using PyMuPDF
"""

import asyncio
import time
from typing import Optional, Dict, Any
import fitz  # PyMuPDF
from fastapi import UploadFile

from backend.config import PDFConfig
from .file_validator import FileValidator
from .text_cleaner import TextCleaner
from .exceptions import (
    PDFProcessingError,
    EmptyPDFError,
    InvalidPDFError,
    FileTooLargeError
)


class PDFProcessor:
    """
    Core PDF processing class for text extraction
    """
    
    def __init__(self, config: PDFConfig = None):
        self.config = config or PDFConfig()
        self.validator = FileValidator(self.config)
        self.text_cleaner = TextCleaner(self.config)
    
    async def extract_text_from_upload(self, file: UploadFile) -> str:
        """
        Extract text from uploaded PDF file
        
        Args:
            file: FastAPI UploadFile object
            
        Returns:
            str: Extracted and cleaned text
        """
        # Validate file first
        await self.validator.validate_pdf_file(file)
        
        # Read file content
        pdf_bytes = await file.read()
        
        # Extract text from bytes
        return await self.extract_text_from_bytes(pdf_bytes)
    
    async def extract_text_from_bytes(self, pdf_bytes: bytes) -> str:
        """
        Extract text from PDF bytes data
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            str: Extracted and cleaned text
        """
        if not pdf_bytes:
            raise EmptyPDFError("PDF bytes data is empty")
        
        try:
            # Run text extraction in thread pool to avoid blocking
            extracted_text = await asyncio.get_event_loop().run_in_executor(
                None, self._extract_text_sync, pdf_bytes
            )
            
            # Clean the extracted text
            cleaned_text = self.text_cleaner.clean_extracted_text(extracted_text)
            
            # Basic validation using config
            if len(cleaned_text.strip()) < self.config.MIN_TEXT_LENGTH:
                raise EmptyPDFError(f"Extracted text is too short (less than {self.config.MIN_TEXT_LENGTH} characters)")
            
            return cleaned_text
            
        except Exception as e:
            if isinstance(e, PDFProcessingError):
                raise
            raise PDFProcessingError(f"Failed to extract text from PDF: {str(e)}")
    
    def _extract_text_sync(self, pdf_bytes: bytes) -> str:
        """
        Synchronous text extraction using PyMuPDF
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            str: Raw extracted text
        """
        doc = None
        try:
            # Open PDF from bytes
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            # Check document validity
            if doc.is_closed or doc.page_count == 0:
                raise InvalidPDFError("PDF document is empty or corrupted")
            
            # Check page count limit (prevent processing huge documents)
            if doc.page_count > self.config.MAX_PAGE_COUNT:
                raise FileTooLargeError(f"PDF has too many pages ({doc.page_count}). Maximum: {self.config.MAX_PAGE_COUNT}")
            
            extracted_text = ""
            
            # Extract text from each page
            for page_num in range(doc.page_count):
                try:
                    page = doc[page_num]
                    page_text = page.get_text()
                    
                    if page_text.strip():
                        extracted_text += page_text + "\n\n"
                        
                except Exception as e:
                    print(f"Warning: Failed to extract text from page {page_num + 1}: {e}")
                    continue
            
            if not extracted_text.strip():
                raise EmptyPDFError("No text could be extracted from the PDF")
            
            return extracted_text
            
        except Exception as e:
            if isinstance(e, PDFProcessingError):
                raise
            
            # Check for specific errors
            error_message = str(e).lower()
            if "password" in error_message or "encrypted" in error_message:
                raise InvalidPDFError("PDF is password protected")
            elif "damaged" in error_message or "corrupt" in error_message:
                raise InvalidPDFError("PDF file appears to be corrupted")
            else:
                raise PDFProcessingError(f"PyMuPDF extraction failed: {str(e)}")
                
        finally:
            # Always close the document
            if doc is not None:
                try:
                    doc.close()
                except:
                    pass
    
    async def process_resume_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        Process resume PDF file and return results
        
        Args:
            file: FastAPI UploadFile object
            
        Returns:
            dict: Processing results
        """
        start_time = time.time()
        
        try:
            # Extract text
            resume_text = await self.extract_text_from_upload(file)
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "resume_text": resume_text,
                "processing_time": processing_time,
                "error": None
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            return {
                "success": False,
                "resume_text": None,
                "processing_time": processing_time,
                "error": str(e)
            } 