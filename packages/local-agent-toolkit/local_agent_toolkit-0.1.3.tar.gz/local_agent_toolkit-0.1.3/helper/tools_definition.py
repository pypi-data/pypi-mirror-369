tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Lists all files in a given directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "The path to the directory.",
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "If True, lists files in subdirectories as well.",
                    },
                },
                "required": ["directory"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads the content of a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The path to the file.",
                    },
                },
                "required": ["filepath"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Writes content to a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The path to the file.",
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file.",
                    },
                },
                "required": ["filepath", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files_by_pattern",
            "description": "Lists files in a given directory that match a regex pattern.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "The path to the directory.",
                    },
                    "pattern": {
                        "type": "string",
                        "description": "The regex pattern to match file names.",
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "If True, lists files in subdirectories as well.",
                    },
                },
                "required": ["directory", "pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ask_any_question_internet",
            "description": "Sends a question to an external internet-based API and returns the response text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question string to send to the API for answering.",
                    },
                    "vendor": {
                        "type": "string",
                        "description": 'The name of the vendor/service to use for answering the question. Defaults to "Perplexity".',
                    },
                },
                "required": ["question"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mkdir",
            "description": "Create a directory at the specified path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path of the directory to create.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_shell_command",
            "description": "Execute a shell command and return the output.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute.",
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "The directory to execute the command in. If not provided, uses the current working directory.",
                    },
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sqlite_execute_sql",
            "description": "Executes an SQL statement on a SQLite database and returns the result. Default database path is 'database/database.db'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "The SQL statement to execute.",
                    },
                    "params": {
                        "type": ["array", "null"],
                        "description": "Parameters for parameterized queries (optional).",
                    },
                    "db_path": {
                        "type": "string",
                        "description": "Path to the SQLite database file (optional). Defaults to 'database/database.db'.",
                    },
                },
                "required": ["sql"],
            },
        },
    },
]
