import pandas as pd

# Specify Deployment Year of interest
deploy_year = '2024'

# Read in the master list of all s3_keys
df_a = pd.read_csv("s3_keys.csv")

unique_deploy = set()

for index, row in df_a.iterrows():
    key = row["Key"]
    key_parts = key.split('/')

    if len(key_parts) > 3 and key_parts[1] == deploy_year:
        unique_deploy.add(key_parts[2])

list_deploys = [deploymentID for deploymentID in unique_deploy]
list_deploys.sort()

for deploymentID in list_deploys:
    print(deploymentID)

# 2024-05-25_WM_Boardwalk_F
# 2024-05-25_WM_Boardwalk_G
# 2024-06-03_UR011
# 2024-06-08_WM_Boardwalk_D

## Exported 2024-07-11: 
# 2024-06-29_WM_Boardwalk_D
# 2024-06-29_WM_Boardwalk_G
# 2024-07-06_WM_Boardwalk_G
# 2024-07-20_WM_Boardwalk_G_UR004
# 2024-07-20_WM_Boardwalk_D_UR010
# 2024-07-20_WM_DIS_A_UR016
# 2024-07-20_WM_DIS_B_UR007