from setuptools import setup, find_packages

setup(
    name="easy_rag_pipeline",
    version="0.1.5",
    packages=find_packages(),
    install_requires=[
        "langchain",
        "langchain-core",
        "langchain-openai",
        "langchain-community",
        "langchain-groq",
        "langchain-google-genai",
        "faiss-cpu",
        "pypdf",
        "tiktoken",
        "sentence-transformers",
        "pyyaml",
        "python-dotenv",
        "streamlit",
    ],
    author="Engr.Hamza",

    description="A reusable and configurable RAG (Retrieval-Augmented Generation) pipeline.",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    
)

