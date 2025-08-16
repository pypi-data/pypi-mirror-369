import os
import sys
import datetime
import requests
import fnmatch
import re
import subprocess
import tomllib
from google.genai import types

from .ai_client import configure_api

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
# Development Scrap
en.txt
scrap.txt
combined.txt
"""

def generate_gitignore(user_files: list):
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
    print("Please specify a license. Choose from one of the popular options below:\n")
    for key, info in POPULAR_LICENSES.items():
        print(f"  - {key:<15} ({info['name']}): {info['keywords']}")
    print("\nExample: gencraft license mit")

def generate_license(license_type: str):
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
    lines = text.strip().split('\n')
    if len(lines) > 1 and lines[0].strip().startswith('```') and lines[-1].strip() == '```':
        return '\n'.join(lines[1:-1])
    return text.strip()

def _parse_gitignore(gitignore_content: str) -> set:
    patterns = set()
    for line in gitignore_content.splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            patterns.add(line)
    return patterns

def get_project_context():
    context = []
    ignore_patterns = _parse_gitignore(PYTHON_GITIGNORE_TEMPLATE)
    try:
        with open('.gitignore', 'r') as f:
            user_patterns = _parse_gitignore(f.read())
            ignore_patterns.update(user_patterns)
    except FileNotFoundError:
        pass
    ignore_patterns.update({'.git', 'LICENSE', 'README.md'})
    for root, dirs, files in os.walk("."):
        dirs[:] = [
            d for d in dirs
            if not any(fnmatch.fnmatch(d, pattern.rstrip('/')) for pattern in ignore_patterns)
        ]
        relative_path = os.path.relpath(root, ".")
        if relative_path != ".":
            context.append(f"Directory: {relative_path.replace(os.sep, '/')}/")
        for file in files:
            file_path = os.path.join(relative_path, file)
            if any(fnmatch.fnmatch(file_path, pattern) for pattern in ignore_patterns):
                continue
            if file == 'pyproject.toml':
                try:
                    with open(os.path.join(root, file), 'r') as f:
                        context.append(f"\n--- Contents of {file} ---\n{f.read()}\n")
                except Exception:
                    context.append(f"  - File: {file} (Could not read)")
            else:
                context.append(f"  - File: {file}")
    return "\n".join(context)

def _get_project_metadata():
    metadata = {
        "github_user": None, "github_repo": None, "pypi_name": None,
        "python_version": None, "license_type": None
    }
    try:
        remote_url = subprocess.check_output(["git", "remote", "get-url", "origin"], text=True).strip()
        match = re.search(r'(?:[:/])([^/]+)/([^/]+?)(?:\.git)?$', remote_url)
        if match:
            metadata["github_user"], metadata["github_repo"] = match.groups()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    try:
        with open("pyproject.toml", "rb") as f:
            pyproject_data = tomllib.load(f)
            project_info = pyproject_data.get("project", {})
            metadata["pypi_name"] = project_info.get("name")
            metadata["python_version"] = project_info.get("requires-python", "").strip('>=')
            for classifier in project_info.get("classifiers", []):
                if "License :: OSI Approved" in classifier:
                    metadata["license_type"] = classifier.split("::")[-1].strip().replace(" License", "")
                    break
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        pass
    return metadata

def generate_readme(user_prompt: str):
    print("🔎 Scanning project and gathering metadata...")
    project_context = get_project_context()
    metadata = _get_project_metadata()

    prompt_parts = [
        "You are an expert technical writer and open-source maintainer, specializing in creating professional and visually appealing README.md files.",
        "Your task is to generate a complete README for a software project based on the context and metadata provided.",
        "---",
        "**Style and Formatting Rules:**",
        "1.  **Badges are Mandatory:** Start the README with a block of relevant badges. Use the provided metadata to generate them.",
        "2.  **Structure is Key:** Follow this exact structure: Badges, Project Title, Short Description, Main Body (Features, Installation, Usage), Contributing, License.",
        "3.  **Use Emojis:** Use relevant emojis to make sections visually engaging (e.g., 🚀 for Features, 🛠️ for Installation).",
        "4.  **Code Blocks:** Use triple backticks (```) with language identifiers for all commands and code examples.",
    ]

    badge_instructions = ["---", "**Badge Generation Instructions:**", "Generate the complete markdown for a block of badges. Use the Shields.io (`https://img.shields.io`) format. Here are the patterns:"]
    if metadata.get("pypi_name"):
        pypi_name = metadata["pypi_name"]
        badge_instructions.append(f"- PyPI Version: `[![PyPI version](https://badge.fury.io/py/{pypi_name}.svg)](https://badge.fury.io/py/{pypi_name})`")
        badge_instructions.append(f"- Python Version: `[![Python Version](https://img.shields.io/pypi/pyversions/{pypi_name})](https://pypi.org/project/{pypi_name})`")

    if metadata.get("license_type"):
        license_type = metadata["license_type"]
        badge_instructions.append(f"- License: `[![License: {license_type}](https://img.shields.io/badge/License-{license_type.replace('-', '--')}-blue.svg)](https://opensource.org/licenses/{license_type})`")

    if metadata.get("github_user") and metadata.get("github_repo"):
        gh_user, gh_repo = metadata["github_user"], metadata["github_repo"]
        badge_instructions.append(f"- GitHub Stars: `[![GitHub stars](https://img.shields.io/github/stars/{gh_user}/{gh_repo})](https://github.com/{gh_user}/{gh_repo}/stargazers)`")
        badge_instructions.append(f"- GitHub Workflow Status: `[![Build Status](https://img.shields.io/github/actions/workflow/status/{gh_user}/{gh_repo}/publish-to-pypi.yml?branch=main)](https://github.com/{gh_user}/{gh_repo}/actions)`")

    prompt_parts.extend(badge_instructions)

    metadata_info = ["---", "**Provided Project Metadata:**"]
    for key, value in metadata.items():
        if value:
            metadata_info.append(f"- {key.replace('_', ' ').title()}: {value}")
    prompt_parts.extend(metadata_info)

    prompt_parts.extend([
        "---", "**User's High-Level Request:**", f"'{user_prompt}'",
        "---", "**Project File Structure & Context:**", project_context,
        "---", "Now, generate the complete, beautiful, badge-rich README.md file. Only return the raw Markdown content without any commentary or code fences."
    ])

    prompt = "\n".join(prompt_parts)

    print("⏳ Generating README.md with expert-level instructions...")
    
    try:
        client = configure_api()
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
        )
        readme_content = _strip_markdown_fences(response.text)
        with open("README.md", "w") as f:
            f.write(readme_content)
        print("✅ README.md generated successfully.")
    except Exception as e:
        print(f"Error generating README: {e}")
        sys.exit(1)