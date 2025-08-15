import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

def configure_api():
    """Loads API key from .env or environment and configures the Gemini client."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("--- Welcome to DiffCraft! API Key Not Found ---\n")
        print("Please configure your API key:")
        print("\nMethod 1 (recommended): Create a `.env` file with:")
        print('    GEMINI_API_KEY="YOUR_API_KEY_HERE"\n')
        print("Method 2: Set an environment variable (e.g. macOS/Linux):")
        print('    export GEMINI_API_KEY="YOUR_API_KEY_HERE"\n')
        print("Get your key here: https://aistudio.google.com/app/apikey\n")
        raise ValueError("API key configuration not found.")
    return genai.Client(api_key=api_key)

def generate_commit_message(
    diff: str,
    commit_type: str = None,
    history: str = None,
    language: str = 'English'
) -> str:
    """
    Generates a Git commit message using Gemini-2.5-Flash-Lite with thinking disabled.
    """
    client = configure_api()

    prompt_parts = [
        "As an expert software developer, write a high-quality Git commit message."
    ]
    if commit_type:
        prompt_parts.append(f"The commit message must have the type '{commit_type}'.")
    else:
        prompt_parts.append("Automatically detect the type from: feat, fix, docs, style, refactor, test, chore.")

    prompt_parts.append(f"The commit message must be written in {language}.")
    prompt_parts.append("Analyze the following git diff and produce a concise commit message following Conventional Commits.")
    
    if history:
        prompt_parts.append("\nRecent commit history for context:")
        prompt_parts.append(f"```\n{history}\n```")

    prompt_parts.append("\nGit Diff:")
    prompt_parts.append(f"```diff\n{diff}\n```")
    prompt_parts.append("\nOnly return the raw commit message—no commentary or 'git commit -m'.")

    prompt = "\n".join(prompt_parts)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", # Highest RPD for free tier;
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)  # disables thinking
            ),
        )
        return response.text.strip()
    except Exception as e:
        return f"Error generating commit message: {e}"