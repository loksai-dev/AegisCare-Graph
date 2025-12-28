"""
Configuration module for AegisCare Graph
Loads environment variables securely from .env file
NEVER hardcode credentials - all must come from environment variables
"""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


def _mask_sensitive_value(value: str, visible_chars: int = 4) -> str:
    """Mask sensitive values for safe logging (show only last few characters)"""
    if not value or len(value) <= visible_chars:
        return "***"
    return "*" * (len(value) - visible_chars) + value[-visible_chars:]


class Settings(BaseSettings):
    """Application settings loaded from environment variables
    
    SECURITY NOTE: All credentials are loaded from environment variables only.
    Never hardcode API keys, passwords, or tokens in this file.
    """
    
    # Neo4j Configuration
    neo4j_uri: str = os.getenv("NEO4J_URI", "")
    neo4j_username: str = os.getenv("NEO4J_USERNAME", "")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "")
    neo4j_database: str = os.getenv("NEO4J_DATABASE", "neo4j")
    
    # Aura Configuration
    aura_instance_id: str = os.getenv("AURA_INSTANCEID", "")
    aura_instance_name: str = os.getenv("AURA_INSTANCENAME", "")
    
    # Gemini AI Configuration
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "google/gemini-2.5-flash")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env that aren't in the model
    
    def __repr__(self) -> str:
        """Safe string representation that masks sensitive values"""
        return (
            f"Settings("
            f"neo4j_uri={_mask_sensitive_value(self.neo4j_uri)}, "
            f"neo4j_username={self.neo4j_username}, "
            f"neo4j_password=***, "
            f"gemini_api_key=***, "
            f"neo4j_database={self.neo4j_database}, "
            f"gemini_model={self.gemini_model})"
        )


# Global settings instance
settings = Settings()


def validate_settings():
    """Validate that all required settings are present
    
    SECURITY: This function only checks for presence, never logs actual values
    """
    required = [
        "neo4j_uri",
        "neo4j_username", 
        "neo4j_password",
        "gemini_api_key"
    ]
    
    missing = [key for key in required if not getattr(settings, key)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    # Log validation success (without sensitive values)
    logger.info("Settings validated successfully - all required credentials loaded from environment")
    
    return True

