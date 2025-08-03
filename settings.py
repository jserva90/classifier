#!/usr/bin/env python3

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    PORT: int = 5000
    HOST: str = "0.0.0.0"
    DEBUG: bool = False
    DEFAULT_MODEL: str = "gpt-4.1"
    DEFAULT_TEMPERATURE: float = 0.3
    DEFAULT_MAX_TOKENS: int = 1000
    DEFAULT_CLAUSE_TYPES: List[str] = [
        "Termination", 
        "Confidentiality", 
        "Governing Law", 
        "Payment Terms", 
        "Liability", 
        "Intellectual Property"
    ]
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()