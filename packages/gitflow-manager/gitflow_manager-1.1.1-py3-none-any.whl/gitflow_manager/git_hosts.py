import json
import warnings
from abc import ABC, abstractmethod
from typing import Any

import requests
from git import GitCommandError


class GitHost(ABC):
    """
    Abstract base class to define the interface for interacting with Git hosting services.
    """

    def __init__(
        self,
        git_object: Any,
        git_host_rest_url: str,
        project_id: str,
        repo_id: str,
        token: str,
        ssh: bool = False,
    ):
        """
        Initialize the Git host object with required parameters.

        :param git_object: Git object from a Git library (e.g., GitPython)
        :param project_id: Project identifier in the Git hosting service
        :param repo_id: Repository identifier
        :param token: Authentication token
        :param ssh: Boolean indicating if SSH connection should be used
        """
        self.git_obj = git_object
        self.project_id = project_id
        self.git_host_rest_url = git_host_rest_url
        self.repo_id = repo_id
        self.token = token
        self.ssh = ssh
        self.http_success = {200, 201, 202, 203, 204, 205, 206, 207, 208, 226}

    def git_push(self, branch: str = "HEAD", tag: str | None = None) -> None:
        """Push changes to a Git remote repository."""
        self.git_remote(method="push", branch=branch, tag=tag)

    def git_pull(self) -> None:
        """Pull changes from a Git remote repository."""
        self.git_remote(method="pull")

    @abstractmethod
    def git_remote(self, method: str, branch: str = "HEAD", tag: str | None = None) -> None:
        """Push or pull changes to/from a Git remote repository."""
        pass

    @abstractmethod
    def create_merge_request(self, source_branch: str, target_branch: str, description: str) -> None:
        """Create a merge request between branches."""
        pass

    def git_remote_https(self, method: str, branch: str = "HEAD", tag: str | None = None) -> None:
        """
        Default HTTPS push or pull method for subclasses.

        :param method: Git operation, either "push" or "pull"
        :param branch: Branch to push or pull
        :param tag: Optional tag to push
        """
        assert method in {"push", "pull"}, "Method must be 'push' or 'pull'"
        branch = branch or self._get_current_branch()

        try:
            command = ["git", method, "origin", branch]
            if method == "push" and tag:
                command.extend(["refs/tags/" + tag])
            self.git_obj.execute(command)
        except Exception as e:
            raise RuntimeError(f"HTTPS {method} failed: {str(e)}")

    @abstractmethod
    def get_web_url(self) -> str:
        """
        Generate a web URL for the repository based on the Git service format.

        :return: Web URL of the repository
        """
        pass

    def _create_request(self, url: str, method: str = "GET", **kwargs) -> requests.Response:
        """
        Create and send an HTTP request with authorization headers.

        :param url: URL for the request
        :param method: HTTP method (e.g., GET, POST)
        :param kwargs: Additional parameters for the request
        :return: Response object
        """
        headers = {"Authorization": f"Bearer {self.token}"}
        headers.update(kwargs.pop("headers", {}))
        response = requests.request(method, url, headers=headers, **kwargs)

        if response.status_code not in self.http_success:
            response.raise_for_status()

        return response

    @abstractmethod
    def get_protected_branches(self) -> list[str]:
        """Retrieve a list of protected branches in the repository."""
        pass

    def _get_current_branch(self) -> str:
        """
        Retrieve the current branch checked out in the repository.

        :return: Name of the current branch
        """
        return self.git_obj.execute(["git", "rev-parse", "--abbrev-ref", "HEAD"])


