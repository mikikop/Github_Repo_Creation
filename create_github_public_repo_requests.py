import os
import subprocess
import requests
import shutil


def get_script_directory():
    """Get the directory where the current script is located"""
    return os.path.dirname(os.path.abspath(__file__))


def clean_git_artifacts():
    """Clean up git-related artifacts from failed attempts"""
    # Remove .git directory if it exists
    if os.path.isdir(".git"):
        print("Cleaning up existing .git directory...")
        shutil.rmtree(".git")

    # Remove any existing git config files
    git_config = ".git*"
    for item in os.listdir():
        if item.startswith(".git"):
            if os.path.isfile(item):
                os.remove(item)
                print(f"Removed {item}")


def create_gitignore(project_path):
    """Create .gitignore file first, before any git operations"""
    # Get the directory where both scripts are located
    script_dir = get_script_directory()
    gitignore_script = os.path.join(script_dir, "create_gitignore.py")

    # Check if create_gitignore.py exists
    if not os.path.exists(gitignore_script):
        raise FileNotFoundError(f"create_gitignore.py not found at {gitignore_script}")

    # Check if .gitignore already exists
    gitignore_path = os.path.join(project_path, ".gitignore")
    if os.path.exists(gitignore_path):
        user_input = input(".gitignore already exists. Do you want to overwrite it? (y/n): ")
        if user_input.lower() != 'y':
            print("Keeping existing .gitignore file")
            return
        print("Overwriting existing .gitignore file")

    # Run create_gitignore.py with the correct path
    try:
        subprocess.run(["python", gitignore_script], check=True)
        print("Created .gitignore using create_gitignore.py")
    except subprocess.CalledProcessError as e:
        print(f"Error creating .gitignore: {e}")
        raise


def check_github_repo_exists(repo_name, headers):
    """Check if repository already exists on GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}"
    response = requests.get(url, headers=headers)
    return response.status_code == 200


# GitHub credentials
GITHUB_USERNAME = input("Enter your GitHub username: ")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("GitHub token is not set. Please set the GITHUB_TOKEN environment variable.")
    exit(1)

# GitHub API URL to create a repository
GITHUB_API_URL = "https://api.github.com/user/repos"

# Headers for GitHub API request
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

# Prompt user for the new repository name
while True:
    repo_name = input("Enter the name of the new GitHub repository: ")
    if check_github_repo_exists(repo_name, headers):
        print(f"Repository '{repo_name}' already exists on GitHub!")
        continue_anyway = input("Do you want to try a different name? (y/n): ")
        if continue_anyway.lower() == 'y':
            continue
        else:
            exit(1)
    break

repo_description = input("Enter a description for the repository: ")

# Clean up any existing git artifacts
clean_git_artifacts()

# Payload to send to GitHub API for repository creation
data = {
    "name": repo_name,
    "description": repo_description,
    "private": False,  # Set to True if you want a private repo
}

# Use requests to make the API request
try:
    response = requests.post(GITHUB_API_URL, json=data, headers=headers)
    response.raise_for_status()
    print(f"Repository '{repo_name}' created successfully on GitHub!")
except requests.exceptions.RequestException as e:
    print(f"Error creating repository: {e}")
    if response.status_code == 422:
        print("This might mean the repository already exists or the name is invalid.")
    exit(1)

# Create .gitignore first
project_path = os.getcwd()
try:
    create_gitignore(project_path)
except Exception as e:
    print(f"Error during .gitignore creation: {e}")
    exit(1)

# Initialize the local Git repository
print("Initializing local Git repository...")
try:
    subprocess.run(["git", "init"], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error initializing git repository: {e}")
    exit(1)

# Create a README file if none exists
readme_path = "README.md"
if not os.path.exists(readme_path):
    print(f"Creating {readme_path}...")
    with open(readme_path, "w") as f:
        f.write(f"# {repo_name}\n\n{repo_description}")

# Create and switch to main branch
print("Creating and switching to 'main' branch...")
try:
    subprocess.run(["git", "checkout", "-b", "main"], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error creating main branch: {e}")
    exit(1)

# Add all files, commit, and push to GitHub
print("Adding files according to .gitignore rules...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error during git add/commit: {e}")
    exit(1)

# Set the remote origin and push to GitHub
remote_url = f"git@github.com:{GITHUB_USERNAME}/{repo_name}.git"
try:
    subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error adding remote: {e}")
    exit(1)

print(f"Pushing to remote repository: {remote_url}")
try:
    subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
    print(f"Project successfully pushed to GitHub at {remote_url}")
except subprocess.CalledProcessError as e:
    print(f"Error pushing to GitHub: {e}")
    print("This might be due to SSH key issues or network problems.")
    exit(1)