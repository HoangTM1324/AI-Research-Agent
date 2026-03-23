from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # --- Qdrant config ---
    COLLECTION_NAME: str = "pdf_chunk"
    QDRANT_API_KEY: str
    QDRANT_HOST: str

    # --- Embedding model configs ---
    EMBEDDOMG_API_KEY: str 
    EMBEDDING_MODEL: str = "gemini-embedding-001"
    EMBEDDING_DIM: int = 768

    # --- Generate model config