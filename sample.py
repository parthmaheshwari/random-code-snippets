import boto3
# import os
import re
import requests
from requests_aws4auth import AWS4Auth
import json

region = 'us-west-2'  # e.g. us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'https://search-mydomain2-nvbh56gkrxbkirdsi2nljfnw3q.us-west-2.es.amazonaws.com'  # the Amazon ES domain, including https://
index = 's3-mgch'
type = 'dejoule'
url = host + '/' + index + '/' + type

headers = {"Content-Type": "application/json"}

s3 = boto3.client('s3')

#-----------------------------------------------------------------------------
# LOCAL TEST

# path = r"C:\Users\Parthmaheswari\Desktop"
# filename = "2018-12-19 00_00_41.log"
# Read every file in directory
# for filename in os.listdir(path):
#     with open(filename, "r") as f:
#         # Read each line of the file
#         for line in file:
#             print(line.split())
#             try:
#                 for i in escapeChr:
#                     line = line.replace(i, i.replace('"', '\\"'))
#                     json_arr.append(json.loads(line))
#             except:
#                 continue
#             jsonString = json.dumps(json_arr)
#             print(jsonString)
#--------------------------------------------------------------------------------



# Lambda execution starts here
def handler(event, context):
    for record in event['Records']:
        # print(event)
        # Get the bucket name and key for the new file
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # Get, read, and split the file into lines
        obj = s3.get_object(Bucket=bucket, Key=key)
        body = obj['Body'].read().decode('utf-8')
        lines = json.loads(body)
        #
        # # Fix the JSON
        for line in lines:
        #     try:
        #         for i in escapeChr:
        #             line = line.replace(i, i.replace('"', '\\"'))
        #             json_arr.append(json.loads(line))
        #     except:
        #         continue
            r = requests.post(url, auth=awsauth, json=line, headers=headers)

