# easy-rag-pipeline

A simple, flexible, and production-ready Retrieval-Augmented Generation (RAG) pipeline for Python. Supports OpenAI, Groq, OpenRouter, Gemini, and HuggingFace models for both LLM and embeddings. Built for easy integration and rapid prototyping.

**Maintainer & Author:** Engr. Hamza

---

## Features
- Plug-and-play RAG pipeline for text, PDF, and web sources
- Supports OpenAI, Groq, OpenRouter, Gemini, and HuggingFace
- FAISS vector store for fast retrieval
- Easy configuration via YAML
- High-level utility functions for quick usage
- Modular: index once, query many times

---

## Installation

```bash
pip install easy-rag-pipeline
```

---

## Quickstart Example

### 1. Basic RAG from a file
```python
from easy_rag_pipeline.api import rag_from_file

answer = rag_from_file(
              query="What is Retrieval-Augmented Generation (RAG)?",
              file_path="examples/sample_document.txt",
              config_path="examples/config.yaml"
)
print(answer)
```

### 2. RAG from a website
```python
from easy_rag_pipeline.api import rag_from_url

answer = rag_from_url(
              query="What is RAG?",
              url="https://en.wikipedia.org/wiki/Retrieval-augmented_generation",
              config_path="examples/config.yaml"
)
print(answer)
```

### 3. RAG from a string of text
```python
from easy_rag_pipeline.api import rag_from_text

answer = rag_from_text(
              query="What is RAG?",
              text="Retrieval-Augmented Generation (RAG) is a technique...",
              config_path="examples/config.yaml"
)
print(answer)
```

### 4. Index a file and save the vector store
```python
from easy_rag_pipeline.api import index_file

index_file(
              file_path="examples/sample_document.txt",
              config_path="examples/config.yaml",
              save_path="vector_store"
)
```

### 5. Load a saved index and query it
```python
from easy_rag_pipeline.api import load_index_and_query

answer = load_index_and_query(
              query="What is RAG?",
              index_path="vector_store",
              config_path="examples/config.yaml"
)
print(answer)
```

---

## Configuration

Edit `examples/config.yaml` to set your LLM, embedding, and vector store providers. Example:

```yaml
llm:
       provider: "groq"  # or "openai", "openrouter", "gemini"
       model: "llama3-8b-8192"
       temperature: 0.7
embedding:
       provider: "huggingface"  # or "openai", "groq", "openrouter"
       model: "sentence-transformers/all-MiniLM-L6-v2"
vector_store:
       provider: "faiss"
chunking:
       chunk_size: 1000
       chunk_overlap: 100
retrieval:
       k: 5
```

---

## API Reference

### High-level utility functions (in `easy_rag_pipeline.api`):
- `rag_from_file(query, file_path, config_path)`
- `rag_from_url(query, url, config_path)`
- `rag_from_text(query, text, config_path)`
- `index_file(file_path, config_path, save_path)`
- `load_index_and_query(query, index_path, config_path)`

### Advanced usage
You can use the lower-level pipeline functions for more control:
```python
from easy_rag_pipeline.pipeline import create_and_persist_vector_store, query_rag_pipeline, simple_rag_pipeline
```

---

## Supported Providers
- **OpenAI**: GPT-3.5, GPT-4, text-embedding-ada-002, etc.
- **Groq**: Llama3, Mixtral, and more
- **OpenRouter**: Claude, Llama, and more (OpenAI-compatible API)
- **Gemini**: Google Gemini models
- **HuggingFace**: Local and hosted embedding models

---


## Setting API Keys

You can provide API keys in two ways:

### 1. Using a `.env` file (recommended)
Create a `.env` file in your project root:
```
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk-...
GOOGLE_API_KEY=...  # for Gemini
OPENROUTER_API_KEY=...  # for OpenRouter
```
The pipeline will automatically load these using `python-dotenv` if installed.

### 2. Setting API keys in your code
You can set the API key directly in your config dictionary before running the pipeline:
```python
config = load_config("examples/config.yaml")
config['llm']['api_key'] = "sk-..."  # or your GROQ/OPENROUTER key
config['embedding']['api_key'] = "sk-..."  # if needed for embeddings
answer = rag_from_file(
       query="What is RAG?",
       file_path="examples/sample_document.txt",
       config_path="examples/config.yaml"
)
```
Or set the environment variable in your script:
```python
import os
os.environ["OPENAI_API_KEY"] = "sk-..."
os.environ["GROQ_API_KEY"] = "gsk-..."
```
This will be picked up automatically by the pipeline.

