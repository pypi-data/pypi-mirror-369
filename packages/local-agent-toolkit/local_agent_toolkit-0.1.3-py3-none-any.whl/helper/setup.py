"""
Environment setup utilities for Local Agent Toolkit.

This module provides functions for managing environment variables
and helping users configure the toolkit on first use.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv, set_key

def check_env_vars() -> bool:
    """
    Check if required environment variables are set.
    
    Returns:
        bool: True if all required variables are set, False otherwise
    """
    current_agent = os.getenv("CURRENT_AGENT")
    
    if current_agent is None:
        return False
        
    if current_agent.upper() == "OLLAMA":
        return all([
            os.getenv("OLLAMA_MODEL"),
            os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_HOST")
        ])
    elif current_agent.upper() == "OPENAI":
        has_api_key = bool(os.getenv("OPENAI_API_KEY"))
        if not has_api_key:
            return False
        
        if not os.getenv("OPENAI_API_BASE"):
            os.environ["OPENAI_API_BASE"] = "https://api.openai.com/v1"
        
        return True
    
    return False

def get_env_file_path(global_config: bool = False) -> Path:
    """
    Get the path to the environment file.
    
    Args:
        global_config: Whether to use global configuration path
        
    Returns:
        Path: Path to the environment file
    """
    if global_config:
        config_dir = Path.home() / ".config" / "local-agent-toolkit"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / ".env"
    else:
        return Path(os.getcwd()) / ".env"

def save_env_vars(env_vars: Dict[str, str], global_config: bool = False) -> Path:
    """
    Save environment variables to a .env file.
    
    Args:
        env_vars: Dictionary of environment variables to save
        global_config: Whether to save to global configuration
        
    Returns:
        Path: Path to the saved environment file
    """
    env_file = get_env_file_path(global_config)
    
    if not env_file.exists():
        env_file.touch()
    
    for key, value in env_vars.items():
        set_key(str(env_file), key, value)
    
    return env_file

def interactive_setup() -> Optional[Path]:
    """
    Run an interactive setup to configure the Local Agent Toolkit.
    
    Returns:
        Optional[Path]: Path to the saved configuration file or None if canceled
    """
    print("\n" + "=" * 60)
    print("🚀 Local Agent Toolkit - First-time Setup")
    print("=" * 60)
    print("\nWelcome! Let's set up your environment for Local Agent Toolkit.")
    print("This will help you configure the AI agent you want to use.\n")
    
    print("First, choose which AI agent you want to use:")
    print("1. Ollama (local LLM, requires Ollama running)")
    print("2. OpenAI (requires API key)")
    
    agent_choice = ""
    while agent_choice not in ["1", "2"]:
        agent_choice = input("\nEnter your choice (1 or 2): ").strip()
        if agent_choice not in ["1", "2"]:
            print("Invalid choice. Please enter 1 or 2.")
    
    env_vars = {}
    
    if agent_choice == "1":
        env_vars["CURRENT_AGENT"] = "OLLAMA"
        
        default_model = "llama3.1"
        model = input(f"\nEnter Ollama model name [{default_model}]: ").strip()
        if not model:
            model = default_model
        env_vars["OLLAMA_MODEL"] = model
        
        default_url = "http://localhost:11434"
        base_url = input(f"\nEnter Ollama base URL [{default_url}]: ").strip()
        if not base_url:
            base_url = default_url
        env_vars["OLLAMA_BASE_URL"] = base_url
        env_vars["OLLAMA_HOST"] = base_url
        
    else:
        env_vars["CURRENT_AGENT"] = "OPENAI"
        
        while True:
            api_key = input("\nEnter your OpenAI API key: ").strip()
            if not api_key:
                print("API key cannot be empty. Please try again.")
            elif not api_key.startswith(("sk-", "sk_")):
                print("Warning: This doesn't look like a valid OpenAI API key.")
                confirm = input("Continue anyway? (y/n): ").strip().lower()
                if confirm == 'y':
                    break
            else:
                break
        env_vars["OPENAI_API_KEY"] = api_key
        
        default_api_base = "https://api.openai.com/v1"
        api_base = input(f"\nEnter OpenAI API base URL [{default_api_base}]: ").strip()
        if not api_base:
            api_base = default_api_base
        env_vars["OPENAI_API_BASE"] = api_base
        
        default_model = "gpt-4"
        model = input(f"\nEnter OpenAI model name [{default_model}]: ").strip()
        if not model:
            model = default_model
        env_vars["OPENAI_MODEL"] = model
    
    print("\nWhere would you like to save this configuration?")
    print("1. Current directory (.env file in your working directory)")
    print("2. Global user configuration (~/.config/local-agent-toolkit/.env)")
    
    save_choice = ""
    while save_choice not in ["1", "2"]:
        save_choice = input("\nEnter your choice (1 or 2): ").strip()
        if save_choice not in ["1", "2"]:
            print("Invalid choice. Please enter 1 or 2.")
    
    global_config = (save_choice == "2")
    
    env_file = save_env_vars(env_vars, global_config)
    
    print("\n✅ Configuration saved successfully!")
    print(f"📁 Configuration file: {env_file}")
    
    for key, value in env_vars.items():
        os.environ[key] = value
    
    print("\n🔄 Configuration loaded and ready to use!")
    print("=" * 60)
    
    return env_file

def ensure_env_setup() -> bool:
    """
    Ensure environment variables are set up properly.
    
    This function checks if required environment variables are set.
    If not, it loads them from available .env files in priority order.
    If no configuration is found, it triggers the interactive setup.
    
    Returns:
        bool: True if setup was successful, False otherwise
    """
    if check_env_vars():
        return True
    
    local_env = Path(os.getcwd()) / ".env"
    if local_env.exists():
        load_dotenv(dotenv_path=str(local_env))
        if check_env_vars():
            return True
    
    package_env = Path(os.path.dirname(os.path.dirname(__file__))) / ".env"
    if package_env.exists():
        load_dotenv(dotenv_path=str(package_env))
        if check_env_vars():
            return True
    
    global_env = Path.home() / ".config" / "local-agent-toolkit" / ".env"
    if global_env.exists():
        load_dotenv(dotenv_path=str(global_env))
        if check_env_vars():
            return True
    try:
        interactive_setup()
        return check_env_vars()
    except (KeyboardInterrupt, EOFError):
        print("\n\n❌ Setup canceled. You'll need to configure the environment before using the toolkit.")
        return False
