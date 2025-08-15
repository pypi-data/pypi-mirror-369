
import os
from openai import OpenAI
import json
from typing import Callable, Dict, Any, List

MAX_ITERATIONS = os.getenv("MAX_ITERATIONS", "25")

class OpenAIAgent:
    """
    An AI agent that uses OpenAI models to interact with users and execute tools.
    
    This agent provides both streaming and non-streaming completions using the official
    OpenAI Python client. It supports tool calling, custom API endpoints, and maintains
    conversation history throughout the interaction.
    
    Attributes:
        model (str): The OpenAI model to use for completions.
        tool_definitions (List[Dict]): List of tool definitions for function calling.
        tool_callables (Dict[str, Callable]): Mapping of tool names to callable functions.
        messages (List[Dict]): Conversation history maintained throughout the session.
        client (OpenAI): Initialized OpenAI client instance.
    """
    
    def __init__(self, model: str = None, tool_definitions: List[Dict] = None, 
                 tool_callables: Dict[str, Callable] = None, system_prompt: str = None, 
                 api_base: str = None, api_key: str = None):
        """
        Initialize the OpenAI agent with configuration parameters.
        
        Args:
            model (str, optional): Model name to use. Defaults to OPENAI_MODEL env var.
            tool_definitions (List[Dict], optional): List of tool function definitions.
            tool_callables (Dict[str, Callable], optional): Mapping of tool names to functions.
            system_prompt (str, optional): System message to initialize conversation.
            api_base (str, optional): Custom API base URL. Defaults to OPENAI_API_BASE env var.
            api_key (str, optional): API key for authentication. Defaults to OPENAI_API_KEY env var.
        """
        self.model = model or os.getenv("OPENAI_MODEL")
        self.tool_definitions = tool_definitions
        self.tool_callables = tool_callables
        self.messages = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})
        
        api_base_url = api_base or os.getenv("OPENAI_API_BASE") or "https://api.openai.com/v1"
        
        self.client = OpenAI(
            base_url=api_base_url,
            api_key=api_key or os.getenv("OPENAI_API_KEY")
        )

    def run(self, user_prompt: str, max_iterations: int = MAX_ITERATIONS):
        """
        Execute a conversation with the AI agent using non-streaming completion.
        
        This method processes the user's prompt through multiple iterations, handling
        tool calls and maintaining conversation context until a final response is reached
        or the maximum iteration limit is exceeded.
        
        Args:
            user_prompt (str): The user's input message to process.
            max_iterations (int, optional): Maximum number of iterations to attempt.
                Defaults to MAX_ITERATIONS environment variable or 25.
        
        Returns:
            str: The final response from the agent or an error message if the task
                could not be completed within the iteration limit.
        
        Raises:
            Exception: Catches and returns API errors as strings.
        """
        self.messages.append({"role": "user", "content": user_prompt})
        for i in range(int(max_iterations)):
            print(f"Iteration {i + 1}")
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=self.tool_definitions if self.tool_definitions else None,
                    temperature=1,
                    top_p=1,
                    max_tokens=4096
                )
                
                message = completion.choices[0].message
                self.messages.append({
                    "role": message.role,
                    "content": message.content,
                    "tool_calls": [tool_call.model_dump() for tool_call in message.tool_calls] if message.tool_calls else None
                })
                
                if not message.tool_calls:
                    return message.content or ""
                
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    if tool_name not in self.tool_callables:
                        print(f"Error: Tool '{tool_name}' not found.")
                        self.messages.append({
                            "role": "tool",
                            "content": f"Error: Tool '{tool_name}' not found.",
                            "tool_call_id": tool_call.id
                        })
                        continue
                    try:
                        print(f"Calling tool: {tool_name} with args: {tool_args}")
                        tool_output = self.tool_callables[tool_name](**tool_args)
                        print(f"Tool output: {tool_output}")
                        self.messages.append({
                            "role": "tool",
                            "content": str(tool_output),
                            "tool_call_id": tool_call.id
                        })
                    except Exception as e:
                        print(f"Error executing tool '{tool_name}': {e}")
                        self.messages.append({
                            "role": "tool",
                            "content": f"Error executing tool '{tool_name}': {e}",
                            "tool_call_id": tool_call.id
                        })
            except Exception as e:
                print(f"API error: {e}")
                return f"API error: {e}"
                
        return "The agent could not complete the task within the maximum number of iterations."

    def run_with_streaming(self, user_prompt: str, max_iterations: int = MAX_ITERATIONS):
        """
        Execute a conversation with the AI agent using streaming completion.
        
        This method processes the user's prompt with real-time streaming output,
        displaying content as it's generated. It handles reasoning content for
        compatible models and processes tool calls after streaming completion.
        
        Args:
            user_prompt (str): The user's input message to process.
            max_iterations (int, optional): Maximum number of iterations to attempt.
                Defaults to MAX_ITERATIONS environment variable or 25.
        
        Returns:
            str: The final response from the agent or an error message if the task
                could not be completed within the iteration limit.
        
        Raises:
            Exception: Catches and returns API errors as strings.
        """
        self.messages.append({"role": "user", "content": user_prompt})
        for i in range(int(max_iterations)):
            print(f"Iteration {i + 1}")
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=self.tool_definitions if self.tool_definitions else None,
                    temperature=1,
                    top_p=1,
                    max_tokens=4096,
                    stream=True
                )
                
                full_content = ""
                tool_calls = []
                current_message = {"role": "assistant", "content": ""}
                
                for chunk in completion:
                    reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
                    if reasoning:
                        print(reasoning, end="", flush=True)
                    
                    if chunk.choices[0].delta.content is not None:
                        content_chunk = chunk.choices[0].delta.content
                        full_content += content_chunk
                        print(content_chunk, end='', flush=True)
                    
                    if chunk.choices[0].delta.tool_calls:
                        for tool_call_delta in chunk.choices[0].delta.tool_calls:
                            while len(tool_calls) <= tool_call_delta.index:
                                tool_calls.append({
                                    "id": "",
                                    "type": "function",
                                    "function": {"name": "", "arguments": ""}
                                })
                            
                            if tool_call_delta.id:
                                tool_calls[tool_call_delta.index]["id"] = tool_call_delta.id
                            if tool_call_delta.function:
                                if tool_call_delta.function.name:
                                    tool_calls[tool_call_delta.index]["function"]["name"] = tool_call_delta.function.name
                                if tool_call_delta.function.arguments:
                                    tool_calls[tool_call_delta.index]["function"]["arguments"] += tool_call_delta.function.arguments
                    
                    if chunk.choices[0].delta.role:
                        current_message["role"] = chunk.choices[0].delta.role
                
                print()
                current_message["content"] = full_content
                
                if tool_calls:
                    current_message["tool_calls"] = tool_calls
                
                self.messages.append(current_message)
                
                if not tool_calls:
                    return full_content
                
                for tool_call in tool_calls:
                    tool_name = tool_call["function"]["name"]
                    tool_args = json.loads(tool_call["function"]["arguments"])
                    
                    if tool_name not in self.tool_callables:
                        print(f"Error: Tool '{tool_name}' not found.")
                        self.messages.append({
                            "role": "tool",
                            "content": f"Error: Tool '{tool_name}' not found.",
                            "tool_call_id": tool_call["id"]
                        })
                        continue
                    try:
                        print(f"Calling tool: {tool_name} with args: {tool_args}")
                        tool_output = self.tool_callables[tool_name](**tool_args)
                        print(f"Tool output: {tool_output}")
                        self.messages.append({
                            "role": "tool",
                            "content": str(tool_output),
                            "tool_call_id": tool_call["id"]
                        })
                    except Exception as e:
                        print(f"Error executing tool '{tool_name}': {e}")
                        self.messages.append({
                            "role": "tool",
                            "content": f"Error executing tool '{tool_name}': {e}",
                            "tool_call_id": tool_call["id"]
                        })
            except Exception as e:
                print(f"API error: {e}")
                return f"API error: {e}"
                
        return "The agent could not complete the task within the maximum number of iterations."
