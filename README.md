# GitHub Repo Searcher

This Python script is designed to search through repositories within specified GitHub organizations for specific strings within the `.github` directory of each repository for files that end in `.yml` or `.yaml`. It utilizes the GitHub GraphQL API to fetch repositories efficiently and then iterates through them to find matching content.

## Usage

To run the script, use the following command:

```bash
pip3 install -r requirements.txt
python3 main.py -orgs ArctiqDemos -strings actions/upload-artifact -token <GITHUB_TOKEN>
```

## Input Flags

The script accepts several input flags to customize its behavior. Below is a list of all available flags:

### `-token`

- **Description**: Specifies the GitHub personal access token to authenticate API requests.
- **Required**: Yes (either through this flag or the `GITHUB_TOKEN` environment variable).
- **Example**: `-token abc1234567890`

### `-url`

- **Description**: The GitHub API base URL. This is useful if you're working with GitHub Enterprise or a self-hosted GitHub instance.
- **Default**: `https://api.github.com`
- **Example**: `-url https://github.yourdomain.com/api/v3`

### `-orgs`

- **Description**: A list of GitHub organizations to search through.
- **Required**: Yes
- **Example**: `-orgs ArctiqTeam AnotherOrg`

### `-strings`

- **Description**: A list of strings to search for within the `.github` directory of each repository.
- **Default**: `['actions/upload-artifact']`
- **Example**: `-strings actions/upload-artifact actions/checkout`

## Environment Variables

- **GITHUB_TOKEN**: If the `-token` flag is not provided, the script will look for this environment variable to authenticate API requests.

## Example

Here’s an example command to run the script:

```bash
python3 main.py -orgs ArctiqTeam AnotherOrg -strings actions/upload-artifact actions/checkout -token abc1234567890
```

This command will:
- Search through the repositories in the organizations `ArctiqTeam` and `AnotherOrg`.
- Look for the strings `actions/upload-artifact` and `actions/checkout` within the `.github` directory of each repository.
- Use the provided GitHub token `abc1234567890` for authentication.

## Logging

The script automatically logs its operations to a file named `github_repo_explorer_<timestamp>.log`, where `<timestamp>` is the current date and time in the `US/Eastern` timezone. The log file is useful for auditing and reviewing the script's actions after it has completed.

---