class BitBucket(GitHost):
    """
    A class to communicate with Bitbucket for pushing and merge requests
    """

    def __init__(self, git_object, git_host_rest_url, project_id, repo_id, token, ssh=False):
        """

        :param git_object: git object from git python
        :param project_id: Gitlab project id of project
        :param ssh: Boolean if ssh connection to Gitlab is set
        """
        super().__init__(git_object, git_host_rest_url, project_id, repo_id, token, ssh)

    def git_remote_https(self, method, branch="HEAD", tag=None):
        """
        Push or pull changes to/from a Git remote repository using HTTPS

        :param method: Git operation method, either "push" or "pull"
        :param branch: Branch to push or pull
        :param tag:
        """
        assert method in ["push", "pull"]
        if branch == "HEAD":
            branch = self.git_obj.execute(["git", "rev-parse", "--abbrev-ref", "HEAD"])

        info = self._create_request(
            f"{self.git_host_rest_url}/api/1.0/projects/{self.project_id}/repos/{self.repo_id}"
        ).json()
        url = info["links"]["clone"][1]["href"]
        if url != self.git_obj.execute(["git", "remote", "get-url", "origin"]):
            ssh_url = True
            # set origin temporarily to https url
            url = url.replace("https://", f"https://oauth2:{self.token}@")
            self.git_obj.execute(["git", "remote", "set-url", "origin", url])
            # necessary as some configs have an extra push url (and we cannot check if it exists...)
            self.git_obj.execute(["git", "remote", "set-url", "--push", "origin", url])
        else:
            ssh_url = False
        try:
            if method == "push":
                self.git_obj.execute(["git", "push", "--set-upstream", "origin", branch])
                if tag is not None:
                    self.git_obj.execute(["git", "push", "origin", f"refs/tags/{tag}"])

            else:
                self.git_obj.execute(["git", "pull", "origin", branch])
        except GitCommandError as e:
            raise Exception(
                f"Trying to communicate via https failed due to:\n{str(e)}\n\n" f"Please pull/push manually!!!"
            )
        finally:
            self.git_obj.fetch("origin")
            self.git_obj.execute(["git", "branch", "--set-upstream-to", f"origin/{branch}"])
            if ssh_url:
                # make sure remote tracking is set back to the default
                self.git_obj.execute(
                    [
                        "git",
                        "remote",
                        "set-url",
                        "origin",
                        [link["href"] for link in info["links"]["clone"] if link["name"] == "ssh"][0],
                    ]
                )
                self.git_obj.execute(
                    [
                        "git",
                        "remote",
                        "set-url",
                        "--push",
                        "origin",
                        [link["href"] for link in info["links"]["clone"] if link["name"] == "ssh"][0],
                    ]
                )

    def git_remote(self, method, branch="HEAD", tag=None):
        """
        Push or pull changes to/from a Git remote repository

        :param method: Git operation method, either "push" or "pull"
        :param branch: Branch to push or pull
        :param tag:
        """
        assert method in ["push", "pull"]
        if branch == "HEAD":
            branch = self.git_obj.execute(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        self.git_obj.checkout(branch)
        if self.ssh:
            try:
                if method == "push":
                    self.git_obj.execute(["git", "push", "--set-upstream", "origin", branch])
                    if tag is not None:
                        self.git_obj.execute(["git", "push", "origin", f"refs/tags/{tag}"])
                else:
                    self.git_obj.execute(["git", "pull", "origin"])
            except GitCommandError as e:
                if "correct access rights" in str(e):
                    warnings.warn("It seems your ssh keys are not existent/accessible. Trying to communicate via https")
                    self.ssh = False
                    self.git_remote_https(method=method, branch=branch, tag=tag)
                else:
                    raise e
        else:
            self.git_remote_https(method=method, branch=branch, tag=tag)

    def get_protected_branches(self):
        """
        Get a list of protected branches in a Bitbucket repository.

        :return: A list of names for the protected branches in the repository.
        """
        try:
            response = self._create_request(
                f"{self.git_host_rest_url}/branch-permissions/2.0/projects/{self.project_id}/repos/{self.repo_id}/restrictions"
            ).json()

            if isinstance(response, requests.Response) and response.status_code == 401:
                print(
                    f"Your user is not authorized to retrieve protected branches. Message from Bitbucket:\n"
                    f"{response['errors'][0]['message']}\n"
                    f"Please check that you have repo-admin rights to this repo."
                )
                return []

            is_last_page = response["isLastPage"]

            protected = []
            for branch in response["values"]:
                if branch["type"] == "pull-request-only":
                    protected.append(branch["matcher"]["displayId"])
            while not is_last_page:
                response = self._create_request(
                    f'{self.git_host_rest_url}/branch-permissions/2.0/projects/{self.project_id}/repos/{self.repo_id}/restrictions?start={response["nextPageStart"]}'
                ).json()
                for branch in response["values"]:
                    if branch["type"] == "pull-request-only":
                        protected.append(branch["matcher"]["displayId"])
                is_last_page = response["isLastPage"]

            return protected

        except Exception as e:
            return f"Could not identify protected branches: {e}"

    def create_merge_request(self, source_branch, target_branch, description):
        """
        Create a merge request in a Bitbucket repository.

        :param source_branch: The branch to be merged into the target branch.
        :param target_branch: The branch into which the source branch will be merged.
        :param description: A description for the merge request.
        """
        # make sure source branch is up to date on origin
        self.git_push(source_branch)
        # create merge information
        merge_data = {
            "title": f"Merge {source_branch} into {target_branch}",
            "description": description,
            "fromRef": {
                "id": source_branch,
                "repository": {
                    "slug": self.repo_id,
                    "project": {"key": self.project_id},
                },
            },
            "toRef": {
                "id": target_branch,
                "repository": {
                    "slug": self.repo_id,
                    "project": {"key": self.project_id},
                },
            },
        }

        response = self._create_request(
            f"{self.git_host_rest_url}/api/1.0/projects/{self.project_id}/repos/{self.repo_id}/pull-requests",
            method="POST",
            data=json.dumps(merge_data),
            headers={"Content-type": "application/json"},
        )
        if response.status_code in self.http_success and response.json()["state"] == "OPEN":
            print(
                f"******Merge request for {source_branch} into {target_branch} successfully opened!*******\n"
                f"Visit it under\n{response.json()['links']['self'][0]['href']}\nfor merging or assigning someone."
            )

        elif response.status_code not in self.http_success:
            warnings.warn(
                f"Merge request failed, request errored with code {response.status_code} and error " f"{response.text}"
            )
        else:
            warnings.warn(f"Merge request failed: \n{response.json()}")

    def get_web_url(self) -> str:
        """
        Generate a web URL for the repository based on the Git service format.

        :return: Web URL of the repository
        """
        return f"https://{self.git_host_rest_url}/projects/{self.project_id}/repos/{self.repo_id}"


class GitLab(GitHost):
    """
    A class to communicate with GitLab for pushing and merge requests
    """

    def __init__(self, git_object, git_host_rest_url, project_id, repo_id, token, ssh=False):
        """

        :param git_object: git object from git python
        :param project_id: Gitlab project id of project
        :param ssh: Boolean if ssh connection to Gitlab is set
        """
        super().__init__(git_object, git_host_rest_url, project_id, repo_id, token, ssh)

    def git_remote_https(self, method, branch="HEAD", tag=None):
        """
        Push or pull changes to/from a Git remote repository using HTTPS

        :param method: Git operation method, either "push" or "pull"
        :param branch: Branch to push or pull
        :param tag:
        """
        if method not in ["push", "pull"]:
            raise AssertionError
        if branch == "HEAD":
            branch = self.git_obj.execute(["git", "rev-parse", "--abbrev-ref", "HEAD"])

        info = self._create_request(f"{self.git_host_rest_url}/projects/{self.project_id}").json()
        if "error" in info:
            raise AssertionError(f"Error when accessing Gitlab API: {info['error_description']}")
        url = info["http_url_to_repo"]
        origin_url = self.git_obj.execute(["git", "remote", "get-url", "origin"])
        url_replaced = False
        if "https://" not in origin_url:
            url_replaced = True
            # set origin temporarily to https url
            url = url.replace("https://", f"https://oauth2:{self.token}@")
            self.git_obj.execute(["git", "remote", "set-url", "origin", url])
            # necessary as some configs have an extra push url (and we cannot check if it exists...)
            self.git_obj.execute(["git", "remote", "set-url", "--push", "origin", url])
        else:
            user_name = self._create_request(f"{self.git_host_rest_url}/user").json()["username"]
            url = url.replace("https://", f"https://{user_name}:{self.token}@")
            if url != origin_url:
                url_replaced = True
                self.git_obj.execute(["git", "remote", "set-url", "origin", url])
                # necessary as some configs have an extra push url (and we cannot check if it exists...)
                self.git_obj.execute(["git", "remote", "set-url", "--push", "origin", url])

        try:
            if method == "push":
                self.git_obj.execute(["git", "push", "--set-upstream", "origin", branch])
                if tag is not None:
                    self.git_obj.execute(["git", "push", "origin", f"refs/tags/{tag}"])

            else:
                self.git_obj.execute(["git", "pull", "origin", branch])
        except GitCommandError as e:
            raise Exception(
                f"Trying to communicate via https failed due to:\n{str(e)}\n\n" f"Please pull/push manually!!!"
            )
        finally:
            self.git_obj.fetch("origin")
            self.git_obj.execute(["git", "branch", "--set-upstream-to", f"origin/{branch}"])
            if url_replaced:
                # make sure remote tracking is set back to the default
                self.git_obj.execute(["git", "remote", "set-url", "origin", origin_url])
                self.git_obj.execute(["git", "remote", "set-url", "--push", "origin", origin_url])

    def git_remote(self, method, branch="HEAD", tag=None):
        """
        Push or pull changes to/from a Git remote repository

        :param method: Git operation method, either "push" or "pull"
        :param branch: Branch to push or pull
        :param tag:
        """
        assert method in ["push", "pull"]
        if branch == "HEAD":
            branch = self.git_obj.execute(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        self.git_obj.checkout(branch)
        if self.ssh:
            try:
                if method == "push":
                    self.git_obj.execute(["git", "push", "--set-upstream", "origin", branch])
                    if tag is not None:
                        self.git_obj.execute(["git", "push", "origin", f"refs/tags/{tag}"])
                else:
                    self.git_obj.execute(["git", "pull", "origin"])
            except GitCommandError as e:
                if "correct access rights" in str(e):
                    warnings.warn("It seems your ssh keys are not existent/accessible. Trying to communicate via https")
                    self.ssh = False
                    self.git_remote_https(method=method, branch=branch, tag=tag)
                else:
                    raise e
        else:
            self.git_remote_https(method=method, branch=branch, tag=tag)

    def get_protected_branches(self):
        """
        Get a list of protected branches in a GitLab repository.

        :return: A list of names for the protected branches in the repository.
        """
        response = self._create_request(f"{self.git_host_rest_url}/projects/{self.project_id}/protected_branches").json()
        protected = []
        for br in response:
            if br["push_access_levels"][0]["access_level"] == 0:
                protected.append(br["name"])
        return protected

    def create_merge_request(self, source_branch, target_branch, description):
        """
        Create a merge request in a GitLab repository.

        :param source_branch: The branch to be merged into the target branch.
        :param target_branch: The branch into which the source branch will be merged.
        :param description: A description for the merge request.
        """
        # make sure source branch is up to date on origin
        self.git_push(source_branch)
        # create merge information
        merge_data = {
            "id": self.project_id,
            "source_branch": source_branch,
            "target_branch": target_branch,
            "title": f"Merge {source_branch} into {target_branch}",
            "description": description,
            "remove_source_branch": False,
        }

        response = self._create_request(
            f"{self.git_host_rest_url}/projects/{self.project_id}/merge_requests",
            method="POST",
            data=json.dumps(merge_data),
            headers={"Content-type": "application/json"},
        )
        if response.status_code in self.http_success and response.json()["state"] in ["OPEN", "opened"]:
            print(
                f"******Merge request for {source_branch} into {target_branch} successfully opened!*******\n"
                f"Visit it under\n{response.json()['web_url']}\nfor merging or assigning someone."
            )

        elif response.status_code not in self.http_success:
            warnings.warn(
                f"Merge request failed, request errored with code {response.status_code} and error " f"{response.text}"
            )
        else:
            warnings.warn(f"Merge request failed: \n{response.json()}")

    def get_web_url(self) -> str:
        """
        Generate a web URL for the repository based on the Git service format.

        :return: Web URL of the repository
        """
        response = self._create_request(
            f"{self.git_host_rest_url}/projects/{self.project_id}",
            method="GET",
            headers={"Content-type": "application/json"},
        ).json()
        return response["web_url"]
