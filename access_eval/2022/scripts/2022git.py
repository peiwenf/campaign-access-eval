#import packages
import pandas as pd
import os
import subprocess

#import scraped data
df = pd.read_csv(str(os. getcwd())+"/../data/AttorneyGeneral.csv")
df = df.where(pd.notnull(df), None)

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
        if (row.CampWeb[-1] == "/" and 
        row.CampWeb.count("/") > 3) or (row.CampWeb[-1] != "/" and 
        row.CampWeb.count("/") > 2) or (any(item in row.CampWeb for item in list)) \
        or(row.State.lower() in row.CampWeb.lower() and 
        (row.Names.lower().split()[-1] not in row.CampWeb.lower() and row.Names.lower().split()[0] not in row.CampWeb.lower())):
            row.CampWeb = None

# Add a column for election results 
df["Result"]="Lose"
currentS = ""
for i, row in df.iterrows():
    if row.State is not None:
        if row.State != currentS:
            currentS = row.State
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

#download reports
store_dir = str(os. getcwd())+"/../reports/AttorneyGeneral"
subprocess.run(["gh", "run", "download", "-D", store_dir])

# Delete the current workflows- runs after every dataframe - in terminal

# OWNER="peiwenf"
# REPO="campaign-access-eval"

# # list workflows
# subprocess.run(["gh", "api", "-X", "GET", \
# "repos/peiwenf/campaign-access-eval/actions/workflows", "|", "jq", ".workflows[]", "|", \
#     ".name,.id"])

# gh api -X GET repos/peiwenf/campaign-access-eval/actions/workflows | jq '.workflows[] | .name,.id'

# # copy the ID of the workflow you want to clear and set it
# WORKFLOW_ID=45319078

# # list runs
# gh api -X GET /repos/$OWNER/$REPO/actions/workflows/$WORKFLOW_ID/runs | jq '.workflow_runs[] | .id'

# # delete runs (you'll have to run this multiple times if there's many because of pagination)
# gh api -X GET /repos/$OWNER/$REPO/actions/workflows/$WORKFLOW_ID/runs | jq '.workflow_runs[] | .id' | xargs -I{} gh api -X DELETE /repos/$OWNER/$REPO/actions/runs/{}