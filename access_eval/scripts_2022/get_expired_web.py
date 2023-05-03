import pandas as pd
import os

original = pd.read_csv(str(os. getcwd())+"/../analysis//data_2022/Local_Elections_cleaned1.csv")
original = original.dropna(subset=['campaign_website_url'])
# after = pd.read_csv(str(os. getcwd())+"/../analysis//data_2022/2022-mayor-study-data.csv")
after = pd.read_csv(str(os. getcwd())+"/../analysis//data_2022/2022-local-elections-cat-data.csv")
df_all = original.merge(after.drop_duplicates(), on=['campaign_website_url'], 
                   how='left', indicator=True)
expired = df_all[df_all['_merge'] == 'left_only']
expired = expired.loc[:, ['names_x', 'location_x', 'party_x', "campaign_website_url", "candidate_page_x", "race", "election_result", "number_of_votes_for_race", "number_of_votes_for_candidate",
"vote_share", "camp_hand_x", "off_hand_x", "per_hand_x" ]] 
expired = expired.rename(columns={"names_x": "names", 
"location_x": "location", "electoral_position_x": "electoral_position", "candidate_page_x":"candidate_page", 
"camp_head_x":"camp_hand", "off_hand_x":"off_hand", "per_hand_x":"per_hand", "party_x":"party", "election_result_x":"election_result",
	"number_of_votes_for_race_x":"number_of_votes_for_race", "number_of_votes_for_candidate_x":"number_of_votes_for_candidate",
    "vote_share_x":"vote_share", "electoral_position_x":"electoral_position", "camp_hand_x":"camp_hand", "race":"electoral_position"
})