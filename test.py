import argparse

def main():
    args = parse_args()
    owner_name, repo_name = args.repo.split("/")
    print(owner_name)

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