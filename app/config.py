import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    # OpenAI API Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4-turbo-preview", env="OPENAI_MODEL")
    
    # OpenAI Agent SDK Configuration
    agent_sdk_enabled: bool = Field(True, env="AGENT_SDK_ENABLED")
    agent_threads_ttl: int = Field(3600, env="AGENT_THREADS_TTL")  # Time to live for agent threads in seconds
    
    # DALL-E Configuration
    dalle_model: str = Field("dall-e-3", env="DALLE_MODEL")
    
    # Application Configuration
    app_host: str = Field("0.0.0.0", env="APP_HOST")
    app_port: int = Field(8000, env="APP_PORT")
    debug: bool = Field(False, env="DEBUG")
    
    # Post Proposals Configuration
    min_proposals: int = Field(10, env="MIN_PROPOSALS")
    max_proposals: int = Field(20, env="MAX_PROPOSALS")
    
    # Search Configuration
    search_enabled: bool = Field(True, env="SEARCH_ENABLED")
    max_search_results: int = Field(5, env="MAX_SEARCH_RESULTS")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Create settings instance
settings = Settings()
