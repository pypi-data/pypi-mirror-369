"""
Core functionality for Vibe Python
"""
import os
import sys
import subprocess
import tempfile
from typing import Optional, Dict, Any
import json

try:
    import openai
except ImportError:
    openai = None

from .config import get_config


def set_api_key(api_key: str) -> None:
    """Set the OpenAI API key"""
    config = get_config()
    config.set_api_key(api_key)


def set_model(model_name: str) -> None:
    """Set the model name"""
    config = get_config()
    config.set_model(model_name)


def set_api_url(api_url: str) -> None:
    """Set the API URL"""
    config = get_config()
    config.set_api_url(api_url)


def set_temperature(temperature: float) -> None:
    """Set the temperature for API calls"""
    config = get_config()
    config.set_temperature(temperature)


def _execute_python_code(code: str) -> Dict[str, Any]:
    """
    Execute Python code and return the result
    
    Args:
        code: Python code to execute
        
    Returns:
        Dictionary with 'success', 'output', 'error' keys
    """
    try:
        # Create a temporary file with the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        # Execute the code using subprocess
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        # Clean up temporary file
        os.unlink(temp_file)
        
        if result.returncode == 0:
            return {
                "success": True,
                "output": result.stdout.strip(),
                "error": None,
                "return_code": result.returncode
            }
        else:
            return {
                "success": False,
                "output": result.stdout.strip(),
                "error": result.stderr.strip(),
                "return_code": result.returncode
            }
            
    except subprocess.TimeoutExpired:
        os.unlink(temp_file)
        return {
            "success": False,
            "output": "",
            "error": "Code execution timed out (30 seconds)",
            "return_code": -1
        }
    except Exception as e:
        if 'temp_file' in locals():
            try:
                os.unlink(temp_file)
            except:
                pass
        return {
            "success": False,
            "output": "",
            "error": f"Execution error: {str(e)}",
            "return_code": -1
        }


def _call_openai_api(code: str) -> str:
    """
    Call OpenAI API to execute Python code and return results
    
    Args:
        code: Python code to analyze and execute
        
    Returns:
        String containing the execution result
    """
    config = get_config()
    
    if not config.is_configured():
        raise ValueError("OpenAI API key not configured. Use set_api_key() or set OPENAI_API_KEY environment variable.")
    
    if openai is None:
        raise ImportError("OpenAI library not installed. Install with: pip install openai")
    
    # Configure OpenAI client
    client = openai.OpenAI(
        api_key=config.api_key,
        base_url=config.api_url
    )
    
    # Prepare the prompt
    prompt = f"""You are a Python code execution assistant. Execute the following Python code and return ONLY the command line output (stdout/stderr) that would appear when running this code.

Rules:
1. If the code runs successfully, return only the printed output or final result
2. If there are errors, return only the error message as it would appear in the terminal
3. Do not add any explanations, comments, or formatting - just the raw output
4. If the code produces no output, return an empty response
5. Handle imports, calculations, print statements, and basic Python operations

Python code to execute:
```python
{code}
```

Command line output:"""

    try:
        response = client.chat.completions.create(
            model=config.model_name,
            messages=[
                {"role": "system", "content": "You are a Python code execution assistant that returns only the raw command line output."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        raise RuntimeError(f"OpenAI API call failed: {str(e)}")


def run_vibe(code_or_file: str, use_local: bool = False) -> str:
    """
    Execute Python code using OpenAI API or local execution
    
    Args:
        code_or_file: Python code string or path to Python file
        use_local: If True, execute locally instead of using OpenAI API
        
    Returns:
        String containing the execution result
    """
    # Check if input is a file path
    if os.path.isfile(code_or_file):
        with open(code_or_file, 'r', encoding='utf-8') as f:
            code = f.read()
    else:
        code = code_or_file
    
    if use_local:
        # Execute locally
        result = _execute_python_code(code)
        if result["success"]:
            return result["output"]
        else:
            return result["error"] or "Code execution failed"
    else:
        # Use OpenAI API
        try:
            return _call_openai_api(code)
        except Exception as e:
            return f"Error: {str(e)}"