from PyPDF2 import PdfReader
from docx import Document

def extract_text_from_pdf(cv_path):
    reader = PdfReader(cv_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(cv_path):
    doc = Document(cv_path)
    text = ''
    for para in doc.paragraphs:
        text += para.text
    return text
