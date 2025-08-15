import os
import pathlib
import re
import sys
import warnings

from git.exc import GitCommandError

from gitflow_manager.changelog import Sections
from gitflow_manager.errors import GitFlowManagerError
from gitflow_manager.file_utils import read_file, read_toml, write_to_file, write_to_toml


class GitFlowManager:
    def __init__(
        self,
        git,
        git_host,
        branch_of_interest,
        main_branch_name: str = "main",
        app_versions: dict = None,
        check_docs: bool = False,
        dynamic_version: bool = True,
        project_layout: str = "src",
    ):
        """_summary_

        :param git: _description_
        :type git: _type_
        :param git_host: _description_
        :type git_host: _type_
        :param branch_of_interest: _description_
        :type branch_of_interest: _type_
        :param app_versions: _description_, defaults to None
        :type app_versions: dict, optional
        :param check_docs: _description_, defaults to False
        :type check_docs: bool, optional
        :param dynamic_version: If the param is set in the pyproject.toml, defaults to True
        :type dynamic_version: bool, optional
        """
        self.git = git
        self.git_host = git_host
        self.branch_of_interest = branch_of_interest
        self.main_branch_name = main_branch_name
        self.app_versions = app_versions  # in case of a monorepo
        self.check_docs = check_docs
        self.dynamic_version = dynamic_version
        self.layout = project_layout
        self.package_name, self.package_version = self.get_package_info(layout=project_layout,
                                                                        dynamic_version=dynamic_version)
        self.steps_to_do = []
        self.steps_done = []
        self.files_to_commit = []

    @staticmethod
    def get_package_info(path_to_toml: str = "pyproject.toml", layout: str = "flat", dynamic_version: bool = False):
        """

        :return: Dictionary of the apps with their name and version
        """
        pyproject_data = read_toml(path_to_toml)
        package_name = pyproject_data["project"]["name"]
        if dynamic_version:
            if layout == "flat":
                path_to_init = pathlib.Path(f"{package_name}/__init__.py")
            elif layout == "src":
                path_to_init = pathlib.Path(f"src/{package_name}/__init__.py")
            else:
                path_to_init = pathlib.Path(layout)

            init_file = read_file(path_to_init)
            version_pattern = r"^__version__\s*=\s*['\"](\d+\.\d+\.\d)['\"]"
            # Search for the version pattern
            match = re.search(version_pattern, init_file, re.MULTILINE)
            if match:
                package_version = match.group(1)
            else:
                raise FileNotFoundError(f"Found no version in init file {path_to_init}. If your project has no dynamic"
                                        f"version, please set 'dynamic_version' to false in '.gitflow_manager.yml'.")
        else:
            package_version = pyproject_data["project"]["version"]
        return package_name, package_version

    def branch_from_main(self, chglog, user_name, app_specific_changes, app_specific_text):
        """
        Create a new branch from the main branch, update version and changelog, and push new branch to origin

        :param chglog:
        :param user_name:
        :param app_specific_changes:
        :param app_specific_text:
        """
        # from main branch only one version type is possible. Ask for continuing
        answer = input(
            f"You are on branch {self.main_branch_name}. Possible options:\n"
            "- New Hotfix (v*.*.X)\n"
            "Continue (y/n)?\n"
        )
        if answer != "y":
            print("Aborted...")
            sys.exit()

        branch_type = "hotfix"

        # update version number accordingly
        package_version_parsed = [int(x) for x in self.package_version.split(".")]
        new_package_version = self.increase_version(package_version_parsed, "hotfix")
        branch_name = f"hotfix/v{new_package_version}"
        self.steps_to_do.extend([f'Checkout to "{branch_name}"'])
        # create the new hotfix branch and checkout
        self.git.checkout("HEAD", b=branch_name)  # create a new branch
        self.steps_done.append(self.steps_to_do.pop(0))

        self.add_log_changes(
            new_package_version,
            branch_type,
            [Sections.fixed],
            chglog,
            user_name,
            app_specific_changes,
            app_specific_text,
        )

        # change the App Package version
        self.change_package_version(new_package_version)

        if self.app_versions:
            # in the hotfix case we do not know which app will be changed so we have to ask
            self.add_modified_apps_main()
        # commit and push changes
        self.commit_and_push(branch_name=branch_name, branch_type="New hotfix")

    def branch_from_dev(self, chglog, user_name, app_specific_changes, app_specific_text):
        """
        Create a new branch from dev, update changelog, and push new branch to origin

        :param chglog:
        :param user_name:
        :param app_specific_changes:
        :param app_specific_text:
        :return:
        """
        # ask for new version type
        answer = input(
            "You are on branch dev. Possible options:\n"
            "- New major (vX.0.0) release (1)\n"
            "- New minor (v*.X.0) release (2)\n"
            "- New feature branch (3)\n"
            "- New bugfix branch (4)\n\n"
            "Please choose one option by typing the number!\n"
        )
        assert re.match("^[1-4]$", answer) is not None, "Please give a number from 1 to 4!"

        answer = int(answer)
        version_mapping = {1: "major", 2: "minor", 3: "feature", 4: "bugfix"}
        type_version = version_mapping[answer]

        if type_version in ("major", "minor"):
            # update version number accordingly
            package_version_parsed = [int(x) for x in self.package_version.split(".")]
            new_package_version = self.increase_version(package_version_parsed, type_version)
            # create the new release branch
            new_branch = f"v{new_package_version}"
            branch_type = "release"
            ask_list = [Sections.added, Sections.changed, Sections.fixed]
        else:
            new_package_version = None
            if type_version == "feature":
                branch_type = "feature"
                ask_list = [Sections.added, Sections.changed]
            else:
                branch_type = "bugfix"
                ask_list = [Sections.fixed]
            while True:
                new_branch = input(f"What should be the name of the {branch_type} branch?\n")
                if re.match("^[a-zA-Z_]+$", new_branch) is not None:
                    break
                else:
                    print("Only letters and underscore is allowed!")

        branch_name = f"{branch_type}/{new_branch}"
        self.steps_to_do.extend([f'Checkout to "{branch_name}"'])
        # create the new release branch and checkout
        self.git.checkout("HEAD", b=branch_name)  # create a new branch
        self.steps_done.append(self.steps_to_do.pop(0))

        self.add_log_changes(
            new_package_version,
            branch_type,
            ask_list,
            chglog,
            user_name,
            app_specific_changes,
            app_specific_text,
        )

        if new_package_version is not None:
            # change the App Package version
            self.change_package_version(new_package_version)
            # in the dev case we know that all changes for this release had been merged into dev, so we can check
            # which apps had been changed since the last merge to the main branch (changes
            if self.app_versions:
                self.add_modified_apps_dev(type_version)
            self.steps_done.append(self.steps_to_do.pop(0))

        commit_type = {
            "major": "Major changes",
            "minor": "Intermediate changes",
            "feature": "New feature",
            "bugfix": "New bugfix",
        }[type_version]
        # commit and push changes
        self.files_to_commit.append("docs/source/change_log*")
        self.commit_and_push(branch_name=branch_name, branch_type=commit_type)

    def merge_hotfix_or_release(self, chglog, user_name, app_specific_changes, app_specific_text):
        """
        Merge a hotfix or release branch into dev and/or the main branch

        :param chglog:
        :param user_name:
        :param app_specific_changes:
        :param app_specific_text:
        """
        answer = input(
            f"Edit change log information? (0)\n"
            f"Merge branch {self.branch_of_interest} into:\n"
            f"- Dev? (1)\n"
            f"- Dev & {self.main_branch_name}? (2)\n"
            f"Please choose one option by typing the number.\n"
        )
        if re.match("^[0-2]$", answer) is None:
            print(f"Answer was {answer}, aborting...")
            sys.exit()

        if answer == "0":
            self.edit_change_log_info(
                chglog, user_name, app_specific_changes, app_specific_text
            )
        else:
            # fill steps to do list
            self.steps_to_do.append("Do a sanity push of your branch to origin beforehand")
            self.steps_to_do.append(
                f"Merge branch into dev & {self.main_branch_name} (directly+pushing or via merge request)"
            )
            branches_to_merge = ["dev"]

            if answer == "2":
                branches_to_merge.append(self.main_branch_name)
                # only do the commit check if there will be merge into the main branch
                self.commit_check(branches_to_merge[-1])
                last_main_commit = self.git.execute(["git", "rev-parse", f"origin/{branches_to_merge[-1]}"])
                self.check_doc_changes(branches_to_merge[-1], last_main_commit)
            else:
                last_main_commit = self.git.execute(["git", "rev-parse", f"origin/{branches_to_merge[-1]}"])

            # sanity push that remote is up to date
            self.git_host.git_push(self.branch_of_interest)
            self.steps_done.append(self.steps_to_do.pop(0))
            # replace this message with the real ones
            self.steps_to_do.pop(0)

            protected_branches = self.git_host.get_protected_branches()
            descr = None
            for main_branch in branches_to_merge:
                if main_branch in protected_branches:
                    self.request_merge(main_branch, last_main_commit, descr)

                else:
                    self.merge_branch(main_branch)
                    if main_branch == self.main_branch_name:
                        # remove this as soon as the gitlab yml supports tagging the main branch online
                        self.git.execute(["git", "tag", f"v{self.package_version}"])
                    self.git_host.git_push(main_branch)
                    self.steps_done.append(self.steps_to_do.pop(0))

    def merge_feature_or_bugfix(self, chglog, user_name, app_specific_changes, app_specific_text):
        """
        Merge a feature or bugfix branch into dev.

        :param chglog:
        :param user_name:
        :param app_specific_changes:
        :param app_specific_text:
        """
        answer = input(
            f"Edit change log information? (0)\n"
            f"Merge branch {self.branch_of_interest} into dev? (1)\n"
            f"Please choose one option by typing the number.\n"
        )
        if re.match("^[0-1]$", answer) is None:
            print(f"Answer was {answer}, aborting...")
            sys.exit()

        if answer == "0":
            self.edit_change_log_info(
                chglog, user_name, app_specific_changes, app_specific_text
            )
        else:
            print("******Checking latest commit of dev...******")
            main_branch = "dev"
            self.commit_check(main_branch)

            last_main_commit = self.git.execute(["git", "rev-parse", f"origin/{main_branch}"])
            self.check_doc_changes(main_branch, last_main_commit)

            protected_branches = self.git_host.get_protected_branches()
            descr = None
            if main_branch in protected_branches:
                self.request_merge(main_branch, last_main_commit, descr)

            else:
                self.merge_branch(main_branch)
                self.git_host.git_push(main_branch)
                self.git_host.git_push(self.branch_of_interest)
                self.steps_done.append(self.steps_to_do.pop(0))

    @staticmethod
    def increase_version(version_parsed, version_type: str):
        """

        :param version_parsed: current version of the package
        :param version_type: major or minor release or feature
        :return: new version of the package
        """
        assert version_type in ["minor", "major", "hotfix"]
        match version_type:
            case "hotfix":
                version_parsed[2] += 1
            case "minor":
                version_parsed[1] += 1
                version_parsed[2] = 0
            case "major":
                version_parsed[0] += 1
                version_parsed[1] = 0
                version_parsed[2] = 0
        return ".".join([str(x) for x in version_parsed])

    def change_package_version(self, new_version: str):
        """
        Add the new version number to the package

        :param path_to_init: Path to the file that has to be updated
        :param old_version: Old version number
        :param new_version: New version number
        """
        if self.layout == "flat":
            path_to_init = pathlib.Path(f"{self.package_name}/__init__.py")
        elif self.layout == "src":
            path_to_init = pathlib.Path(f"src/{self.package_name}/__init__.py")
        else:
            path_to_init = pathlib.Path(self.layout)

        assert path_to_init.exists(), f"Path to init file under {path_to_init} with layout {self.layout} not found."

        self.change_version_init(path_to_init, self.package_version, new_version)
        self.files_to_commit.append(path_to_init)

        # manually update the version number in the pyproject.toml if not set to dynamic
        if not self.dynamic_version:
            path_to_pyproject = "pyproject.toml"
            self.change_version_pyproject(path_to_pyproject, new_version=new_version)
            self.files_to_commit.append(path_to_pyproject)

    def change_app_version(self, path_to_init, old_version: str, new_version: str):
        """
        Add the new version number to the package

        :param path_to_init: Path to the file that has to be updated
        :param old_version: Old version number
        :param new_version: New version number
        """
        self.change_version_init(path_to_init, old_version, new_version)
        self.files_to_commit.append(path_to_init)

    @staticmethod
    def change_version_init(path_to_init: str, old_version: str, new_version: str):
        init_text = read_file(path_to_init)
        init_text_new = init_text.replace(old_version, new_version)
        if init_text == init_text_new:
            warnings.warn(f"Failed to replace old version string with new one in {path_to_init}. Probably it does not"
                          f"contain a version string.")
        else:
            write_to_file(path_to_init, init_text_new)

    @staticmethod
    def change_version_pyproject(path_to_toml: str, new_version: str):
        pyproject_data = read_toml(path_to_toml)
        pyproject_data["project"]["version"] = new_version
        write_to_toml(path_to_toml, pyproject_data)

    def add_modified_apps_dev(self, version_type: int):
        """
        Update App version for changed apps

        :param version_type: major (0) or minor (1) release, feature (2) or bugfix (3)
        """
        # check if an app folder has been modified since branching off from the main branch
        last_common_commit = self.git.execute(["git", "merge-base", "HEAD", f"origin/{self.main_branch_name}"])
        file_diff = self.git.execute(["git", "diff", "HEAD", last_common_commit, "--name-only"]).split("\n")

        mod_app_folders = []
        if self.app_versions:
            for folder in self.app_versions.keys():
                if any([folder + "/" in file_str for file_str in file_diff]):
                    mod_app_folders.append(folder)
                    app_version_parsed = [int(x) for x in self.app_versions[folder]["version"].split(".")]
                    new_app_version = self.increase_version(app_version_parsed, version_type)
                    # change the App version
                    self.change_app_version(
                        os.path.join(folder, "__init__.py"),
                        old_version=self.app_versions[folder]["version"],
                        new_version=new_app_version,
                    )

        if mod_app_folders:
            print(
                f"App folders {mod_app_folders} had modified content since branching off from the main branch."
                f"Their app version have been increased accordingly"
            )

    def add_modified_apps_main(self):
        """
        Update App version for changed apps
        """
        answer = (
            input(
                "Which apps will be changed? Type the numbers (e.g. 13 for app 1 and 3), "
                "* for all apps or nothing for no app.\n"
                + "\n".join("%d : %s" % (i, s) for i, s in enumerate(self.app_versions.keys(), 1))
            )
            + "\n"
        )
        mod_app_folders = []
        if "*" in answer:
            mod_app_folders = self.app_versions.keys()
        elif len(answer) > 0:
            for i, app_folder in enumerate(self.app_versions.keys(), 1):
                if str(i) in answer:
                    mod_app_folders.append(app_folder)

        # update App version for changed apps
        for app_folder in mod_app_folders:
            app_version_parsed = [int(x) for x in self.app_versions[app_folder]["version"].split(".")]
            new_app_version = self.increase_version(app_version_parsed, 2)
            # change the App version
            self.change_app_version(
                os.path.join(app_folder, "__init__.py"),
                old_version=self.app_versions[app_folder]["version"],
                new_version=new_app_version,
            )

        self.steps_done.append(self.steps_to_do.pop(0))

    def add_log_changes(
        self,
        new_package_version,
        branch_type: str,
        ask_list,
        chglog,
        user_name,
        app_specific_changes,
        app_specific_text,
    ):
        """
        Add changes to changelog and update steps-to-do list

        :param branch_name: Full name of the new branch
        :param new_package_version: New version of the package for the changelog
        :param branch_type: release, hotfix, feature or bugfix
        :param ask_list: Change log sections that have to be updated
        :param chglog:
        :param user_name:
        :param app_specific_changes:
        :param app_specific_text:
        """
        # fill steps to do list
        self.steps_to_do.extend(
            [
                "Log changes to change_log.json and create new change_log.rst",
                "Write new version numbers to each __init__.py (package, and apps if they change)",
                "Add __init__.py and change_log* to git stage",
                "Commit git changes",
                "Push new branch to origin",
            ]
        )
        if new_package_version is None and branch_type != "hotfix":
            self.steps_to_do.remove("Write new version numbers to each __init__.py (package, and apps if they change)")

        # ask for the changes that will be done and add them to the change log
        if branch_type == "release":
            print(
                "******Please log, if there'll be any changes to be done on this release branch not already done"
                " in dev! This will be used for the change log!******"
            )
        else:
            print(
                f"******Please log the changes you will be doing on this {branch_type} branch! "
                "This will be used for the change log!******",
            )

        section_list = chglog.ask_for_changes(user_name, ask_list, app_specific_changes, app_specific_text)
        chglog.create_new_version(new_package_version, section_list)
        chglog.write_log()
        self.files_to_commit.append("docs/source/change_log*")
        self.steps_done.append(self.steps_to_do.pop(0))

    def commit_and_push(self, branch_name, message=None, branch_type=None):
        """
        Commit and push to origin. Can be a new branch

        :param branch_name: Name of the new branch
        :param branch_type: release, hotfix, feature or bugfix
        :param message: the message to use as commit message. Is an "Initial commit" message by default
        """
        if message is None:
            message = f"{branch_type}. Initial branch commit"

        self.git.add(self.files_to_commit)
        self.steps_done.append(self.steps_to_do.pop(0))
        print(self.git.status())

        try:
            self.git.commit(f'-m {message}')
        except GitCommandError:
            print("******Try committing changes again after pre-commit.******")
            self.git.add(self.files_to_commit)
            self.git.commit(f'-m {message}')

        self.steps_done.append(self.steps_to_do.pop(0))
        print(f"******Pushing now...******")
        self.git_host.git_push(branch_name)
        self.files_to_commit = []
        self.steps_done.append(self.steps_to_do.pop(0))

    def edit_change_log_info(
        self, chglog, user_name, app_specific_changes, app_specific_text
    ):
        """
        Edit change log information or regenerate change log.
        :param chglog:
        :param user_name:
        :param app_specific_changes:
        :param app_specific_text:
        :return:
        """
        answer = input(
            "Edit change log information? (0)\n"
            "Regenerate change log? (1)\n"
            "Please choose one option by typing the number.\n"
        )

        if re.match("^[01]$", answer) is None:
            print(f"Answer was {answer}, aborting...")
            sys.exit()

        if answer == "0":
            self.add_change_log_info(
                chglog, user_name, app_specific_changes, app_specific_text
            )
        else:
            self.steps_to_do.append("Create new change_log.rst")
            print("******Regenerating change log...******")
            chglog.write_log()
            self.steps_done.append(self.steps_to_do.pop(0))

    def add_change_log_info(self, chglog, user_name, app_specific_changes, app_specific_text):
        """
        Update change log and commit and push changes.

        :param chglog:
        :param user_name:
        :param app_specific_changes:
        :param app_specific_text:
        :return:
        """
        # fill steps to do list
        self.steps_to_do.append(
            "Log changes to change_log.json and create new change_log.rst"
        )
        if "bugfix/" in self.branch_of_interest or "hotfix/" in self.branch_of_interest:
            ask_sections = [Sections.fixed]
        else:
            ask_sections = [Sections.added, Sections.changed, Sections.fixed]
        section_list = chglog.ask_for_changes(user_name, ask_sections, app_specific_changes, app_specific_text)

        if "bugfix/" in self.branch_of_interest or "feature/" in self.branch_of_interest:
            chglog.add_to_version(None, section_list)
        else:
            chglog.add_to_version(self.package_version, section_list)

        chglog.write_log()
        self.steps_done.append(self.steps_to_do.pop(0))
        answer = input("Commit and Push changes? (y/n)\n")
        if answer.lower() == "n":
            print("Changes will not be committed and pushed...")
            return

        self.steps_to_do.extend(
            [
                "Add change_log* to git stage",
                "Commit git changes",
                "Push new branch to origin",
            ]
        )
        self.files_to_commit.append("docs/source/change_log*")
        print(self.git.status())
        print("******Committing and pushing change log changes...******")
        self.commit_and_push(branch_name=self.branch_of_interest, message="Added more change log information")

    def commit_check(self, branch_to_merge):
        """
        Check that latest commit of the main branch is in the branch of interest

        :param branch_to_merge: Branch to merge into, dev or the main branch
        """
        self.steps_to_do.insert(
            0,
            f"Check if latest commit on {branch_to_merge} is in your branch {self.branch_of_interest}",
        )
        # find last common ancestor between current and main branch/dev
        common_commit = self.git.execute(["git", "merge-base", "HEAD", f"origin/{branch_to_merge}"])
        # find most recent commit of current branch
        last_commit = self.git.execute(["git", "rev-parse", self.branch_of_interest])
        # find most recent commit of main branch/dev
        last_main_commit = self.git.execute(["git", "rev-parse", f"origin/{branch_to_merge}"])
        if last_commit == last_main_commit:
            raise GitFlowManagerError(f"{branch_to_merge} is already up to date with your branch {self.branch_of_interest}")
        self.steps_done.append(self.steps_to_do.pop(0))
        if (
            common_commit != last_main_commit
            and self.git.execute(["git", "diff", last_main_commit, common_commit]) != ""
        ):
            raise GitFlowManagerError(
                f"Your branch {self.branch_of_interest} does not include the latest commit from {branch_to_merge}! "
                f"Please merge {branch_to_merge} into your current branch and "
                f"{'manually correct the version numbers accordingly' if branch_to_merge == self.main_branch_name else 'rerun the script'}!"
            )

    def check_doc_changes(self, branch_to_merge, last_main_commit):
        """
        Check for changes in the docs before merging into main branch/dev

        :param branch_to_merge: branch to merge into, main branch or dev
        :param last_main_commit: Last commit of the main branch or dev branch
        """
        # check for changes in the docs before merging into main branch/dev
        response = self.git.execute(["git", "diff", last_main_commit, "HEAD", "docs/source/change_log.rst"])
        text_changes = "\n".join(
            [line[1:] for line in response.split("\n") if len(line) > 1 and line[0] == "+" and line[0:3] != "+++"]
        )
        if (self.check_docs is True and branch_to_merge == self.main_branch_name) or branch_to_merge == "dev":
            changed_docs = self.git.execute(
                [
                    "git",
                    "diff",
                    "--name-only",
                    last_main_commit,
                    "HEAD",
                    "docs/source/*",
                ]
            )
            if len(changed_docs) == 0:
                answer = input(
                    f"WARNING: You are about to merge below listed changes into the main branch but no "
                    f"changes could be found made to the docs! Please make sure that none of your "
                    f"changes are outdating the docs, or update them accordingly!\nIf you are sure to "
                    f"continue anyways, type 'y' and hit Enter. Otherwise we'll stop here for now...\n\n"
                    f"The following changes were made since last merge:\n{text_changes}"
                )
                if re.match("^y$", answer) is None:
                    print(f"Answer was {answer}, aborting...")
                    sys.exit()

    def request_merge(self, branch_to_merge, last_main_commit, descr):
        """
        For protected branches, create a merge request

        :param branch_to_merge: Branch to merge into, main branch or dev
        :param last_main_commit: Last commit of the branch to merge into
        :param descr: Description for the merge request
        """
        # fill steps to do list
        self.steps_to_do.append(f"Create merge request for branch {self.branch_of_interest} into {branch_to_merge}")
        print(f"****** {branch_to_merge} is a protected branch! Creating merge request... ******")
        if descr is None:
            descr = input(
                f"Enter some description for the merge to {branch_to_merge} "
                f"(adding all git commit messages if nothing entered)\n"
            )
            if len(descr) <= 1:
                commit_history = self.git.execute(
                    [
                        "git",
                        "log",
                        '--pretty=format:"%h%x09%an:%x09%s"',
                        f"{last_main_commit}..HEAD",
                    ]
                )
                commit_history = "* " + "* ".join(commit_history.splitlines(True))
                descr = (
                    f"Merge of {self.branch_of_interest} into {branch_to_merge}.\n\n"
                    f"Git history:\n\n{commit_history}"
                )

        self.git_host.create_merge_request(
            source_branch=self.branch_of_interest,
            target_branch=branch_to_merge,
            description=descr,
        )
        self.steps_done.append(self.steps_to_do.pop(0))

    def merge_branch(self, branch_to_merge):
        """
        Merge current branch into main branch/dev and update steps-to-do list

        :param branch_to_merge: Branch to merge into, main branch or dev
        """
        self.steps_to_do.append(f"Merge branch {self.branch_of_interest} into {branch_to_merge}")
        self.steps_to_do.append(f"Push {branch_to_merge} to origin")

        print(f"******Merging {self.branch_of_interest} into {branch_to_merge}, tagging and pushing...******")
        # merge into main branch / dev
        self.git.checkout(branch_to_merge)
        self.git.merge(["--no-ff", self.branch_of_interest])
        self.steps_done.append(self.steps_to_do.pop(0))
