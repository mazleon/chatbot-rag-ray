import logging
from typing import List, Optional
from app.core.config import get_settings

logger = logging.getLogger(__name__)


def parse_pdf(file_bytes: bytes) -> str:
    try:
        import PyPDF2
        from io import BytesIO
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except ImportError:
        logger.warning("PyPDF2 not installed, falling back to text extraction")
        return file_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        logger.error(f"PDF parsing error: {e}")
        return file_bytes.decode('utf-8', errors='ignore')


def parse_docx(file_bytes: bytes) -> str:
    try:
        from docx import Document
        from io import BytesIO
        doc = Document(BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except ImportError:
        logger.warning("python-docx not installed, cannot parse DOCX")
        return ""
    except Exception as e:
        logger.error(f"DOCX parsing error: {e}")
        return ""


def parse_txt(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        logger.error(f"TXT parsing error: {e}")
        return ""


def parse_markdown(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        logger.error(f"Markdown parsing error: {e}")
        return ""


def parse_file(content: bytes, filename: str) -> Optional[str]:
    ext = filename.lower().split('.')[-1]
    
    parsers = {
        'pdf': parse_pdf,
        'docx': parse_docx,
        'doc': parse_docx,
        'txt': parse_txt,
        'md': parse_markdown,
        'markdown': parse_markdown,
    }
    
    parser = parsers.get(ext)
    if not parser:
        logger.warning(f"Unsupported file type: {ext}")
        return None
    
    try:
        text = parser(content)
        if not text or not text.strip():
            logger.warning(f"No text extracted from {filename}")
            return None
        return text
    except Exception as e:
        logger.error(f"Error parsing {filename}: {e}")
        return None
