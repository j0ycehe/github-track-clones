import os
import pandas as pd
from datetime import datetime as dt, date
from github import Github
import argparse

# convert data frame to a csv file + output to directory
def main():
    args = parse_args()
    token = os.environ.get("SECRET_TOKEN")
    g = Github(token)
    repo = g.get_repo(args.repo)

    df_clones = clones_to_df(fetch_clones(repo))

    owner_name, repo_name = args.repo.split("/")

    stats_dir = './download-stats'
    if not os.path.exists(stats_dir):
        os.mkdir(stats_dir)
    
    path = os.path.join(stats_dir, f"{owner_name}_{repo_name}_daily_clones.csv")
    
    if len(df_clones):
        df_latest_clones = df_clones.tail(1)
        last_download_date = df_clones.tail(1).index.date[0]

        if not os.path.isfile(path):
            df_clones.to_csv(path)

        # only update csv file if latest clone timestamp matches today's date
        # i.e. there were clones today
        elif last_download_date == date.today():
            df_latest_clones.to_csv(path, mode='a', header=False)

# convert clone statistics to a data frame
def clones_to_df(clones): 
    timestamps = [] 
    total_clone_counts = []

    for c in clones: 
        timestamps.append(c.timestamp)
        total_clone_counts.append(c.count)

    df = pd.DataFrame(
        data = {
            "clone_count": total_clone_counts
        },
        index = pd.DatetimeIndex(data=timestamps, tz="UTC")
    )
    df.index.name = "date"
    return df

# get clone statistics 
def fetch_clones(repo):
    clones = repo.get_clones_traffic()
    return clones["clones"]

# get owner name and repo name
def parse_args():
    parser = argparse.ArgumentParser(
        description="Requires the environment variables REPO and SECRET_TOKEN to be set."
    )

    parser.add_argument(
        "repo",
        metavar="REPOSITORY",
        help="Owner and repository. Must contain a slash. "
        "Example: owner/repository"
    )

    args = parser.parse_args()
    return args

main()