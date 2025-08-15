import argparse
from pathlib import Path
from urllib.parse import urlparse
import requests
import yaml

from gitflow_manager.run import run


def get_project_details(repo_url, git_host_token):
    """Get the details of the repository: url, project id, repository name"""
    parsed_url = urlparse(repo_url)
    host = parsed_url.netloc
    path = parsed_url.path.strip("/").rstrip(".git")

    namespace, repo_name = path.split("/", 1)
    gitlab_api_url = f"https://{host}/api/v4"
    project_api_url = f"{gitlab_api_url}/projects/{path.replace('/', '%2F')}"

    headers = {"PRIVATE-TOKEN": git_host_token}
    response = requests.get(project_api_url, headers=headers)

    if response.status_code == 200:
        project_data = response.json()
        return gitlab_api_url, project_data["id"], repo_name
    else:
        raise Exception(f"GitLab request failed: {response.status_code} - {response.text}")


def save_config(file_path: Path, data):
    """Save configuration to .gitflow_manager.yml"""
    with file_path.open("w") as f:
        yaml.dump(data, f, default_flow_style=False)
    print(f"Configuration saved to {file_path}")


def load_config(file_path: Path):
    """Load configuration from .gitflow_manager.yml"""
    if file_path.is_file():
        with file_path.open("r") as f:
            return yaml.safe_load(f)
    return None


def init(config_file: Path):
    """Function to initialize GitFlowManager"""

    # Check if config exists
    if not config_file.is_file() or input("Configuration already existing in .gitflow_manager.yml. "
                        "Use existing configuration (y/n)?\n").lower() == "n":
        # create new config file and use new information
        repo_url = input("Please enter the URL of your repository:\n")
        git_host_token = input("Please enter a project or personal token, with which you can access that repository "
                         "(read/write):\n")
        git_host_rest_url, project_id, repo_name = get_project_details(repo_url, git_host_token=git_host_token)
        project_layout = input("Please enter the layout of your project (e.g., 'flat' or 'src'):\n")
        dynamic_version = input("Is the versioning of your project dynamic (y/n)?\n")
        dynamic_version = dynamic_version.lower() == "y"
        check_docs = input("Check for changes in the docs before merging (y/n)?\n")
        check_docs = check_docs.lower() == "y"
        use_ssh = input("Would you like to use ssh connection (y/n)?\n")
        use_ssh = use_ssh.lower() == "y"

        # Save config
        save_config(config_file, {
            "git_host_rest_url": git_host_rest_url,
            "git_host_token": git_host_token,
            "project_id": project_id,
            "repo_name": repo_name,
            "project_layout": project_layout,
            "dynamic_version": dynamic_version,
            "check_docs": check_docs,
            "use_ssh": use_ssh
        })

        ignore_file = Path(".gitignore")

        # Datei erstellen, falls sie nicht existiert
        if not ignore_file.is_file():
            ignore_file.write_text(f"{config_file.name}\n")
        else:
            content = ignore_file.read_text().splitlines()
            if config_file.name not in content:
                with ignore_file.open("a") as f:
                    f.write(f"\n{config_file.name}\n")


def main():
    parser = argparse.ArgumentParser(
        description="""GitFlowManager: manages the creation of new branches and merges of existing ones."""
    )
    parser.add_argument(
        "--init",
        default=False,
        action="store_true",
        help="Used to start the gitflow_manager.",
    )
    config_file = Path.cwd().joinpath(".gitflow_manager.yml")
    args = parser.parse_args()
    if args.init:
        init(config_file)

    if config_file.is_file():
        config = load_config(config_file)
        # use config file based on user choice during init
        run(config["project_id"],
            config["repo_name"],
            folder=str(Path.cwd()),  # Get the current project directory,
            git_host_rest_url=config["git_host_rest_url"],
            git_host_token=config["git_host_token"],
            layout=config["project_layout"],
            dynamic_version=config["dynamic_version"],
            check_docs=config["check_docs"],
            use_ssh=config["use_ssh"]
            )
    else:
        raise FileNotFoundError("Git manager config file '.gitflow_manager.yml' not found in the current directory. "
                                "Either you are in the wrong directory, or you have not run 'gfm --init', yet.")


if __name__ == "__main__":
    main()
