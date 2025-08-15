from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def generate_answer(query: str, docs: list, llm_config: dict):
    """
    Generates an answer using an LLM based on the query and retrieved documents.

    Args:
        query (str): The user's original query.
        docs (list): A list of retrieved documents to use as context.
        llm_config (dict): Configuration for the LLM.

    Returns:
        str: The generated answer.
    """
    provider = llm_config.get("provider", "openai").lower()
    model_name = llm_config.get("model")
    api_key = llm_config.get("api_key")
    temperature = llm_config.get("temperature", 0.7)

    if provider == "openai":
        llm = ChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            temperature=temperature
        )
    elif provider == "openrouter":
        llm = ChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=temperature
        )
    elif provider == "groq":
        llm = ChatGroq(
            model=model_name,
            groq_api_key=api_key,
            temperature=temperature
        )
    elif provider == "gemini":
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature,
            convert_system_message_to_human=True # Gemini needs this
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

    # include metadata (title/source) alongside page content to help answer
    # questions about document metadata (e.g., title)
    pieces = []
    for d in docs:
        title = d.metadata.get('title') if hasattr(d, 'metadata') else None
        source = d.metadata.get('source') if hasattr(d, 'metadata') else None
        meta = []
        if title:
            meta.append(f"Title: {title}")
        if source:
            meta.append(f"Source: {source}")
        if meta:
            pieces.append(" | ".join(meta))
        pieces.append(d.page_content)
    context = "\n\n".join(pieces)

    prompt_template = """
    Use the following context to answer the question at the end.
    If you don't know the answer, just say that you don't know. Do not try to make up an answer.

    Context:
    {context}

    Question:
    {question}

    Helpful Answer:
    """
    prompt = PromptTemplate.from_template(prompt_template)

    # Using LangChain Expression Language (LCEL) for the chain
    chain = prompt | llm | StrOutputParser()

    return chain.invoke({
        "context": context,
        "question": query
    })