---

## License
MIT

---

## Maintainer
Engr. Hamza


**A flexible, configurable, and easy-to-use Retrieval-Augmented Generation (RAG) pipeline in a box.**

</div>
set PYTHONUTF8=1

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/easy-rag-pipeline.svg)](https://pypi.org/project/easy-rag-pipeline/)
[![Build Status](https://img.shields.io/travis/com/your-username/easy_rag_pipeline.svg)](https://travis-ci.com/your-username/easy_rag_pipeline)

</div>

---

**Easy RAG Pipeline** is a production-grade framework for building and deploying RAG applications. It handles the entire workflow from document ingestion to answer generation, allowing you to plug in different LLMs, embedding models, and vector stores with a simple, configuration-driven setup.

## ✨ Key Features

- **🔌 Pluggable Architecture**: Easily switch between LLMs (**OpenAI, Groq, Gemini, OpenRouter**), embedding models (**OpenAI, HuggingFace**), and vector stores (**FAISS**).
- **⚙️ Configuration-Driven**: No hard-coding. Manage all your settings—from chunk sizes to model names—through a single `config.yaml` file.
- **🚀 Efficient & Practical**: Includes two pipeline modes: a simple all-in-one for quick demos, and an advanced two-step process (index then query) for production efficiency.
- **📚 Multi-Format Ingestion**: Out-of-the-box support for loading documents from PDFs, text files, and websites.
- **📦 Ready-to-Use**: Comes with a CLI example and an interactive Streamlit demo to get you started in minutes.
- **🔧 Extensible by Design**: Clean, modular code that's easy to extend with your own custom components.

## 🏗️ Architecture

The pipeline follows a standard, modular RAG architecture that is easy to understand and build upon.

```
[Source Document: PDF, TXT, URL]
             |
             v
      [1. Ingest & Load]
             |
             v
      [2. Chunk Documents]
             |
             v
      [3. Generate Embeddings]  <-- (Pluggable: OpenAI, HuggingFace)
             |
             v
      [4. Store in Vector DB]   <-- (Pluggable: FAISS)
             |
             +-----------------------+
             |                       |
             v                       v
[User Query] -> [5. Retrieve Docs]  [Vector Database]
             |
             v
[Retrieved Context + Query]
             |
             v
      [6. Generate Answer]      <-- (Pluggable: OpenAI, Groq, Gemini)
             |
             v
         [Answer]
```

## 🚀 Getting Started


python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install all required dependencies.

```bash
pip install -r requirements.txt
```

Finally, install the package in editable mode, which allows you to modify the code and see changes instantly.

```bash
pip install -e .
```

### 2. Configuration

This project is managed by a central configuration file and environment variables for your secrets.

**a. Set up API Keys:**

Copy the example environment file and add your secret API keys. The pipeline will automatically load the correct key based on the provider you choose in `config.yaml`.

```bash
cp .env.example .env
```
Now, edit `.env` and add your keys:
```
# For OpenAI
OPENAI_API_KEY="sk-..."

# For Groq
GROQ_API_KEY="gsk_..."

# For Google Gemini
GOOGLE_API_KEY="AIzaSy..."

# For OpenRouter
OPENROUTER_API_KEY="sk-or-..."
```

**b. Select your Components:**

Open `examples/config.yaml` to select the models and components you want to use. For example, to switch to Groq's Llama3 model:

```yaml
# examples/config.yaml

llm:
  provider: "groq"
  model: "llama3-8b-8192"
  temperature: 0.7
```

### 3. Run the Demo

You can test the pipeline with either the basic CLI example or the interactive Streamlit app.

**a. Basic CLI Example:**

This script will run the simple, all-in-one pipeline on the included sample document.

```bash
python examples/basic_rag.py
```

**b. Interactive Streamlit Demo:**

For a more visual experience, launch the Streamlit app.

```bash
streamlit run examples/streamlit_demo.py
```
This will open the demo in your web browser.

## ⚙️ Advanced Usage

For production scenarios, re-indexing your documents on every query is inefficient. The library provides a two-step process for this:

1.  **Index Your Data**: Run a script to process and store your documents in a persistent vector store.
2.  **Query the Store**: Run your application to load the pre-indexed store and query it repeatedly.

<details>
<summary>Click to see an example of the advanced workflow</summary>

```python
# script_to_index.py
from easy_rag_pipeline import create_and_persist_vector_store, load_config

# Load config
config = load_config("examples/config.yaml")

# Create and save a FAISS vector store from a PDF
create_and_persist_vector_store(
    source_path="path/to/my_document.pdf",
    source_type="pdf",
    config=config,
    save_path="my_vector_store"
)

# --------------------------------------------------

# script_to_query.py
from easy_rag_pipeline import query_rag_pipeline, load_config
from langchain_community.vectorstores import FAISS
from easy_rag_pipeline.embed import get_embedding_function

# Load config and embedding function
config = load_config("examples/config.yaml")
embedding_function = get_embedding_function(config['embedding'])

# Load the persisted vector store
vector_store = FAISS.load_local("my_vector_store", embedding_function, allow_dangerous_deserialization=True)

# Query the pipeline
query = "What was the main finding of the document?"
answer = query_rag_pipeline(query, vector_store, config)
print(answer)
```

</details>

## 🔧 Extensibility

The library is designed to be easily extended.

-   **To add a new LLM**:
    1.  Install the required package (e.g., `pip install langchain-anthropic`).
    2.  Add an `elif provider == "anthropic":` block in `easy_rag_pipeline/generate.py`.
    3.  Update `config.py` to load the `ANTHROPIC_API_KEY`.
-   **To add a new Document Loader**:
    1.  Add the loader function (e.g., `load_docx`) in `easy_rag_pipeline/ingest.py`.
    2.  Update the `pipeline.py` functions to accept the new `source_type`.

## 🗺️ Roadmap

This project is under active development. Future enhancements include:

- [ ] Support for more vector databases (Chroma, Pinecone, Weaviate).
- [ ] Asynchronous pipeline for improved performance.
- [ ] Hybrid retrieval combining keyword search (BM25) and semantic search.
- [ ] Support for image and multi-modal RAG.
- [ ] Integration with RAG evaluation frameworks.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss your ideas.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Elysia agent (optional)

If you want agentic behavior (decision trees, tool selection) you can register the pipeline's retrieve/generate tools with an Elysia Tree.

```python
from easy_rag_pipeline import create_elysia_tree, create_and_persist_vector_store, load_config

cfg = load_config('examples/config.yaml')
vs = create_and_persist_vector_store(cfg.get('source_path', 'examples/sample_document.txt'), cfg.get('source_type','txt'), cfg)

try:
       tree = create_elysia_tree(vectorstore=vs, register_tools=True)
except ImportError:
       raise SystemExit('Install elysia-ai to use the agent: pip install elysia-ai')

resp, objs = tree('Summarize the document and cite sources')
print(resp)
```

Elysia remains optional — the code uses lazy imports so your package doesn't require `elysia-ai` unless you run the agent.

## RAG-Anything adapter (optional)

If you use the RAG-Anything project for richer, multimodal parsing, the package includes a lightweight adapter that converts RAG-Anything nodes into `Document`-like objects suitable for the pipeline.

Usage example:

```python
from easy_rag_pipeline.adapters.raganything_adapter import parse_with_raganything

# Parse a local PDF / multimodal file with raganything (must be installed separately)
docs = parse_with_raganything('path/to/my_multimodal_document.pdf', config={'some_setting': True})

# You can then chunk/embed/index these docs using the normal pipeline helpers
from easy_rag_pipeline.ingest import chunk_documents
from easy_rag_pipeline.embed import get_embedding_function
from easy_rag_pipeline.store import create_vector_store

chunks = chunk_documents(docs, chunk_size=800, chunk_overlap=100)
embed_fn = get_embedding_function({'provider': 'openrouter', 'model': 'text-embedding-3-large'})
vs = create_vector_store(chunks, embed_fn, {'provider': 'faiss'})
```

Notes:
- `raganything` must be installed separately. The adapter will raise ImportError if it's not present.
- The adapter returns `Document`-like objects with `page_content` and `metadata` fields.

