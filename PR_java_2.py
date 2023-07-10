import requests
import pandas as pd
import re
from dateutil.parser import parse
from concurrent.futures import ThreadPoolExecutor
import time
from concurrent.futures import as_completed


# Function to get the names of top Java repositories from GitHub
def get_top_java_repos(token, max_repos=10):
    headers = {'Authorization': f'token {token}'}
    repos = []
    page = 1

    while len(repos) < max_repos:
        # Make a request to the GitHub API to get repositories sorted by the number of stars
        response = requests.get(f'https://api.github.com/search/repositories?q=language:java&sort=stars&page={page}',
                                headers=headers)
        data = response.json()
        # Extend the list of repository names
        repos.extend([repo['full_name'] for repo in data['items']])
        page += 1

    return repos[:max_repos]


# Function to get the file types from the diff URL of a pull request
def get_file_types_from_diff(token, diff_url):
    headers = {'Authorization': f'token {token}'}
    response = requests.get(diff_url, headers=headers)
    diff_content = response.text

    # Extract the file paths from the diff content using regex
    file_paths = re.findall(r"diff --git a/(.*?) b/(.*?)\n", diff_content)
    # Get the file types by splitting the file path on the '.' character and getting the last element
    file_types = {path.split('.')[-1] for paths in file_paths for path in paths}

    return list(file_types)


# Function to get data for all pull requests in a given repository
def get_pr_data(token, repo):
    headers = {'Authorization': f'token {token}'}
    prs = []
    page = 1

    while True:
        try:
            # Make a request to the GitHub API to get all pull requests for the repository
            response = requests.get(f'https://api.github.com/repos/{repo}/pulls?state=all&page={page}&per_page=100',
                                    headers=headers)
            data = response.json()

            if not data:
                break

            for pr in data:
                # Get the file types from the diff URL
                file_types = get_file_types_from_diff(token, pr['diff_url'])
                # Calculate the processing time of the pull request
                created_at = parse(pr['created_at'])
                closed_at = parse(pr['closed_at']) if pr['closed_at'] else None
                process_time = (closed_at - created_at).total_seconds() if closed_at else None

                # Append the pull request data to the list
                prs.append({
                    'repo': repo,
                    'pr_id': pr['id'],
                    'title': pr['title'],
                    'user': pr['user']['login'],
                    'created_at': pr['created_at'],
                    'updated_at': pr['updated_at'],
                    'closed_at': pr['closed_at'],
                    'is_merged': pr['merged_at'] is not None,
                    'file_types': file_types,
                    'process_time': process_time
                })
            page += 1
        except Exception as e:
            print(f"Error while processing repo {repo}: {str(e)}")
            # Retry after a delay
            time.sleep(5)

    return prs


# Function to process a repository (get all pull requests data)
def process_repo(token, repo):
    return get_pr_data(token, repo)


# The main part of the script
token = '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'
top_java_repos = get_top_java_repos(token)

all_prs = []

# Use a thread pool to process repositories concurrently
with ThreadPoolExecutor(max_workers=5) as executor:
    future_to_repo = {executor.submit(process_repo, token, repo): repo for repo in top_java_repos}
    for future in as_completed(future_to_repo):
        repo = future_to_repo[future]
        try:
            # Get the result of the future and extend the list of all pull requests
            all_prs.extend(future.result())
        except Exception as e:
            print(f"Error while processing repo {repo}: {str(e)}")

# Save the data to a CSV file
df = pd.DataFrame(all_prs)
df.to_csv('top_java_repos_prs_add.csv', index=False)
