import pandas as pd
import requests
import hdbscan
# from sklearn.cluster import DBSCAN

API_ENDPOINT = ""

# This is the input format of this program, an nx2 list, epoch against the corresponding value
sample_data = [[1547551080000,24],[1547551140000,24],[1547551200000,24],[1547551260000,24],[1547551320000,24],[1547551380000,24],[1547551440000,24
        ],[1547551500000,24],[1547551560000,30],[1547551620000,24],[1547551680000,24],[1547551740000,24],[1547551800000,24],[1547551860000,24]]


outlier_df = pd.DataFrame.from_records(sample_data,columns={'timestamp','values'})
outlier_df.set_index('timestamp',inplace=True)

# Locally stored file
# data = pd.read_json('mod_mgch_7-ra.json',orient='columns')
# outlier_df = pd.DataFrame.from_dict(data,orient='columns')
# outlier_df['timestamp'] = outlier_df['ra'].apply(lambda x:x[0])
# outlier_df['room_temp'] = outlier_df['ra'].apply(lambda x:x[1])
# outlier_df = outlier_df.drop(columns = ["ra"])
# outlier_df.set_index('timestamp',inplace=True)

# HDBSCAN with default settings
hdbscan_obj = hdbscan.HDBSCAN().fit_predict(outlier_df) # returns a list of outlier flags
outlier_df['outlier'] = hdbscan_obj # adds outlier column to the input dataframe

# DBSCAN
# dbscan_obj = DBSCAN(eps = 0.5, min_samples = 3).fit_predict(outlier_df)
# outlier_df['outlier_dbscan'] = dbscan_obj

# dataframe to json
outlier_json = outlier_df.to_json(orient='index') 
r = requests.post(url = API_ENDPOINT, data = outlier_json)
# print(outlier_json)