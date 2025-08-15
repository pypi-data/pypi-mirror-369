from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader, TextLoader

def load_pdf(file_path: str):
    """Loads a PDF file and returns a list of documents."""
    loader = PyPDFLoader(file_path)
    return loader.load()

def load_website(url: str):
    """Loads content from a website and returns a list of documents."""
    loader = WebBaseLoader(url)
    return loader.load()

def load_text(file_path: str):
    """Loads a text file and returns a list of documents."""
    loader = TextLoader(file_path)
    return loader.load()

def chunk_documents(docs: list, chunk_size: int = 500, chunk_overlap: int = 50):
    """
    Chunks a list of documents into smaller pieces.

    Args:
        docs (list): A list of documents to be chunked.
        chunk_size (int): The maximum size of each chunk (in characters).
        chunk_overlap (int): The number of characters to overlap between chunks.

    Returns:
        list: A list of chunked documents.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(docs)
