# Making a new release of opensarlab_frontend

The extension can be published to `PyPI` and `npm` manually or by using GitHub actions to release on `PyPI` described in [Automated releases with GitHub Actions](#automated-releases-with-github-actions).

## Manual release

### Python package

This extension can be distributed as Python packages. All of the Python
packaging instructions are in the `pyproject.toml` file to wrap your extension in a
Python package. Before generating a package, you first need to install some tools:

```bash
pip install build twine hatch
```

Bump the version using `hatch`. By default this will create a tag.
See the docs on [hatch-nodejs-version](https://github.com/agoose77/hatch-nodejs-version#semver) for details.

```bash
hatch version <new-version>
```

Make sure to clean up all the development files before building the package:

```bash
jlpm clean:all
```

You could also clean up the local git repository:

```bash
git clean -dfX
```

To create a Python source package (`.tar.gz`) and the binary package (`.whl`) in the `dist/` directory, do:

```bash
python -m build
```

> `python setup.py sdist bdist_wheel` is deprecated and will not work for this package.

Then to upload the package to PyPI, do:

```bash
twine upload dist/*
```

### NPM package

To publish the frontend part of the extension as a NPM package, do:

```bash
npm login
npm publish --access public
```

## Automated releases with GitHub Actions

### ⚙️ Setting up your project to deploy using PyPI Trusted Publisher ⚙️

#### Set up PyPI

- Create PyPI project
- In Manage mode on PyPI project, click `Publishing` and add new GitHub Trusted Publisher
  - Set Workflow name to `publish-release.yml`
  - Set Environment name to the environment your action will be using (Usually prod or test)
- Create access token for your User
  - In Account Settings, click on `Add API token`
  - Set its scope to your project only
  - Save your PyPI token for when setting up your GitHub environment

#### Create GitHub Personal Access Token (PAT)

- The following should be completed on a GitHub account all collaborators in the repo have access to (eg: machine user)
- Go to GitHub account `settings`
- Scroll down to `Developer Settings`
- Click `Personal Access Token`
  - Select `Fine-grained tokens`
- `Generate new token` in the upper right
- Give the token a name and description
- Set `Resource Owner` to the GitHub organization or user who owns the repository
- Set `Repository Access` to Only select repositories
  - Select your repository from the dropdown
- Give `Repository Permissions` read and write access to
  - Contents
  - Issues
  - Pull Requests
  - Workflows
- Save your token for when setting up your GitHub environment

#### Set up GitHub Environment

- Create a [GitHub Environment](https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-deployments/managing-environments-for-deployment)
  - Go to your repository settings
  - Under `Code and automation` select environment
  - Click `New Environment` and provide a name
- In your GitHub Environment
  - Add token to the [Github Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets) in the repository:
    - `PUBLISH_GITHUB_PAT` (Your GitHub PAT)
    - `PYPI_TOKEN` (Your PyPI token created in when setting up PyPI)
  - Add to the [Github Variables](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/store-information-in-variables) in the repository:
    - `REPOSITORY_URL` (The repository you will be uploading to)

### ▶️ Deploying Using GitHub Action ▶️

- PREREQUISITES
  - Your extension package including `package.json` file
  - [Set up PyPI](#set-up-pypi)
  - [Set up GitHub Personal Access Token](#create-github-personal-access-token-pat)
  - [Set up GitHub Environment](#set-up-github-environment)
  - Read and write permissions to the branch you are deploying from
    - If you have branch protections requiring a pull request to merge into the branch you are deploying from (eg: main), allow the user with your GitHub PAT to bypass required pull requests in the `Allow specified actors to bypass required pull requests` section in your branch protection rules
- Go to GitHub Actions panel
- Run with workflow_dispatch `Step 1: Prep Release`
  - REQUIRED
    - Set `environment` to the name the environment with your secrets and variables
    - Set `version` to the new version of your package
      - For alpha versions append "-alpha.X" to your version where X is your alpha iteration
  - OPTIONAL
    - Set `branch` to the branch you want to target
    - Set `since` to the date or git reference you want to use the PRs since
    - Set `since_last_stable` if you only want to use PRs since the last stable release
    - Set `steps_to_skip` to a comma separated list of steps you want to skip in the release population step
- Run with workflow_dispatch `Step 2: Publish Release`
  - REQUIRED
    - Set `environment` to the name the environment with your secrets and variables
    - Set `tag` to the tag of the release you want to publish
- If both jobs succeeded, your deployment to PyPI should be successful

## Publishing to `conda-forge`

If the package is not on conda forge yet, check the documentation to learn how to add it: https://conda-forge.org/docs/maintainer/adding_pkgs.html

Otherwise a bot should pick up the new version publish to PyPI, and open a new PR on the feedstock repository automatically.
