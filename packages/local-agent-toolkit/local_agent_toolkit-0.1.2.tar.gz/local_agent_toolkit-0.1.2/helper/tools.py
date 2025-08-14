import os
import re
import json
import requests
import subprocess
from dotenv import load_dotenv


def list_files(directory, recursive=False):
    """
    Lists all files in a given directory.

    Args:
      directory: The path to the directory.
      recursive: If True, lists files in subdirectories as well.

    Returns:
      A list of file paths, or an error message if the directory does not exist.
    """
    if not os.path.isdir(directory):
        return f"Error: Directory '{directory}' not found."

    try:
        file_list = []
        for entry in os.scandir(directory):
            if entry.is_file():
                file_list.append(entry.path)
            elif entry.is_dir() and recursive:
                file_list.extend(list_files(entry.path, recursive=True))
        return file_list
    except Exception as e:
        return f"Error listing files in '{directory}': {e}"


def read_file(filepath):
    """
    Reads the content of a file.

    Args:
      filepath: The path to the file.

    Returns:
      The content of the file as a string, or an error message if the file doesn't exist.
    """
    if not os.path.exists(filepath):
        return f"Error: File '{filepath}' not found."
    try:
        with open(filepath, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file '{filepath}': {e}"


def write_file(filepath, content):
    """
    Writes content to a file.

    Args:
      filepath: The path to the file.
      content: The content to write to the file.

    Returns:
        A success message or an error message.
    """
    try:
        with open(filepath, "w") as f:
            f.write(content)
        return f"File '{filepath}' written successfully."
    except Exception as e:
        return f"Error writing to file '{filepath}': {e}"


def list_files_by_pattern(directory, pattern, recursive=False):
    """
    Lists files in a given directory that match a regex pattern.

    Args:
      directory: The path to the directory.
      pattern: The regex pattern to match file names.
      recursive: If True, lists files in subdirectories as well.

    Returns:
      A list of file paths that match the pattern, or an error message if the directory does not exist.
    """
    if not os.path.isdir(directory):
        return f"Error: Directory '{directory}' not found."

    try:
        file_list = []
        for entry in os.scandir(directory):
            if entry.is_file() and re.search(pattern, entry.name):
                file_list.append(entry.path)
            elif entry.is_dir() and recursive:
                file_list.extend(list_files_by_pattern(entry.path, pattern, recursive=True))
        return file_list
    except Exception as e:
        return f"Error listing files by pattern in '{directory}': {e}"


def ask_any_question_internet(question, vendor="Perplexity"):
    """
    Sends a question to an external internet-based API and returns the response text.

    Args:
        question (str): The question string to send to the API for answering.
        vendor (str, optional): The name of the vendor/service to use for answering the question.
            Defaults to "Perplexity".

    Returns:
        The response text from the API or an error message.
    """
    # Load .env file from the project root directory
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    base_url = os.getenv("API_BASE_URL")
    if not base_url:
        return "Error: API_BASE_URL not set in environment."
    url = base_url.rstrip("/") + "/ask" + vendor

    payload = json.dumps({"question": question})
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"


def mkdir(path):
    """
    Create a directory at the specified path.

    Args:
        path (str): The path of the directory to create.

    Returns:
        bool: True if created or already exists, or error string if failed.
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        return str(e)


def execute_shell_command(command, working_directory=None):
    """
    Execute a shell command and return the output.

    Args:
        command (str): The shell command to execute.
        working_directory (str, optional): The directory to execute the command in.
            If None, uses the current working directory.

    Returns:
        dict: A dictionary containing 'stdout', 'stderr', 'return_code', and 'success'.
    """
    try:
        if working_directory and not os.path.isdir(working_directory):
            return {
                "stdout": "",
                "stderr": f"Error: Directory '{working_directory}' not found.",
                "return_code": 1,
                "success": False
            }
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=working_directory,
            timeout=30
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
            "success": result.returncode == 0
        }
    
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Error: Command timed out after 30 seconds.",
            "return_code": 124,
            "success": False
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Error executing command: {e}",
            "return_code": 1,
            "success": False
        }
