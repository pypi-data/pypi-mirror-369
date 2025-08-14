# Local Agent Toolkit

[![PyPI version](https://badge.fury.io/py/local-agent-toolkit.svg)](https://badge.fury.io/py/local-agent-toolkit)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A sophisticated AI agent toolkit that can use various tools to answer questions and perform tasks. The toolkit supports multiple AI providers including Ollama and OpenAI, and can be used both as a command-line tool and as a Python library.

## 🚀 Quick Start

### Installation

```bash
pip install local-agent-toolkit
```

### Command Line Usage

First, set up your environment configuration (see [Environment Setup](#environment-setup) below), then:

```bash
# Ask a question directly
local-agent "What files are in the current directory?"

# Interactive mode
local-agent

# With custom settings
local-agent "Analyze the code structure" --no-save --no-stream
```

### Python Library Usage

```python
from local_agent_toolkit import run_agent_with_question

# Simple usage
result, messages = run_agent_with_question("List all Python files in the project")
print(result)

# With custom options
result, messages = run_agent_with_question(
    question="What's the weather like?",
    save_messages=False,
    stream=False
)
```

## ✨ Features

- **🤖 Multiple AI Agent Support**: Choose between Ollama and OpenAI agents
- **🛠️ Rich Tool Integration**: File operations, internet search, shell commands, and more
- **💻 Dual Interface**: Command-line tool and Python library
- **📝 Conversation History**: Automatic saving with customizable options
- **⚙️ Flexible Configuration**: Environment-based configuration for different AI providers
- **🔄 Streaming Support**: Real-time response streaming (Ollama)
- **🐍 Python 3.8+**: Compatible with modern Python versions

## 📦 Installation Options

### From PyPI (Recommended)
```bash
pip install local-agent-toolkit
```

### From Source
```bash
git clone https://github.com/technicalheist/local-agent-toolkit.git
cd local-agent-toolkit
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/technicalheist/local-agent-toolkit.git
cd local-agent-toolkit
pip install -e ".[dev]"
```

## Project Structure

```
agent/
├── app.py                    # Main application entry point
├── agents/                   # AI agent implementations
│   ├── OllamaAgent.py       # Ollama-based agent
│   └── OpenAIAgent.py       # OpenAI-based agent
├── helper/                   # Helper modules directory
│   ├── __init__.py          # Package initialization
│   ├── agent.py             # Core agent logic
│   ├── tools.py             # Tool implementations
│   ├── tools_definition.py  # Tool definitions
│   └── tool_call.py         # Function for running the agent
├── __test__/                 # Test files
│   ├── ollama_agent_test.py  # Tests for Ollama agent
│   └── openai_agent_test.py  # Tests for OpenAI agent
├── requirements.txt          # Python dependencies
├── .env                     # Environment variables
└── README.md               # This file
```

## Environment Setup

On your first run, the toolkit will guide you through an interactive setup process where you can:
- Choose between Ollama (local) and OpenAI agents
- Configure the necessary settings (model, API keys, base URLs, etc.)
- Save your configuration either locally or globally

```
$ local-agent "What files are in the current directory?"

========================================================
🚀 Local Agent Toolkit - First-time Setup
========================================================

Welcome! Let's set up your environment for Local Agent Toolkit.
This will help you configure the AI agent you want to use.

First, choose which AI agent you want to use:
1. Ollama (local LLM, requires Ollama running)
2. OpenAI (requires API key)

Enter your choice (1 or 2): 2

Enter your OpenAI API key: sk-...

Enter OpenAI API base URL [https://api.openai.com/v1]: 

Enter OpenAI model name [gpt-4]: 

Where would you like to save this configuration?
1. Current directory (.env file in your working directory)
2. Global user configuration (~/.config/local-agent-toolkit/.env)

Enter your choice (1 or 2): 2

✅ Configuration saved successfully!
📁 Configuration file: /home/user/.config/local-agent-toolkit/.env

🔄 Configuration loaded and ready to use!
========================================================
```

You can also manually configure the toolkit by:

1. Creating a `.env` file in your working directory
2. Setting environment variables in your terminal session
3. Creating a global configuration in `~/.config/local-agent-toolkit/.env`

Example `.env` file contents:
```
CURRENT_AGENT=OLLAMA
OLLAMA_MODEL=llama3.1
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_HOST=http://localhost:11434
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in your project root (copy from `.env.example`):

```bash
# Agent Selection
CURRENT_AGENT=OLLAMA  # or OPENAI

# Ollama Configuration  
OLLAMA_MODEL=llama3.1
OLLAMA_BASE_URL=http://localhost:11434

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Optional Settings
MAX_ITERATIONS=25
WORK_DIRECTORY=./
LOG_LEVEL=INFO
```

### Supported AI Providers

#### 🦙 Ollama Agent
- **Purpose**: Local AI models with privacy
- **Requirements**: Ollama server running locally
- **Models**: Any Ollama-compatible model (llama3.1, codellama, etc.)
- **Benefits**: Privacy, no API costs, offline usage

#### 🤖 OpenAI Agent  
- **Purpose**: Cloud-based AI with latest models
- **Requirements**: OpenAI API key
- **Models**: GPT-4, GPT-3.5-turbo, etc.
- **Benefits**: High performance, latest capabilities

## 🛠️ Available Tools

The agents have access to these built-in tools:

- **📁 File Operations**: `list_files`, `read_file`, `write_file`
- **🔍 Pattern Search**: `list_files_by_pattern`
- **🌐 Internet Search**: `ask_any_question_internet`
- **💻 Shell Commands**: `execute_shell_command`
- **📂 Directory Operations**: `mkdir`

## 📚 Usage Examples

### Command Line Interface

```bash
# Basic usage
local-agent "What Python files are in this project?"

# Interactive mode with conversation history
local-agent

# Disable features
local-agent "Analyze code" --no-save --no-stream

# Custom message file
local-agent "Help me debug" --messages custom_conversation.json
```

### Python Library

```python
# Basic usage
from local_agent_toolkit import run_agent_with_question

result, messages = run_agent_with_question(
    "Create a Python script that lists all files"
)

# Advanced usage with options
result, messages = run_agent_with_question(
    question="What's the project structure?",
    save_messages=True,
    messages_file="project_analysis.json",
    stream=False
)

# Using specific agents
from local_agent_toolkit import OllamaAgent, OpenAIAgent
from local_agent_toolkit.helper.tools_definition import tools

# Create Ollama agent
ollama_agent = OllamaAgent(
    tool_definitions=tools,
    tool_callables=available_functions
)

# Create OpenAI agent  
openai_agent = OpenAIAgent(
    tool_definitions=tools,
    tool_callables=available_functions
)
```

### Environment Management

#### Option 1: Global .env file
```bash
# Create .env in your project root
cp .env.example .env
# Edit .env with your settings
```

#### Option 2: Per-project configuration
```python
import os
from dotenv import load_dotenv

# Load from specific path
load_dotenv('/path/to/your/project/.env')

# Or set programmatically
os.environ['CURRENT_AGENT'] = 'OPENAI'
os.environ['OPENAI_API_KEY'] = 'your_key_here'

from local_agent_toolkit import run_agent_with_question
```

#### Option 3: Docker/Container deployment
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install local-agent-toolkit

# Set environment variables
ENV CURRENT_AGENT=OLLAMA
ENV OLLAMA_BASE_URL=http://ollama-server:11434
ENV OLLAMA_MODEL=llama3.1

COPY . .
CMD ["local-agent"]
```

## 🔧 Development

### Running Tests
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest __test__/

# Run specific tests
pytest __test__/ollama_agent_test.py
pytest __test__/openai_agent_test.py
```

### Building for Distribution
```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to PyPI (maintainers only)
twine upload dist/*
```

## 📝 Project Structure

```
local-agent-toolkit/
├── app.py                    # Command-line interface
├── agents/                   # AI agent implementations
│   ├── OllamaAgent.py       # Ollama-based agent
│   └── OpenAIAgent.py       # OpenAI-based agent
├── helper/                   # Core library modules
│   ├── __init__.py          # Library exports
│   ├── agent.py             # Base agent logic
│   ├── tools.py             # Tool implementations
│   ├── tools_definition.py  # Tool schemas
│   └── tool_call.py         # Main execution function
├── __test__/                 # Test suite
├── requirements.txt          # Dependencies
├── setup.py                 # Package configuration
├── pyproject.toml           # Modern packaging config
└── .env.example             # Environment template
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local AI model serving
- [OpenAI](https://openai.com/) for API access to advanced models
- The Python community for excellent tooling and libraries

## 📞 Support

- 📧 Issues: [GitHub Issues](https://github.com/technicalheist/local-agent-toolkit/issues)
- 📖 Documentation: [GitHub Repository](https://github.com/technicalheist/local-agent-toolkit)
- 💬 Discussions: [GitHub Discussions](https://github.com/technicalheist/local-agent-toolkit/discussions)

Use command-line flags for more control:

```bash
# Ask a question using the --question flag
python app.py --question "What files are in the helper directory?"

# Don't save the conversation history
python app.py --question "Get current time" --no-save

# Save to a custom file
python app.py --question "Create a test directory" --messages-file "my_conversation.json"
```

## Command-Line Options

- `question` (positional): The question to ask the agent
- `-q, --question`: Alternative way to specify the question
- `--no-save`: Don't save the conversation history to a file
- `--messages-file`: Custom filename for saving conversation history (default: `messages.json`)
- `-h, --help`: Show help message

## Examples

```bash
# Interactive mode
python app.py

# Simple question
python app.py "What's the weather like?"

# With custom options
python app.py -q "List directory contents" --messages-file "dir_check.json"

# Without saving conversation
python app.py "Quick calculation: 2+2" --no-save
```

## Available Tools

The agent has access to various tools including:

- **File Operations**: `list_files`, `read_file`, `write_file`, `mkdir`
- **Pattern Matching**: `list_files_by_pattern`
- **Internet Search**: `ask_any_question_internet`
- **Shell Commands**: `execute_shell_command`

## Conversation History

By default, all conversations are saved to `messages.json`. You can:
- Use `--no-save` to skip saving
- Use `--messages-file` to specify a custom filename
- View the conversation history in JSON format

## Notes

- The agent can handle complex multi-step tasks
- **Multiple AI Providers**: Choose between Ollama (local) and OpenAI (cloud) agents based on your needs
- Conversations include tool calls and responses for full transparency
- The JSON conversation files can be used for debugging or analysis
- The agent will continue working until it completes the task or reaches the maximum iteration limit
- Both agent types support the same tool set and functionality
