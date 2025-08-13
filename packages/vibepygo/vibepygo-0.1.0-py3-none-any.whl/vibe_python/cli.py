"""
Command line interface for Vibe Python
"""
import argparse
import sys
from .core import run_vibe, set_api_key, set_model, set_api_url


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Execute Python code using OpenAI API")
    parser.add_argument("file", help="Python file to execute")
    parser.add_argument("--api-key", help="OpenAI API key")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="Model name")
    parser.add_argument("--api-url", default="https://api.openai.com/v1", help="API URL")
    parser.add_argument("--local", action="store_true", help="Execute locally instead of using OpenAI")
    
    args = parser.parse_args()
    
    if args.api_key:
        set_api_key(args.api_key)
    if args.model:
        set_model(args.model)
    if args.api_url:
        set_api_url(args.api_url)
    
    try:
        result = run_vibe(args.file, use_local=args.local)
        print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()