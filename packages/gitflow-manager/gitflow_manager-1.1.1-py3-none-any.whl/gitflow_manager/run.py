import importlib
import os
import pprint

from git import Repo

from gitflow_manager.changelog import ChangeLog
from gitflow_manager.errors import GitFlowManagerError
from gitflow_manager.git_hosts import BitBucket, GitLab
from gitflow_manager.gitflow_manager import GitFlowManager


def get_app_versions(current_folder):
    """

    :return: Dictionary of the apps with their name and version
    """
    versions = {}
    for file in os.listdir(os.path.dirname(current_folder)):
        if os.path.isdir(file) and os.path.isfile(os.path.join(file, "__init__.py")):
            mod = importlib.import_module(file)
            if hasattr(mod, "__app_name__"):
                versions[file] = {
                    "name": mod.__app_name__,
                    "version": mod.__version__,
                }
    return versions


def run(
    project_id: str,
    repo_id: str,
    folder: str,
    git_host_rest_url: str,
    git_host_token: str,
    main_branch_name: str = "main",
    monorepo: bool = False,
    git_host: str = "gitlab",
    check_docs: bool = False,
    app_specific_changes: bool = False,
    app_specific_text: str = None,
    layout: str = "src",
    dynamic_version: bool = False,
    use_ssh: bool = True
):
    git_manager = None
    try:
        # initialize Repo object, add all relevant files (py and version.txt) and print the git status
        repo = Repo(folder)
        assert repo.bare is False, "Folder is no existing Git repository!"
        git = repo.git
        if git_host.lower() == "bitbucket":
            git_host = BitBucket(
                git,
                git_host_rest_url,
                project_id,
                repo_id,
                token=git_host_token,
                ssh=use_ssh,
            )
        elif git_host.lower() == "gitlab":
            git_host = GitLab(
                git,
                git_host_rest_url,
                project_id,
                repo_id,
                token=git_host_token,
                ssh=use_ssh,
            )

        branch_of_interest = repo.active_branch.name
        print("******Pulling current branch to make sure we are up-to-date...******")
        git_host.git_pull()
        user_name = git.config("user.name")

        # Initializing the ChangeLog class
        chglog = ChangeLog(compare_url=f"{git_host.get_web_url()}/compare")
        if monorepo:
            app_versions = get_app_versions(folder)
            print(f"Apps:\n{pprint.pformat(app_versions)}\n\n")
            git_manager = GitFlowManager(
                git,
                git_host,
                branch_of_interest,
                main_branch_name=main_branch_name,
                app_versions=app_versions,
                check_docs=check_docs,
                project_layout=layout,
                dynamic_version=dynamic_version,
            )
        else:
            git_manager = GitFlowManager(
                git,
                git_host,
                branch_of_interest,
                main_branch_name=main_branch_name,
                check_docs=check_docs,
                project_layout=layout,
                dynamic_version=dynamic_version,
            )

        print(f"You are on branch '{branch_of_interest}'.\n")

        if branch_of_interest == main_branch_name:
            git_manager.branch_from_main(chglog, user_name, app_specific_changes, app_specific_text)
        elif branch_of_interest == "dev":
            git_manager.branch_from_dev(chglog, user_name, app_specific_changes, app_specific_text)
        elif branch_of_interest.startswith("hotfix/") or branch_of_interest.startswith("release/"):
            git_manager.merge_hotfix_or_release(
                chglog,
                user_name,
                app_specific_changes,
                app_specific_text,
            )
        elif branch_of_interest.startswith("feature/") or branch_of_interest.startswith("bugfix/"):
            git_manager.merge_feature_or_bugfix(chglog, user_name, app_specific_changes, app_specific_text)
        else:
            raise GitFlowManagerError(f"Unknown branch {branch_of_interest}")

    except Exception as e:
        if isinstance(e, GitFlowManagerError):
            raise e
        msg = f"Exception was raised:\n{e}\n\nThese steps had been performed successfully:\n"
        msg += "-" + "\n-".join(git_manager.steps_done if git_manager is not None else [])
        msg += "\n\nThese steps still need to be done (manually now):\n"
        msg += "-" + "\n-".join(git_manager.steps_to_do if git_manager is not None else ["**All!**"])
        raise Exception(msg)
