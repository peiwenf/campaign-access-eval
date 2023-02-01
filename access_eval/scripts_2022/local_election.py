#don't have the result info yet
#import packages
import pandas as pd
import os
import subprocess

#import scraped data
df = pd.read_csv(str(os. getcwd())+"/../data/LocalElections.csv")
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
list = [".gov",".us", "linkedin"]
for i, row in df.iterrows():
    if row.CampWeb is not None:
        row.CampWeb = row.CampWeb.lower()
        if (row.CampWeb[-1] == "/" and 
        row.CampWeb.count("/") > 3) or (row.CampWeb[-1] != "/" and 
        row.CampWeb.count("/") > 2) or (any(item in row.CampWeb for item in list)):
            row.CampWeb = None

# remove the locations that none of the candidate have a camp page
df['Location'] = df['Race'] + ", " + df['Area'].astype(str)+ ", " + df['County'] + ", "+ df['State'] 
df1 = df.groupby('Location', as_index=False).first()
noneLoc = df1[df1['CampWeb'].isnull()].Location.tolist()
df = df[~df['Location'].isin(noneLoc)]

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