import os
import subprocess
import httpx
import shutil
from typing import Optional


def get_script_directory() -> str:
    """Get the directory where the current script is located"""
    return os.path.dirname(os.path.abspath(__file__))


def clean_git_artifacts():
    """Clean up git-related artifacts from failed attempts"""
    if os.path.isdir(".git"):
        print("Cleaning up existing .git directory...")
        shutil.rmtree(".git")

    for item in os.listdir():
        if item.startswith(".git"):
            if os.path.isfile(item):
                os.remove(item)
                print(f"Removed {item}")


def create_gitignore(project_path: str) -> None:
    """
    Create a .gitignore file from template

    Args:
        project_path: Path where .gitignore should be created

    Raises:
        FileNotFoundError: If template file is not found
    """
    script_dir = get_script_directory()
    gitignore_template_path = os.path.join(script_dir, ".gitignore_template")
    gitignore_path = os.path.join(project_path, ".gitignore")

    # Check if .gitignore already exists
    if os.path.exists(gitignore_path):
        user_input = input(".gitignore already exists. Do you want to overwrite it? (y/n): ")
        if user_input.lower() != 'y':
            print("Keeping existing .gitignore file")
            return

    # Check if template exists
    if not os.path.exists(gitignore_template_path):
        raise FileNotFoundError(f".gitignore_template not found at {gitignore_template_path}")

    # Create .gitignore from template
    try:
        with open(gitignore_template_path, "r") as template:
            gitignore_content = template.read()
        with open(gitignore_path, "w") as file:
            file.write(gitignore_content)
        print(f"Created .gitignore file at {gitignore_path}")
    except IOError as e:
        print(f"Error writing .gitignore file: {e}")
        raise


def check_github_repo_exists(client: httpx.Client, username: str, repo_name: str, headers: dict) -> bool:
    """Check if repository already exists on GitHub"""
    url = f"https://api.github.com/repos/{username}/{repo_name}"
    response = client.get(url, headers=headers)
    return response.status_code == 200


def setup_git_repository(repo_name: str, repo_description: str) -> None:
    """Initialize git repository and create initial files"""
    # Create README if it doesn't exist
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        print(f"Creating {readme_path}...")
        with open(readme_path, "w") as f:
            f.write(f"# {repo_name}\n\n{repo_description}")

    # Initialize git repository
    print("Initializing local Git repository...")
    subprocess.run(["git", "init"], check=True)

    # Create and switch to main branch
    print("Creating and switching to 'main' branch...")
    subprocess.run(["git", "checkout", "-b", "main"], check=True)


def main():
    # Get GitHub credentials
    github_username = input("Enter your GitHub username: ")
    github_token = os.getenv("GITHUB_TOKEN")

    if not github_token:
        print("GitHub token is not set. Please set the GITHUB_TOKEN environment variable.")
        exit(1)

    # Setup API request
    github_api_url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    # Create HTTP client
    with httpx.Client() as client:
        # Get repository details
        while True:
            repo_name = input("Enter the name of the new GitHub repository: ")
            if check_github_repo_exists(client, github_username, repo_name, headers):
                print(f"Repository '{repo_name}' already exists on GitHub!")
                if input("Do you want to try a different name? (y/n): ").lower() != 'y':
                    exit(1)
                continue
            break

        repo_description = input("Enter a description for the repository: ")

        # Clean up any existing git artifacts
        clean_git_artifacts()

        # Create repository on GitHub
        data = {
            "name": repo_name,
            "description": repo_description,
            "private": False,
        }

        try:
            response = client.post(github_api_url, json=data, headers=headers)
            response.raise_for_status()
            print(f"Repository '{repo_name}' created successfully on GitHub!")
        except httpx.HTTPError as e:
            print(f"Error creating repository: {e}")
            if response.status_code == 422:
                print("This might mean the repository already exists or the name is invalid.")
            exit(1)

    # Create .gitignore
    project_path = os.getcwd()
    try:
        create_gitignore(project_path)
    except Exception as e:
        print(f"Error creating .gitignore: {e}")
        exit(1)

    # Setup git repository
    try:
        setup_git_repository(repo_name, repo_description)
    except subprocess.CalledProcessError as e:
        print(f"Error setting up git repository: {e}")
        exit(1)

    # Add and commit files
    try:
        print("Adding files according to .gitignore rules...")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during git add/commit: {e}")
        exit(1)

    # Setup remote and push
    remote_url = f"git@github.com:{github_username}/{repo_name}.git"
    try:
        subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)
        print(f"Pushing to remote repository: {remote_url}")
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
        print(f"Project successfully pushed to GitHub at {remote_url}")
    except subprocess.CalledProcessError as e:
        print(f"Error pushing to GitHub: {e}")
        print("This might be due to SSH key issues or network problems.")
        exit(1)


if __name__ == "__main__":
    main()