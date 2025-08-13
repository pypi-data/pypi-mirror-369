"""
Configuration management for Vibe Python
"""
import os
from typing import Optional


class Config:
    """Configuration class to store API settings"""
    
    def __init__(self):
        self.api_key: Optional[str] = None
        self.model_name: str = "gpt-5-mini"
        self.api_url: str = "https://api.openai.com/v1"
        self.max_tokens: int = 4096
        self.temperature: float = 0.1
        
        # Load from environment variables if available
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        if os.getenv("OPENAI_API_KEY"):
            self.api_key = os.getenv("OPENAI_API_KEY")
        if os.getenv("OPENAI_MODEL"):
            self.model_name = os.getenv("OPENAI_MODEL")
        if os.getenv("OPENAI_API_URL"):
            self.api_url = os.getenv("OPENAI_API_URL")
    
    def set_api_key(self, api_key: str):
        """Set the OpenAI API key"""
        self.api_key = api_key
    
    def set_model(self, model_name: str):
        """Set the model name"""
        self.model_name = model_name
    
    def set_api_url(self, api_url: str):
        """Set the API URL"""
        self.api_url = api_url
    
    def set_temperature(self, temperature: float):
        """Set the temperature for API calls"""
        if not 0.0 <= temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        self.temperature = temperature
    
    def is_configured(self) -> bool:
        """Check if the configuration is valid"""
        return self.api_key is not None
    
    def get_config_dict(self) -> dict:
        """Get configuration as dictionary"""
        return {
            "api_key": self.api_key,
            "model_name": self.model_name,
            "api_url": self.api_url,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }


# Global configuration instance
_config = Config()


def get_config() -> Config:
    """Get the global configuration instance"""
    return _config