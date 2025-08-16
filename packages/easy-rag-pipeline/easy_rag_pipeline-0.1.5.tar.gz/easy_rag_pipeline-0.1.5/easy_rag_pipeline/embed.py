
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

try:
    from langchain_groq import GroqEmbeddings
except ImportError:
    GroqEmbeddings = None

try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    OpenAIEmbeddings = None

# OpenRouter does not have a dedicated embedding class in LangChain as of now.
# If/when it does, add here. For now, use OpenAIEmbeddings with base_url override if needed.

def get_embedding_function(embedding_config: dict):
    """
    Creates and returns an embedding function based on the provided configuration.

    Args:
        embedding_config (dict): A dictionary containing embedding model details.
            Example for OpenAI:
            {
                "provider": "openai",
                "model": "text-embedding-ada-002",
                "api_key": "..."
            }
            Example for HuggingFace:
            {
                "provider": "huggingface",
                "model": "sentence-transformers/all-MiniLM-L6-v2"
            }

    Returns:
        An embedding function object from LangChain.
    """
    provider = embedding_config.get("provider", "openai").lower()

    if provider == "openai":
        if OpenAIEmbeddings is None:
            raise ImportError("langchain_openai is not installed.")
        return OpenAIEmbeddings(
            model=embedding_config.get("model", "text-embedding-ada-002"),
            openai_api_key=embedding_config.get("api_key")
        )
    elif provider == "openrouter":
        if OpenAIEmbeddings is None:
            raise ImportError("langchain_openai is not installed.")
        # OpenRouter supports OpenAI-compatible API for embeddings
        return OpenAIEmbeddings(
            model=embedding_config.get("model", "text-embedding-ada-002"),
            openai_api_key=embedding_config.get("api_key"),
            base_url="https://openrouter.ai/api/v1"
        )
    elif provider == "huggingface":
        return HuggingFaceEmbeddings(
            model_name=embedding_config.get("model", "sentence-transformers/all-MiniLM-L6-v2")
        )
    elif provider == "simple" or provider == "local":
        # Lightweight deterministic embedding for offline testing.
        # Produces a fixed-length vector derived from SHA-256 digest.
        import hashlib

        class SimpleEmbeddings:
            def __init__(self, dim: int = 32):
                self.dim = dim

            def _embed_text(self, text: str):
                if not isinstance(text, str):
                    text = str(text)
                h = hashlib.sha256(text.encode('utf-8')).digest()
                # convert bytes to floats in -0.5..0.5
                vals = [((b / 255.0) - 0.5) for b in h]
                # pad or trim to dim
                if len(vals) >= self.dim:
                    return [float(x) for x in vals[: self.dim]]
                else:
                    # repeat pattern
                    out = vals[:]
                    i = 0
                    while len(out) < self.dim:
                        out.append(vals[i % len(vals)])
                        i += 1
                    return [float(x) for x in out]

            def embed_documents(self, texts):
                return [self._embed_text(t) for t in texts]

            def embed_query(self, text):
                return self._embed_text(text)

            # Support being called directly: some vectorstore implementations
            # accept a callable embedding function rather than a LangChain Embeddings
            # object. Implement __call__ to return the embedding for a single text.
            def __call__(self, text):
                return self._embed_text(text)

        return SimpleEmbeddings(dim=embedding_config.get('dim', 32))
    elif provider == "groq":
        if GroqEmbeddings is None:
            raise ImportError("langchain_groq is not installed or does not support GroqEmbeddings.")
        return GroqEmbeddings(
            model=embedding_config.get("model", "nomic-embed-text-v1"),
            groq_api_key=embedding_config.get("api_key")
        )
    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")
