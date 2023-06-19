import os
import pandas as pd
from datetime import datetime as dt, date, timedelta
from github import Github
import argparse

# (1) output daily + cumulative download stats for this particular repo to directory
# (2) add repo's download stats to overall stats encompassing all repos
def main():
    args = parse_args()
    token = os.environ.get("SECRET_TOKEN")
    g = Github(token)
    repo = g.get_repo(args.repo)

    df_clones = clones_to_df(fetch_clones(repo))
    owner_name, repo_name = args.repo.split("/")

    stats_dir = './download-stats'
    daily_dir = 'daily'
    cum_dir = 'cumulative'
    if not os.path.exists(stats_dir):
        os.makedirs(os.path.join(stats_dir, daily_dir))
        os.makedirs(os.path.join(stats_dir, cum_dir))
    
    daily_path = os.path.join(stats_dir, daily_dir, f"{owner_name}_{repo_name}_daily_clones.csv")
    
    if len(df_clones):
        df_latest_clones = df_clones.tail(1)
        last_download_date = df_clones.tail(1).index.date[0]
        
        if not os.path.isfile(daily_path):
            patch_df(df_clones).to_csv(daily_path)

        # if latest clone timestamp is not today's date, that means there were 
        # no clones today and we should just put 0 for "number of clones"
        elif last_download_date != date.today():
            df_todays_clones = pd.DataFrame(data=[0], index=pd.DatetimeIndex(data=[dt.now().date()]))
            df_todays_clones.to_csv(daily_path, mode='a', header=False)

        else: 
            df_latest_clones.to_csv(daily_path, mode='a', header=False)

    elif os.path.isfile(daily_path):
        df_todays_clones = pd.DataFrame(data=[0], index=pd.DatetimeIndex(data=[dt.now().date()]))
        df_todays_clones.to_csv(daily_path, mode='a', header=False)
    
    # if this script is run for the first time and no clones were made
    # in the past 2 weeks, create a csv storing today's clone count (i.e. 0)
    else:
        df_todays_clones = pd.DataFrame(data={"clone_count": [0]}, index=pd.DatetimeIndex(data=[dt.now().date()]))
        df_todays_clones.index.name = "date"
        df_todays_clones.to_csv(daily_path)

    # generate cumulative downloads for this repo + output to directory
    cum_path = os.path.join(stats_dir, cum_dir, f"{owner_name}_{repo_name}_cum_clones.csv")
    df_cum = pd.read_csv(daily_path)
    df_cum['clone_count'] = df_cum['clone_count'].cumsum()
    df_cum.to_csv(cum_path, mode='w+', index=False)

    # update overall cumulative stats across all repos
    overall_cum_path = os.path.join(stats_dir, cum_dir, "all_repos_cumulative.csv")
    update_overall_cumulative(df_cum, overall_cum_path, args.repo)

def update_overall_cumulative(df_add, path, repo_name):
    df_latest_clones = df_add.tail(1)
    todays_date = df_latest_clones.iat[0, 0]
    todays_clone_count = df_latest_clones.iloc[0, 1]
    df_add = df_add.rename({"clone_count": repo_name}, axis=1)

    if not os.path.exists(path):
        df_add.insert(loc = 1, column = "Overall", value = df_add[repo_name])
        df_add.to_csv(path, index=False)
    
    # if column for this repo already exists in csv
    elif repo_name in pd.read_csv(path):
        df_overall = pd.read_csv(path) 
        # if csv already contains row for today
        if todays_date in df_overall['date'].values:
            df_overall.at[len(df_overall.index) - 1, repo_name] = todays_clone_count
            df_overall.at[len(df_overall.index) - 1, "Overall"] += todays_clone_count
            df_overall.to_csv(path, index=False)
        else:
            df_new_row = pd.DataFrame(columns=list(df_overall))
            df_new_row.at[0, "date"] = todays_date
            df_new_row.at[0, repo_name] = todays_clone_count
            df_new_row.at[0, "Overall"] = todays_clone_count
            df_new_row.to_csv(path, mode='a', header=False, index=False)
    else: 
        df_overall = pd.read_csv(path) 
        df_add = df_add.set_index('date')
        df_overall = df_overall.set_index('date')
        
        df_overall = pd.concat([df_overall, df_add], axis=1).sort_index()
        df_overall.fillna(0, inplace=True)
        df_overall['Overall'] += df_overall[repo_name]
        df_overall.to_csv(path)


# fill in dates where no clones were made with 0's
def patch_df(df):
    cur_date = df.index[0].date()
    todays_date = dt.now().date()
    row = 0
    delta = timedelta(days=1)

    while cur_date <= todays_date:
        missing_clones = pd.DataFrame({"clone_count": [0]}, index=pd.DatetimeIndex(data=[cur_date]))
        missing_clones.index.name = "date"

        if row >= len(df.index):
            df = pd.concat([df, missing_clones])
        elif df.index[row].date() != cur_date:
            df = pd.concat([df.iloc[:row], missing_clones, df.iloc[row:]])

        row += 1
        cur_date += delta   
    return df        

# convert clone statistics to a data frame
def clones_to_df(clones): 
    timestamps = [] 
    total_clone_counts = []

    for c in clones: 
        timestamps.append(pd.to_datetime(c.timestamp).date())
        total_clone_counts.append(c.count)

    df = pd.DataFrame(
        data = {
            "clone_count": total_clone_counts
        },
        index = pd.DatetimeIndex(data=timestamps)
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
        description="Requires the environment variable SECRET_TOKEN to be set."
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