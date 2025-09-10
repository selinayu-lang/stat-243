"""
Problem 4 module for PS1
"""

import requests
import pandas as pd
import matplotlib.pyplot as plt


def get_commits(owner: str, repo: str) -> pd.DataFrame:
    """
    Get up to 100 recent commits from a GitHub repo.

    owner(str): the account that owns the repo, for example "numpy"
    repo(str): the name of the repo, for example "numpy"

    Returns a DataFrame with commit details.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    params = {"per_page": 100}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    # Extract relevant fields
    commits = []
    for c in data:
        commits.append({
            "sha": c.get("sha"),
            "author_name": c.get("commit", {}).get("author", {}).get("name"),
            "author_email": c.get("commit", {}).get("author", {}).get("email"),
            "date": c.get("commit", {}).get("author", {}).get("date"),
            "message": c.get("commit", {}).get("message"),
            "committer_login": (c.get("committer") or {}).get("login"),
        })

    return pd.DataFrame(commits)


def plot_commits_hist(df: pd.DataFrame) -> None:
    """
    Make a bar chart showing how many commits each user made.

    df: a DataFrame from get_commits

    Shows the plot directly, does not return anything.
    """
    counts = df["committer_login"].value_counts()

    plt.figure(figsize=(8, 5))
    counts.plot(kind="bar")
    plt.title("Commits per user")
    plt.xlabel("User")
    plt.ylabel("Number of commits")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


def get_top_committer(owner: str, repo: str, verbose: bool = True) -> dict:
    """
    Find the user with the most commits and get their GitHub info.

    owner(str): the account that owns the repo
    repo(str): the name of the repo
    verbose(bool, default=True): if True, also print a short summary

    Returns a dictionary with the user’s profile info.
    """
    df = get_commits(owner, repo)
    top_user = df["committer_login"].value_counts().idxmax()

    # Get user info
    url = f"https://api.github.com/users/{top_user}"
    response = requests.get(url)
    response.raise_for_status()
    user_info = response.json()

    if verbose:
        print(f"Top committer: {top_user}")
        print(f"Name: {user_info.get('name')}")
        print(f"Public repos: {user_info.get('public_repos')}")
        print(f"Followers: {user_info.get('followers')}")

    return user_info




def get_all_commits(owner: str, repo: str, max_pages: int = 10) -> pd.DataFrame:
    """
    Get commits from many pages of a GitHub repo.

    owner(str): the account that owns the repo
    repo(str): the name of the repo
    max_pages(int, default=10): number of pages to fetch, each page has up to 100 commits

    Returns a DataFrame with all the commits collected.
    """
    all_commits = []
    for page in range(1, max_pages + 1):
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        params = {"per_page": 100, "page": page}
        response = requests.get(url, params=params)
        if response.status_code != 200:
            break
        data = response.json()
        if not data:
            break

        # Save the basic details from each commit
        for c in data:
            all_commits.append({
                "sha": c.get("sha"),
                "author_name": c.get("commit", {}).get("author", {}).get("name"),
                "date": c.get("commit", {}).get("author", {}).get("date"),
                "committer_login": (c.get("committer") or {}).get("login"),
            })

    return pd.DataFrame(all_commits)
