import yaml
import os
from dotenv import load_dotenv

def load_config(path: str = "config.yaml") -> dict:
    """
    Loads configuration from a YAML file and merges it with environment variables,
    especially for API keys.

    Args:
        path (str): The path to the configuration YAML file.

    Returns:
        dict: A dictionary containing the loaded and merged configuration.
    """
    # Load environment variables from a .env file if it exists
    load_dotenv()

    # Load base configuration from YAML file
    with open(path, "r") as f:
        config = yaml.safe_load(f)

    # --- API Key Loading Logic ---
    # Determine the provider for both LLM and embeddings to load the correct key.

    # Load LLM API key
    llm_provider = config.get("llm", {}).get("provider")
    if llm_provider:
        key_name = f"{llm_provider.upper()}_API_KEY"
        # Special case for Google
        if llm_provider.lower() == 'gemini':
            key_name = "GOOGLE_API_KEY"

        api_key = os.getenv(key_name)
        if api_key:
            if 'llm' not in config:
                config['llm'] = {}
            config['llm']['api_key'] = api_key

    # Load Embedding API key
    embedding_provider = config.get("embedding", {}).get("provider")
    if embedding_provider:
        key_name = f"{embedding_provider.upper()}_API_KEY"
        api_key = os.getenv(key_name)
        if api_key:
            if 'embedding' not in config:
                config['embedding'] = {}
            config['embedding']['api_key'] = api_key

    return config
