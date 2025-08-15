# Anacision Gitflow Manager

## Description

The gitflow manager is a tool that helps maintaining clean versioning and documentation in code projects.
By using the gitflow manager one can make sure to stick to the 
[GitFlow](https://nvie.com/posts/a-successful-git-branching-model) rules. Furthermore, it helps maintain a good
changelog and documentation.
Whenever you want to start a new branch or merging it back to dev/main run the `gfm` command.
It uses a dialog to define the type of new branch (feature, bugfix, hotfix, release) or merge option as well as setting 
the required changelog messages.
It then automatically updates version numbers, checks out corresponding branches and commits/merges according to the 
GitFlow.
Changes are also pushed to the Git Host via ssh or https and for protected branches merge requests are initialized.
Currently, the gitflow manager supports Gitlab and Bitbucket as hosting platforms.

### Versioning

- Utilize the gitflow manager in projects to make sure that you easily stick to these rules:
  - Versions are defined in the format *Major.Minor.Hotfix*. New versions are created when opening the hotfix or release 
  branch.
  - The hotfix branch is only allowed to be started from main branch, to increase the Hotfix version digit only and to 
  be merged into main (+ dev thereafter).
  - The release branch is only allowed to be started from dev, to increase the minor or major version digit and to be 
  merged into main (+ dev thereafter). In case of a new major version, the minor and hotfix digit is reset to 0. In case
  of a new minor version, the hotfix digit is reset to 0.
  - The bugfix and feature branches are only allowed to be started from dev, increase no version number and are merged 
  back to dev.
  - All new branches need a description in the change log, which has separate "Added", "Changed" and "Fixed" sections.

### Supported branches with gitflow manager

- **main**: Permanent, stable, (normally) protected branch used for deployment. Each commit has a new version. Merge 
requests only come from release or hotfix branch.
- **dev**: Permanent development branch. Gets merge requests from feature, hotfix and release branch.
- **release/vX.X.X**: Release branch. Branched off from dev branch with new minor or major version. When the branch is
finished, it is merged into main and dev branch. Intermediate merges into dev are allowed, too. Merges from dev into 
release branch are not allowed.
- **feature/xxxxxx**: For features to be developed. Branched off from dev branch and will be merged back into dev after 
finishing feature.
- **bugfix/xxxxxx**: For bugs to be fixed. Branched off from dev branch and will be merged back into dev after 
finishing the fix.
- **hotfix/vX.X.X**: Hotfix branch for fixes from deployed code. Branched off from main branch with new hotfix 
version. When done, is merged into main and dev branch.

### Tagging

- Currently, tagging is not done automatically. You can configure yourself a CI pipeline, that does the job for you.

## Getting started

### Installation

1. Install gitflow manager with pip: `pip install gitflow-manager`
2. Restart terminal

### Usage

- When using the first time, run `gfm --init` in the root of the project.
- Subsequently, just type `gfm` each time you need to branch or merge (or add change log information), and follow the 
dialog
