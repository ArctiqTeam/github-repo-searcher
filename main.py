import requests
import datetime
import pytz
import logging
import argparse
import os
import base64

# GraphQL query to fetch all repositories in organizations with more than 100 repos
graphql_get_repos = """
query GetRepos($org: String!, $cursor: String) {
  organization(login: $org) {
    repositories(first: 100, after: $cursor) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        id
        name
      }
    }
  }
}
"""

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'
 
# Function to execute GraphQL query
def execute_graphql_query(query, variables, github_url, github_token):
    graphql_url = github_url.replace("/v3", "")
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.post(f"{graphql_url}/graphql", json={"query": query, "variables": variables}, headers=headers)
    return response.json()

def is_repository_empty(owner, repo, url, github_token):
    url = f'{url}/repos/{owner}/{repo}'
    headers = {'Authorization': f'token {github_token}'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data['size']
    else:
        print(f"Failed to fetch repository size information: {response.status_code}")
        return None
    
def search_in_content(content, search_strings):
    """Search for specified strings in a file's content."""
    for search_string in search_strings:
        if search_string in content:
            return True
    return False

def search_in_directory(owner, repo, github_url, directory, search_strings, github_token):
    """Search for specified strings in a specific directory within a GitHub repository."""
    headers = {'Authorization': f'token {github_token}'}
    url = f"{github_url}/repos/{owner}/{repo}/contents/{directory}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        contents = response.json()
        matched_files = []
        for item in contents:
            if item['type'] == 'file':
                # Only target .yml or .yaml files
                if item['name'].endswith('.yml') or item['name'].endswith('.yaml'):
                    file_url = item['url']  # Use the API URL to get the file content
                    file_response = requests.get(file_url, headers=headers)
                    if file_response.status_code == 200:
                        file_content = file_response.json().get('content', '')
                        decoded_content = base64.b64decode(file_content).decode('utf-8')
                        if search_in_content(decoded_content, search_strings):
                            matched_files.append(item['html_url'])
            elif item['type'] == 'dir':
                matched_files += search_in_directory(owner, repo, github_url, item['path'], search_strings, github_token)
        return matched_files
    elif response.status_code == 404:
        # Directory does not exist in the repository
        return []
    else:
        print(f"Failed to access directory {directory} in repository {owner}/{repo}")
        return []

def main(github_orgs, github_url, github_token, strings):
    for org in github_orgs:
        org = org.strip()
        cursor = None
        hasNextPage = True

        # Process repositories 100 repos at a time.
        while hasNextPage:
            variables = {"org": org, "cursor": cursor}
            response_data = execute_graphql_query(graphql_get_repos, variables, github_url, github_token)
            organization_data = response_data.get("data", {}).get("organization", {})
            repositories = organization_data.get("repositories", {})
            nodes = repositories.get("nodes", [])

            # Iterate through repositories in the organization
            for node in nodes:
                repo_name = node.get("name")
                is_empty = is_repository_empty(org, repo_name, github_url, github_token)

                if is_empty == 0:
                    print(f"{org}/{repo_name} is empty, skipping...")
                    print()

                print(color.BOLD + f'Searching repository {repo_name}...' + color.END)
                matched_files = search_in_directory(org, repo_name, github_url, ".github", strings, github_token)

                if matched_files:
                    print(color.RED + f'Files containing the specified strings in {org}/{repo_name}' + color.END)
                    print("")
                    for file_path in matched_files:
                        logging.info(f'{org}/{repo_name}: {file_path}')
                        print(f" - {file_path}")
                    print("")
                else:
                    print(color.GREEN + f'No files containing the specified strings found in {repo_name}' + color.END)
                    print("")

            pageInfo = repositories.get("pageInfo", {})
            hasNextPage = pageInfo.get("hasNextPage", False)
            cursor = pageInfo.get("endCursor")

        print("")
        print(color.BOLD + 'The source organization has no more repositories.' + color.END)
        print("")

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-token', default=os.environ.get('GITHUB_TOKEN', ""))
    parser.add_argument('-url', default=os.environ.get('GITHUB_URL', "https://api.github.com"))
    parser.add_argument('-orgs', nargs="+", default=[])
    parser.add_argument('-strings', nargs="+", default=['actions/upload-artifact'])
    args = parser.parse_args()

    if args.token == "":
        print("token not supplied with '-token' flag or by using the 'GITHUB_TOKEN' environment variable.  Aborting...")
        exit(1)

    # Setup logging
    est_timezone = pytz.timezone('US/Eastern')
    current_date = datetime.datetime.now(est_timezone)
    formatted_date = current_date.strftime("%Y-%m-%d-%H")
    logging.basicConfig(filename=f"github_repo_searcher_{formatted_date}.log", level=logging.INFO)

    main(args.orgs, args.url, args.token, args.strings)