import os
from pathlib import Path
from typing import Optional, Union

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres import PGVector

# Load environment variables from a .env file if present
load_dotenv()

# Helper functions for validation


def _require(var_name: str, value: Optional[str]) -> str:
    if value is None or str(value).strip() == "":
        raise EnvironmentError(f"Missing required environment variable: {var_name}")
    return value


def _require_file(path_str: Optional[str], var_name: str) -> str:
    path = _require(var_name, path_str)
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"{var_name} points to a non-existent path: {p}")
    if p.is_dir():
        raise IsADirectoryError(
            f"{var_name} should be a file, but a directory was given: {p}"
        )
    return str(p)


# PDF File path must exist
PDF_PATH = _require_file(os.getenv("PDF_PATH"), "PDF_PATH")

# Database config must always be present
PG_VECTOR_COLLECTION_NAME = _require(
    "PG_VECTOR_COLLECTION_NAME", os.getenv("PG_VECTOR_COLLECTION_NAME")
)
DATABASE_URL = _require("DATABASE_URL", os.getenv("DATABASE_URL"))

# Embeddings / LLM provider configuration
# We must have either OpenAI variables configured OR Google variables configured.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL")

openai_ok = bool(OPENAI_API_KEY and OPENAI_EMBEDDING_MODEL)
google_ok = bool(GOOGLE_API_KEY and GOOGLE_EMBEDDING_MODEL)

if not (openai_ok or google_ok):
    raise EnvironmentError(
        "You must configure either OpenAI or Google embedding provider. "
        "Set both OPENAI_API_KEY and OPENAI_EMBEDDING_MODEL, or both GOOGLE_API_KEY and GOOGLE_EMBEDDING_MODEL."
    )

# Optional: normalize whitespace
if OPENAI_EMBEDDING_MODEL:
    OPENAI_EMBEDDING_MODEL = OPENAI_EMBEDDING_MODEL.strip()
    OPENAI_MODEL = "gpt-5-nano"
if GOOGLE_EMBEDDING_MODEL:
    GOOGLE_EMBEDDING_MODEL = GOOGLE_EMBEDDING_MODEL.strip()
    GOOGLE_MODEL = "gemini-2.5-flash-lite"

# Provider selection: if OpenAI is configured, prefer it; otherwise use Google
PROVIDER = "openai" if openai_ok else "google"


def get_embedding_model_integration(
    provider: str,
) -> Union[OpenAIEmbeddings, GoogleGenerativeAIEmbeddings]:
    if provider == "openai":
        return OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)
    elif provider == "google":
        return GoogleGenerativeAIEmbeddings(model=GOOGLE_EMBEDDING_MODEL)
    raise ValueError(f"Invalid provider: {provider}")


def get_store(embeddings: Union[OpenAIEmbeddings, GoogleGenerativeAIEmbeddings]):
    return PGVector(
        embeddings=embeddings,
        collection_name=PG_VECTOR_COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
    )


def get_chat(provider: str):
    if provider == "openai":
        return ChatOpenAI(model=OPENAI_MODEL)
    elif provider == "google":
        return GoogleGenerativeAI(model=GOOGLE_MODEL)
    raise ValueError(f"Invalid provider: {provider}")
