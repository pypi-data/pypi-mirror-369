"""
Pytest tests for vibe_python
"""
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import vibe_python
from vibe_python.config import Config


class TestConfig:
    """Test configuration functionality"""
    
    def test_config_creation(self):
        """Test creating a new config instance"""
        config = Config()
        assert config.model_name == "gpt-3.5-turbo"
        assert config.api_url == "https://api.openai.com/v1"
        assert config.max_tokens == 4096
        assert config.temperature == 0.1
    
    def test_set_api_key(self):
        """Test setting API key"""
        config = Config()
        config.set_api_key("test-key")
        assert config.api_key == "test-key"
        assert config.is_configured() is True
    
    def test_set_model(self):
        """Test setting model name"""
        config = Config()
        config.set_model("gpt-4")
        assert config.model_name == "gpt-4"
    
    def test_set_api_url(self):
        """Test setting API URL"""
        config = Config()
        config.set_api_url("https://custom-api.com/v1")
        assert config.api_url == "https://custom-api.com/v1"


class TestCore:
    """Test core functionality"""
    
    def test_set_api_key_function(self):
        """Test the set_api_key function"""
        vibe_python.set_api_key("test-key-123")
        config = vibe_python.get_config()
        assert config.api_key == "test-key-123"
    
    def test_set_model_function(self):
        """Test the set_model function"""
        vibe_python.set_model("gpt-4-turbo")
        config = vibe_python.get_config()
        assert config.model_name == "gpt-4-turbo"
    
    def test_set_api_url_function(self):
        """Test the set_api_url function"""
        vibe_python.set_api_url("https://test-api.com/v1")
        config = vibe_python.get_config()
        assert config.api_url == "https://test-api.com/v1"
    
    def test_local_execution_simple(self):
        """Test local execution with simple code"""
        code = "print('Hello, World!')"
        result = vibe_python.run_vibe(code, use_local=True)
        assert result == "Hello, World!"
    
    def test_local_execution_math(self):
        """Test local execution with math operations"""
        code = """
x = 5
y = 10
print(x + y)
"""
        result = vibe_python.run_vibe(code, use_local=True)
        assert result == "15"
    
    def test_local_execution_error(self):
        """Test local execution with error"""
        code = "print(undefined_variable)"
        result = vibe_python.run_vibe(code, use_local=True)
        assert "NameError" in result
    
    def test_local_execution_import(self):
        """Test local execution with imports"""
        code = """
import math
print(int(math.sqrt(16)))
"""
        result = vibe_python.run_vibe(code, use_local=True)
        assert result == "4"
    
    def test_api_call_without_key(self):
        """Test API call without setting API key"""
        # Reset config
        config = vibe_python.get_config()
        config.api_key = None
        
        code = "print('test')"
        result = vibe_python.run_vibe(code, use_local=False)
        assert "Error:" in result
        assert "API key not configured" in result


if __name__ == "__main__":
    pytest.main([__file__])