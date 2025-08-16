"""
Agentils - AI Agent Utilities Library

A powerful toolkit for building AI agents with LLM integration, 
decorators for easy function calling, and utility functions.
"""

from .main import AgentsUtils
from .utils import Utils

__version__ = "0.1.0"
__author__ = "aggreyeric"
__email__ = "ericaggrey@outlook.com"

# Export main classes and functions
__all__ = [
    "AgentsUtils",
    "Utils",
    "main"
]


def main() -> None:
    """Main entry point for the CLI"""
    print("Agentils - AI Agent Utilities")
    print(f"Version: {__version__}")
    print("Use AgentsUtils for LLM decorators and Utils for utility functions.")
    
    # Show basic usage example
    print("\nBasic usage:")
    print("from agentils import AgentsUtils")
    print("")
    print("@AgentsUtils.execute_llm(output='json')")
    print("def my_task():")
    print("    return 'Analyze this data and return JSON'")
    print("")
    print("result = my_task()")
    print("print(result)")
