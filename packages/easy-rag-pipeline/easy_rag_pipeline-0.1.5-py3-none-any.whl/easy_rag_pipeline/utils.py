import logging
import sys

def setup_logging(level=logging.INFO):
    """
    Configures a basic logger to print to stdout.

    Args:
        level (int): The logging level (e.g., logging.INFO, logging.DEBUG).
    """
    logger = logging.getLogger("easy_rag_pipeline")
    logger.setLevel(level)

    # Avoid adding duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

# You can also add other helpers here, for example:
def clean_text(text: str) -> str:
    """
    A simple function to clean input text.
    (e.g., remove extra whitespace)
    """
    return " ".join(text.split())
