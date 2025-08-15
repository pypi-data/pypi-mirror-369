import json
import os
import sys
from dotenv import load_dotenv
from .tools import (
    list_files,
    read_file,
    write_file,
    list_files_by_pattern,
    ask_any_question_internet,
    execute_shell_command,
    mkdir,
    sqlite_execute_sql
)
from agents.OllamaAgent import OllamaAgent
from agents.OpenAIAgent import OpenAIAgent
from .tools_definition import tools as tool_definitions
from .setup import ensure_env_setup

if not ensure_env_setup():
    print("❌ Environment setup failed. Please configure the environment variables before using the toolkit.")
    sys.exit(1)

def run_agent_with_question(question: str, save_messages: bool = True, messages_file: str = "messages.json", stream: bool = True):
    """
    Run the agent with a given question and optionally save the conversation history.
    
    Args:
        question (str): The question to ask the agent
        save_messages (bool): Whether to save the conversation to a JSON file
        messages_file (str): The filename to save messages to
        stream (bool): Whether to stream the response from Ollama (default: True)
    
    Returns:
        tuple: (result, messages) - The agent's response and conversation history
    """
    
    available_functions = {
        "list_files": list_files,
        "read_file": read_file,
        "write_file": write_file,
        "list_files_by_pattern": list_files_by_pattern,
        "ask_any_question_internet": ask_any_question_internet,
        "mkdir": mkdir,
        "execute_shell_command": execute_shell_command,
        "sqlite_execute_sql": sqlite_execute_sql
    }

    current_agent = os.getenv("CURRENT_AGENT", "OLLAMA").upper()
    
    if current_agent == "OPENAI":
        print("Using OpenAI Agent")
        agent = OpenAIAgent(
            tool_definitions=tool_definitions,
            tool_callables=available_functions,
            system_prompt="You are a helpful assistant that can call tools to answer questions."
        )
    else:
        print("Using Ollama Agent")
        agent = OllamaAgent(
            tool_definitions=tool_definitions,
            tool_callables=available_functions,
            system_prompt="You are a helpful assistant that can call tools to answer questions."
        )

    if stream:
        result = agent.run_with_streaming(question)
    else:
        result = agent.run(question)

    def make_serializable(obj):
        """Recursively convert objects to JSON-serializable format"""
        if isinstance(obj, dict):
            return {key: make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [make_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            # Convert object to dictionary
            return {key: make_serializable(value) for key, value in obj.__dict__.items()}
        elif hasattr(obj, 'to_dict'):
            # If object has a to_dict method, use it
            return make_serializable(obj.to_dict())
        else:
            try:
                # Try to serialize as-is (for basic types like str, int, bool, etc.)
                json.dumps(obj)
                return obj
            except (TypeError, ValueError):
                # If not serializable, convert to string
                return str(obj)

    serializable_messages = []
    for message in agent.messages:
        try:
            # Convert the entire message to a serializable format
            serializable_message = make_serializable(message)
            serializable_messages.append(serializable_message)
        except Exception as e:
            print(f"Warning: Could not serialize message: {e}")
            # Fallback: create a basic message structure
            if isinstance(message, dict):
                basic_message = {
                    'role': message.get('role', 'unknown'),
                    'content': str(message.get('content', ''))
                }
                if 'tool_calls' in message:
                    basic_message['tool_calls'] = str(message['tool_calls'])
                if 'name' in message:
                    basic_message['name'] = str(message['name'])
            else:
                basic_message = {
                    'role': getattr(message, 'role', 'unknown'),
                    'content': str(getattr(message, 'content', message))
                }
            serializable_messages.append(basic_message)

    if save_messages:
        try:
            with open(messages_file, "w") as f:
                json.dump(serializable_messages, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save messages to {messages_file}: {e}")
            # Try to save a simplified version
            try:
                simplified_messages = []
                for msg in serializable_messages:
                    if isinstance(msg, dict):
                        simplified_msg = {
                            'role': str(msg.get('role', 'unknown')),
                            'content': str(msg.get('content', ''))
                        }
                        if 'name' in msg:
                            simplified_msg['name'] = str(msg['name'])
                        simplified_messages.append(simplified_msg)
                    else:
                        simplified_messages.append({'role': 'unknown', 'content': str(msg)})
                
                with open(messages_file, "w") as f:
                    json.dump(simplified_messages, f, indent=2)
                print(f"Saved simplified messages to {messages_file}")
            except Exception as e2:
                print(f"Error: Could not save even simplified messages: {e2}")

    return result, serializable_messages
