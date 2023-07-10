import requests
import pandas as pd


def get_top_java_repos(token):
    headers = {'Authorization': f'token {token}'}
    repos = []

    for page in range(1, 11):
        response = requests.get(f'https://api.github.com/search/repositories?q=language:java&sort=stars&page={page}',
                                headers=headers)
        data = response.json()
        repos.extend([repo['full_name'] for repo in data['items']])

    return repos


def get_pr_data(token, repo):
    headers = {'Authorization': f'token {token}'}
    prs = []
    page = 1

    while True:
        response = requests.get(f'https://api.github.com/repos/{repo}/pulls?state=all&page={page}&per_page=100',
                                headers=headers)
        data = response.json()

        if not data:
            break

        for pr in data:
            prs.append({
                'repo': repo,
                'pr_id': pr['id'],
                'title': pr['title'],
                'user': pr['user']['login'],
                'created_at': pr['created_at'],
                'updated_at': pr['updated_at'],
                'closed_at': pr['closed_at'],
                'is_merged': pr['merged_at'] is not None
            })
        page += 1

    return prs


token = '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'
top_java_repos = get_top_java_repos(token)

all_prs = []

for repo in top_java_repos:
    all_prs.extend(get_pr_data(token, repo))

df = pd.DataFrame(all_prs)
df.to_csv('top_java_repos_prs.csv', index=False)
