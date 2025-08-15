import subprocess
import tempfile
from .git_utils import get_git_editor

def open_in_editor(message: str) -> str:
    """
    Opens the given message in the user's default Git editor.

    Args:
        message (str): The initial message to place in the editor.

    Returns:
        str: The message after being edited by the user.
             Returns an empty string if the user deletes all content.
    """
    editor_cmd = get_git_editor()
    
    # Create a temporary file to store the commit message
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".txt") as tf:
        tf.write(message)
        temp_file_path = tf.name

    try:
        # Command might include arguments, so we use shell=True for simplicity here.
        # A more robust solution would parse the command string.
        subprocess.run(f"{editor_cmd} {temp_file_path}", shell=True, check=True)

        # Read the potentially modified content back from the file
        with open(temp_file_path, 'r') as tf:
            edited_message = tf.read().strip()
    finally:
        # Clean up the temporary file
        import os
        os.remove(temp_file_path)

    return edited_message