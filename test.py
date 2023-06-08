from github import Github
import os
import argparse


def main():
    args = parse_args()
    owner_name, repo_name = args.repo.split("/")
    token = os.environ.get("SECRET_TOKEN")
    g = Github(token)
    user = g.get_user(owner_name)
    repo = user.get(repo_name)

    clones = repo.get_clones_traffic()
    
    print(clones["clones"])

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "repo",
        metavar="REPOSITORY",
        help="Owner and repository. Must contain a slash. "
        "Example: owner/repository"
    )

    args = parser.parse_args()
    return args

main()