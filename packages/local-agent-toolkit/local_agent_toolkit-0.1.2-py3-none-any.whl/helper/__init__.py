"""
Local Agent Toolkit - Helper Module

This module provides the core functionality for running an AI agent
with tool calling capabilities, including the agent implementation,
tool definitions, and utility functions.

Main Functions:
    run_agent_with_question: Execute the agent with a question and get results
    
Classes:
    OllamaAgent: Ollama-based agent implementation
    OpenAIAgent: OpenAI-based agent implementation

Usage Examples:
    # As a library
    from local_agent_toolkit import run_agent_with_question
    result, messages = run_agent_with_question("What files are in the current directory?")
    
    # Using specific agents
    from local_agent_toolkit.agents import OllamaAgent, OpenAIAgent
    
    # Using tools directly
    from local_agent_toolkit.helper.tools import list_files, read_file
"""

from .tool_call import run_agent_with_question
from .tools import *
from .tools_definition import tools
from .setup import ensure_env_setup, interactive_setup

# Make the main classes importable from the top level
try:
    from ..agents.OllamaAgent import OllamaAgent
    from ..agents.OpenAIAgent import OpenAIAgent
except ImportError:
    # For when imported as installed package
    try:
        from agents.OllamaAgent import OllamaAgent
        from agents.OpenAIAgent import OpenAIAgent
    except ImportError:
        OllamaAgent = None
        OpenAIAgent = None

__version__ = "0.1.2"
__all__ = [
    'run_agent_with_question', 
    'OllamaAgent', 
    'OpenAIAgent',
    'tools',
    'ensure_env_setup',
    'interactive_setup',
    # Tool functions
    'list_files',
    'read_file', 
    'write_file',
    'list_files_by_pattern',
    'ask_any_question_internet',
    'execute_shell_command',
    'mkdir'
]
