#import packages
import pandas as pd
import os
import subprocess

#import scraped data
df = pd.read_csv(str(os. getcwd())+"/../analysis/data_2022/MayoralElections.csv")
df = df.where(pd.notnull(df), None)
df = df.dropna(how='all')

#Globals
COMMAND_TEMPLATE = (
    "gh workflow run "
    "--repo {repo} "
    "generate-report.yml "
    "-f url={link} "
)
REPO = "peiwenf/campaign-access-eval" # forked repo

#remove the position webs
list = [".gov",".us"]
for i, row in df.iterrows():
    if row.CampWeb is not None:
        row.CampWeb = row.CampWeb.lower()
        if (row.CampWeb[-1] == "/" and 
        row.CampWeb.count("/") > 3) or (row.CampWeb[-1] != "/" and 
        row.CampWeb.count("/") > 2) or (any(item in row.CampWeb for item in list)):
            row.CampWeb = None

# remove the cities that none of the candidate have a camp page
df1 = df.groupby('City', as_index=False).first()
noneCity = df1[df1['CampWeb'].isnull()].City.tolist()
df = df[~df['City'].isin(noneCity)]

# Add a column for election results 
df["Result"]="Lose"
currentS = ""
for i, row in df.iterrows():
    if row.City is not None:
        if row.City != currentS:
            currentS = row.City
            row.Result = "Win"

#run the github actions for a dataframe
for i, row in df.iterrows():
    if row.CampWeb is not None:
        command = COMMAND_TEMPLATE.format(
        repo=REPO,
        link=row.CampWeb,
        )
        proc_resp = subprocess.run(
            command.split(" "),
            check=True,
        )
        print(f"row {i} is done!")

# #download reports
# store_dir = str(os. getcwd())+"/../reports/Mayor"
# subprocess.run(["gh", "run", "download", "-D", store_dir])