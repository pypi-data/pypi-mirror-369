import os
import sys
import datetime
import requests
from .ai_client import configure_api, generate_commit_message # Re-using the AI client

POPULAR_LICENSES = {
    "mit": {"name": "MIT License", "keywords": "Permissive, simple, short."},
    "apache-2.0": {"name": "Apache License 2.0", "keywords": "Permissive, patent grant, detailed."},
    "gpl-3.0": {"name": "GNU GPLv3", "keywords": "Strong copyleft, requires source sharing."},
    "agpl-3.0": {"name": "GNU AGPLv3", "keywords": "Network copyleft, for web services."},
    "mpl-2.0": {"name": "Mozilla Public License 2.0", "keywords": "File-level copyleft, mix with other licenses."},
    "bsd-3-clause": {"name": "BSD 3-Clause License", "keywords": "Permissive, simple, non-endorsement clause."},
    "isc": {"name": "ISC License", "keywords": "Permissive, simpler than MIT, functional equivalent."},
    "unlicense": {"name": "The Unlicense", "keywords": "Public domain dedication, no restrictions."},
}

PYTHON_GITIGNORE_TEMPLATE = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.idea/
.vscode/
"""

def generate_gitignore(user_files: list):
    """Generates or updates the .gitignore file."""
    content = ""
    gitignore_path = ".gitignore"

    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            content = f.read()
        print("Found existing .gitignore. Appending new rules.")
    
    if PYTHON_GITIGNORE_TEMPLATE.strip() not in content:
        content += "\n" + PYTHON_GITIGNORE_TEMPLATE

    if user_files:
        user_section = "\n# User Added\n"
        if user_section.strip() not in content:
             content += user_section
        for item in user_files:
            if item not in content:
                content += f"{item}\n"

    with open(gitignore_path, 'w') as f:
        f.write(content.strip())
    
    print("✅ .gitignore has been created/updated.")

def list_licenses():
    """Displays a list of available licenses."""
    print("Please specify a license. Choose from one of the popular options below:\n")
    for key, info in POPULAR_LICENSES.items():
        print(f"  - {key:<15} ({info['name']}): {info['keywords']}")
    print("\nExample: gencraft license mit")

def generate_license(license_type: str):
    """Fetches and creates a LICENSE file."""
    license_key = license_type.lower()
    if license_key not in POPULAR_LICENSES:
        print(f"Error: License '{license_type}' is not recognized.")
        list_licenses()
        sys.exit(1)

    try:
        author_name = input("Enter the author's full name: ")
        if not author_name:
            print("Author name cannot be empty. Aborting.")
            sys.exit(1)

        print(f"⏳ Fetching {POPULAR_LICENSES[license_key]['name']}...")
        response = requests.get(f"https://api.github.com/licenses/{license_key}")
        response.raise_for_status()
        
        license_data = response.json()
        license_text = license_data["body"]

        # Replace placeholders
        current_year = str(datetime.date.today().year)
        final_text = license_text.replace("[year]", current_year)
        final_text = final_text.replace("[fullname]", author_name)
        
        with open("LICENSE", "w") as f:
            f.write(final_text)

        print("✅ LICENSE file created successfully.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching license from GitHub API: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)



def _strip_markdown_fences(text: str) -> str:
    """
    Removes Markdown code fences (```) from the start and end of a string.
    Handles optional language identifiers like ```markdown.
    """
    lines = text.strip().split('\n')
    
    # Check if the first line starts with ``` and the last line is ```
    if len(lines) > 1 and lines[0].strip().startswith('```') and lines[-1].strip() == '```':
        # Return the content between the fences
        return '\n'.join(lines[1:-1])
    
    # If no fences are found, return the original (but stripped) text
    return text.strip()

def get_project_context():
    """
    Scans the repository to build a concise context for the AI.
    This is the key to avoiding token limits.
    """
    context = []
    ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build'}
    ignore_files = {'LICENSE', 'README.md'}
    
    for root, dirs, files in os.walk("."):
        # Remove ignored directories from traversal
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        # Add directory structure
        relative_path = os.path.relpath(root, ".")
        if relative_path != ".":
            context.append(f"Directory: {relative_path.replace(os.sep, '/')}/")

        for file in files:
            if file in ignore_files:
                continue

            file_path = os.path.join(root, file)
            # For key config files, add their full content
            if file == 'pyproject.toml':
                with open(file_path, 'r') as f:
                    context.append(f"\n--- Contents of {file} ---\n{f.read()}\n")
            # For other files, just list them to show they exist
            else:
                context.append(f"  - File: {file}")

    return "\n".join(context)


def generate_readme(user_prompt: str):
    """Generates a README.md file using the AI."""
    print("🔎 Scanning project structure to build context...")
    project_context = get_project_context()

    prompt_parts = [
        "You are an expert technical writer. Your task is to generate a high-quality README.md file for a software project.",
        "Analyze the following project structure and file overview to understand what the project does.",
        f"The user has provided the following high-level request: '{user_prompt}'",
        "Based on all this information, generate a complete README.md file in Markdown format.",
        "The README should be professional, clear, and include sections like Project Title, Description, Installation, Usage, and Contributing, if applicable.",
        "\n--- Project Context ---\n",
        project_context,
        "\n--- End of Context ---\n",
        "Now, please generate the complete README.md file. Only return the raw Markdown content."
    ]
    
    prompt = "\n".join(prompt_parts)

    print("⏳ Generating README.md with AI...")
    
    try:
        client = configure_api()
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        readme_content = response.text.strip()
        
        with open("README.md", "w") as f:
            f.write(readme_content)

        print("✅ README.md generated successfully.")

    except Exception as e:
        print(f"Error generating README: {e}")
        sys.exit(1)