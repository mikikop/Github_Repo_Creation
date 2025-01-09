import os
import subprocess


# Function to create a .gitignore file
def create_gitignore(project_path):
    gitignore_content = """# Python-related
*.py[cod]
__pycache__/
*.so

# Environment Variables
.env
.config

# Virtual environments
.venv/
env/
ENV/
venv/

# IDEs and editors
.vscode/
.idea/
*.swp
*.swo
*.iml

# Poetry files
poetry.lock

# Operating system files
.DS_Store
Thumbs.db

# Logs and databases
*.log
*.sqlite3
*.db

# Django-related
# Django migration files (keep migrations if needed for versioning)
*.pyc

# Local settings (such as secret keys and local configuration)
local_settings.py
settings_local.py

# Packages #
############
# it's better to unpack these files and commit the raw source
# git has its own built in compression methods
*.7z
*.dmg
*.gz
*.iso
*.jar
*.rar
*.tar
*.zip

# Database files
*.sqlite3
db.sqlite3

# Media and static files
/media/
/static/

# Django secret key file (optional, if used)
.secret_key

# Tests
.coverage
.tox/

# Git-related
*.orig
*.rej

# Qodo
*.qodo
"""
    gitignore_path = os.path.join(project_path, ".gitignore")
    with open(gitignore_path, "w") as file:
        file.write(gitignore_content)
    print(f"Created .gitignore file at {gitignore_path}")

    # Add remote and push changes to GitHub
    subprocess.run(["git", "add", ".gitignore"])
    subprocess.run(['git', 'commit', '-m', 'Add .gitignore file'])
    subprocess.run(["git", "push"])


# Main logic
def main():
    # Get the current working directory
    project_path = os.getcwd()

    # Create .gitignore
    create_gitignore(project_path)


if __name__ == "__main__":
    main()