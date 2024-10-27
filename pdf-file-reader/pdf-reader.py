from langchain_community.document_loaders import PyMuPDFLoader
def get_pdf_content(pdf_path: str) -> str:  
    loader = PyMuPDFLoader(pdf_path)
    docs = loader.load()
    content = ""
    for doc in docs:
        content += doc.page_content
    return content
