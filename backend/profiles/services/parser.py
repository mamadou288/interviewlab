import os
from django.core.exceptions import ValidationError
from django.conf import settings
import pdfplumber
from docx import Document


def validate_file(file):
    """
    Validate file type and size.
    
    Args:
        file: Django UploadedFile object
        
    Raises:
        ValidationError: If file is invalid
    """
    # Check file size
    if file.size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(
            f'File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024 * 1024)}MB'
        )
    
    # Check file type
    content_type = getattr(file, 'content_type', '')
    if content_type not in settings.ALLOWED_FILE_TYPES:
        raise ValidationError(
            f'File type {content_type} is not allowed. Allowed types: PDF, DOCX'
        )
    
    # Check file extension as additional validation
    file_name = file.name.lower()
    if not (file_name.endswith('.pdf') or file_name.endswith('.docx')):
        raise ValidationError('File must be a PDF or DOCX file')


def extract_text_pdf(file_path):
    """
    Extract text from PDF file using pdfplumber.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        str: Extracted text
    """
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise ValidationError(f'Error extracting text from PDF: {str(e)}')


def extract_text_docx(file_path):
    """
    Extract text from DOCX file using python-docx.
    
    Args:
        file_path: Path to DOCX file
        
    Returns:
        str: Extracted text
    """
    try:
        doc = Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text)
        return "\n".join(text)
    except Exception as e:
        raise ValidationError(f'Error extracting text from DOCX: {str(e)}')


def extract_text(file):
    """
    Main function that routes to PDF or DOCX extraction based on mime type.
    
    Args:
        file: Django UploadedFile object
        
    Returns:
        str: Extracted text
    """
    # Save file temporarily to extract text
    file_path = None
    try:
        # Create temporary file
        import tempfile
        suffix = '.pdf' if file.name.lower().endswith('.pdf') else '.docx'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            for chunk in file.chunks():
                tmp_file.write(chunk)
            file_path = tmp_file.name
        
        # Reset file pointer
        file.seek(0)
        
        # Extract text based on file type
        content_type = getattr(file, 'content_type', '')
        if 'pdf' in content_type or file.name.lower().endswith('.pdf'):
            return extract_text_pdf(file_path)
        elif 'wordprocessingml' in content_type or file.name.lower().endswith('.docx'):
            return extract_text_docx(file_path)
        else:
            raise ValidationError('Unsupported file type for text extraction')
    finally:
        # Clean up temporary file
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

