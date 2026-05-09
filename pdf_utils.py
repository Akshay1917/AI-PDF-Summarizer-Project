import pdfplumber
import re

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file and returns it as a string.
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None
    
    return clean_text(text)

def clean_text(text):
    """
    Basic text cleaning to remove extra whitespaces and special characters.
    """
    if not text:
        return ""
    
    # Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text)
    # Remove multiple newlines
    text = re.sub(r'\n+', '\n', text)
    
    return text.strip()
