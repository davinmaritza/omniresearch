"""Configuration management and LLM provider factory for OmniResearch."""

import os
from typing import Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Global configuration settings for OmniResearch."""

    # Provider configurations
    llm_provider: Literal["gemini", "openai", "anthropic", "ollama"] = "gemini"
    llm_model: str = "gemini-1.5-pro"
    
    # API Keys
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Local LLM
    ollama_base_url: str = "http://localhost:11434"
    
    # Search Provider
    search_provider: Literal["duckduckgo", "tavily", "exa"] = "duckduckgo"
    tavily_api_key: Optional[str] = None
    exa_api_key: Optional[str] = None
    
    # Agent Hyperparameters
    max_research_iterations: int = 3
    max_search_results_per_query: int = 5
    enable_fact_checking: bool = True
    report_output_dir: str = "./reports"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


def get_settings() -> Settings:
    """Retrieve application settings."""
    return Settings(
        llm_provider=os.getenv("LLM_PROVIDER", "gemini"),  # type: ignore
        llm_model=os.getenv("LLM_MODEL", "gemini-1.5-pro"),
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        search_provider=os.getenv("SEARCH_PROVIDER", "duckduckgo"),  # type: ignore
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        exa_api_key=os.getenv("EXA_API_KEY"),
        max_research_iterations=int(os.getenv("MAX_RESEARCH_ITERATIONS", "3")),
        max_search_results_per_query=int(os.getenv("MAX_SEARCH_RESULTS_PER_QUERY", "5")),
        enable_fact_checking=os.getenv("ENABLE_FACT_CHECKING", "true").lower() in ("true", "1", "yes"),
        report_output_dir=os.getenv("REPORT_OUTPUT_DIR", "./reports"),
    )
