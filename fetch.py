import os
import pandas as pd
from datetime import datetime as dt, date
from github import Github

# make sure to set environment variables
token = os.environ.get("SECRET_TOKEN")
username = os.environ.get("GH_USERNAME")
repo_name = os.environ.get("REPO_NAME")

g = Github(token)
user = g.get_user(username)
repo = user.get_repo(repo_name)

# convert data frame to a csv file + output to directory
def main():
    df_clones = clones_to_df(fetch_clones(repo))

    path = './clones.csv'
    
    if len(df_clones):
        df_latest_clones = df_clones.tail(1)
        last_download_date = df_clones.tail(1).index.date[0]
        df_existing = pd.read_csv("clones.csv")        

        if not os.path.isfile(path):
            df_clones.to_csv("clones.csv")

        # if latest clone timestamp is not today's date, that means there were 
        # no clones today and we should just put 0 for "number of clones"
        elif last_download_date != date.today():
            df_todays_clones = pd.DataFrame(data=[0], index=pd.DatetimeIndex(data=[dt.now().replace(microsecond=0)], tz="UTC"))
            df_todays_clones.to_csv(path, mode='a', header=False)

        else: 
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

main()