import pandas as pd
import os
import subprocess

urls_to_process_df = pd.read_csv(str(os. getcwd())+"/access_eval/analysis/2022data/AttorneyGeneral.csv")
urls_to_process_df = urls_to_process_df.where(pd.notnull(urls_to_process_df), None)
for i, row in urls_to_process_df.iterrows():
    if row.CampWeb is not None:
        url_test = "url="+row.CampWeb
        proc_resp = subprocess.run(["make", "generate-report", str(url_test)])  # update the row.url with the actual column name
        print(f"row {i} is done!")