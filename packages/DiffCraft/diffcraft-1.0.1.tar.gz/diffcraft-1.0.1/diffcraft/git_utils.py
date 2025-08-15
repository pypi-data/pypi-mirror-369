import subprocess
import sys
import os

def get_staged_diff():
    """
    Retrieves the staged changes (diff) from the Git repository.

    Returns:
        str: The git diff output, or None if an error occurs or the diff is empty.
    """
    try:
        command = ["git", "diff", "--cached"]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        if result.stdout:
            return result.stdout
        else:
            print("No staged changes found. Use 'git add' to stage your files.")
            return None
    except FileNotFoundError:
        print("Error: 'git' command not found. Is Git installed and in your PATH?")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running git diff: {e.stderr}")
        sys.exit(1)

def commit(message: str):
    """
    Commits the staged changes with the given message.

    Args:
        message (str): The commit message.
    """
    try:
        subprocess.run(
            ["git", "commit", "-m", message],
            check=True,
            encoding='utf-f'
        )
        print("✅ Commit created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during commit: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def get_git_editor():
    """
    Retrieves the user's configured Git editor.

    Returns:
        str: The command for the Git editor. Defaults to 'vim' or 'notepad'.
    """
    try:
        editor = subprocess.run(
            ["git", "var", "GIT_EDITOR"],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        return editor
    except (FileNotFoundError, subprocess.CalledProcessError):
        # Fallback if git command fails or variable is not set
        return os.environ.get('EDITOR', 'vim' if os.name != 'nt' else 'notepad')
    

def get_commit_history(n: int):
    """
    Retrieves the subject lines of the last n commits.

    Args:
        n (int): The number of commits to retrieve.

    Returns:
        str: A formatted string of the last n commit subjects, or None.
    """
    if n <= 0:
        return None
    try:
        command = ["git", "log", f"-{n}", "--pretty=format:%s"]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        if result.stdout:
            return result.stdout
        return None
    except Exception:
        # Silently fail if git log fails, it's not a critical error
        print("Warning: Could not retrieve commit history.")
        return None

def add_files(files: list):
    """
    Runs `git add` on the specified list of files.

    Args:
        files (list): A list of file paths to stage.
    """
    try:
        command = ["git", "add"] + files
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Staged {len(files)} file(s).")
    except subprocess.CalledProcessError as e:
        print(f"Error staging files: {e.stderr}")
        sys.exit(1)