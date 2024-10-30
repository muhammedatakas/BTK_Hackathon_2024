import os
from langchain_community.document_loaders import PyMuPDFLoader

def get_pdf_content(pdf_path: str) -> str:
    pdf_path = os.path.normpath(pdf_path)  # Normalize the path
    pdf_path = pdf_path.replace("\\", "/")  # Replace backslashes with forward slashes
    if not os.path.isfile(pdf_path):
        raise ValueError(f"File path {pdf_path} does not exist or is not a valid file.")
    loader = PyMuPDFLoader(pdf_path)
    docs = loader.load()
    content = ""
    for doc in docs:
        content += doc.page_content
    return content

