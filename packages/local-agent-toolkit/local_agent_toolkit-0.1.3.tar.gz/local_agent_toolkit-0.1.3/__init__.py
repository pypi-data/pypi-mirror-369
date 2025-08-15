"""
Local Agent Toolkit

A sophisticated AI agent toolkit supporting multiple AI providers with tool calling capabilities.

This package provides:
- AI agents that can use tools to perform tasks
- Support for Ollama and OpenAI models
- Command-line interface for interactive use
- Python library for programmatic use

Quick Start:
    # Install the package
    pip install local-agent-toolkit
    
    # Use as command line tool
    local-agent "What files are in the current directory?"
    
    # Use as Python library
    from local_agent_toolkit import run_agent_with_question
    result, messages = run_agent_with_question("Your question here")

Environment Variables:
    CURRENT_AGENT: Set to "OLLAMA" or "OPENAI" (default: "OLLAMA")
    OLLAMA_MODEL: Ollama model name (default: "llama3.1")
    OLLAMA_BASE_URL: Ollama server URL (default: "http://localhost:11434")
    OPENAI_API_KEY: OpenAI API key (required for OpenAI agent)
"""

from helper import run_agent_with_question, tools
from helper import OllamaAgent, OpenAIAgent

__version__ = "0.1.0"
__author__ = "TechnicalHeist"
__email__ = "contact@technicalheist.com"

__all__ = [
    'run_agent_with_question',
    'OllamaAgent', 
    'OpenAIAgent',
    'tools'
]
