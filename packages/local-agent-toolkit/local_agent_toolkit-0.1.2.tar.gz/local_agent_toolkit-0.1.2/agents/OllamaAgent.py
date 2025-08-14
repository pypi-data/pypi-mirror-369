
import os
import ollama
from typing import Callable, Dict, Any, List
from dotenv import load_dotenv

# Load .env file from the project root directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

MAX_ITERATIONS = os.getenv("MAX_ITERATIONS", "25")
class OllamaAgent:
    """
    An AI agent that uses Ollama models to interact with users and execute tools.
    This agent can maintain conversation history, execute tool calls,
    and handle multiple iterations of interaction to complete complex tasks.
    Attributes:
        model (str): The name of the Ollama model to use
        tool_definitions (List[Dict]): List of available tool definitions
        tool_callables (Dict[str, Callable]): Dictionary mapping tool names to callable functions
        messages (List[Dict]): Conversation history
        client: Ollama client instance for API communication
    """
    def __init__(self, model: str = None, tool_definitions: List[Dict] = None, tool_callables: Dict[str, Callable] = None, system_prompt: str = None):
        self.model = model or os.getenv("OLLAMA_MODEL")
        self.tool_definitions = tool_definitions
        self.tool_callables = tool_callables
        self.messages = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})
        ollama_host = os.environ.get("OLLAMA_HOST", "https://together-boar-logically.ngrok-free.app/")
        self.client = ollama.Client(host=ollama_host)

    def run(self, user_prompt: str, max_iterations: int = MAX_ITERATIONS):
        self.messages.append({"role": "user", "content": user_prompt})
        for i in range(int(max_iterations)):
            print(f"Iteration {i + 1}")
            response = self.client.chat(
                model=self.model,
                messages=self.messages,
                tools=self.tool_definitions
            )
            if 'message' in response and response['message']:
                self.messages.append(response['message'])
                if not response['message'].get('tool_calls'):
                    return response['message']['content']
                tool_calls = response['message']['tool_calls']
                for tool_call in tool_calls:
                    tool_name = tool_call['function']['name']
                    tool_args = tool_call['function']['arguments']
                    if tool_name not in self.tool_callables:
                        print(f"Error: Tool '{tool_name}' not found.")
                        self.messages.append({
                            "role": "tool",
                            "content": f"Error: Tool '{tool_name}' not found.",
                            "name": tool_name
                        })
                        continue
                    try:
                        print(f"Calling tool: {tool_name} with args: {tool_args}")
                        tool_output = self.tool_callables[tool_name](**tool_args)
                        print(f"Tool output: {tool_output}")
                        self.messages.append({
                            "role": "tool",
                            "content": str(tool_output),
                            "name": tool_name
                        })
                    except Exception as e:
                        print(f"Error executing tool '{tool_name}': {e}")
                        self.messages.append({
                            "role": "tool",
                            "content": f"Error executing tool '{tool_name}': {e}",
                            "name": tool_name
                        })
            else:
                print("Error: Empty response from the model.")
                return "The agent received an empty response from the model."
        return "The agent could not complete the task within the maximum number of iterations."

    def run_with_streaming(self, user_prompt: str, max_iterations: int = MAX_ITERATIONS):
        self.messages.append({"role": "user", "content": user_prompt})
        for i in range(int(max_iterations)):
            print(f"Iteration {i + 1}")
            stream = self.client.chat(
                model=self.model,
                messages=self.messages,
                tools=self.tool_definitions,
                stream=True
            )
            full_content = ""
            tool_calls = []
            current_message = {"role": "assistant", "content": ""}
            for chunk in stream:
                if 'message' in chunk and chunk['message']:
                    message = chunk['message']
                    if 'content' in message and message['content']:
                        content_chunk = message['content']
                        full_content += content_chunk
                        print(content_chunk, end='', flush=True)
                    if 'tool_calls' in message and message['tool_calls']:
                        tool_calls.extend(message['tool_calls'])
                    if 'role' in message:
                        current_message['role'] = message['role']
                    if 'content' in message:
                        current_message['content'] = full_content
            print()  # New line after streaming content
            if tool_calls:
                current_message['tool_calls'] = tool_calls
            self.messages.append(current_message)
            if not tool_calls:
                return full_content
            for tool_call in tool_calls:
                tool_name = tool_call['function']['name']
                tool_args = tool_call['function']['arguments']
                if tool_name not in self.tool_callables:
                    print(f"Error: Tool '{tool_name}' not found.")
                    self.messages.append({
                        "role": "tool",
                        "content": f"Error: Tool '{tool_name}' not found.",
                        "name": tool_name
                    })
                    continue
                try:
                    print(f"Calling tool: {tool_name} with args: {tool_args}")
                    tool_output = self.tool_callables[tool_name](**tool_args)
                    print(f"Tool output: {tool_output}")
                    self.messages.append({
                        "role": "tool",
                        "content": str(tool_output),
                        "name": tool_name
                    })
                except Exception as e:
                    print(f"Error executing tool '{tool_name}': {e}")
                    self.messages.append({
                        "role": "tool",
                        "content": f"Error executing tool '{tool_name}': {e}",
                        "name": tool_name
                    })
        return "The agent could not complete the task within the maximum number of iterations."
