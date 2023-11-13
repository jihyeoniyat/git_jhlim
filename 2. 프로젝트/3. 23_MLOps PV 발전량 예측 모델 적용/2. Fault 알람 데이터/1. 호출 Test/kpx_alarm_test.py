import requests
from requests_toolbelt import MultipartEncoder
import pandas as pd
from pytz import timezone
from azure.storage.blob import BlobServiceClient
from datetime import datetime, timedelta
import argparse
import os
import xml.etree.ElementTree as ET
import json


# 세션 생성
session = requests.Session()

## Login
url_login = 'https://essonm.ls-electric.com/api/login'
m = MultipartEncoder(fields = {'username': 'majin', 'password': '12345'}, encoding='utf-8')

response_login = session.post(url_login, data=m, headers={'Content-Type': m.content_type})

response_login.raise_for_status()  # 오류 발생 시 예외 처리


api_url = 'https://essonm.ls-electric.com/api/alarms'

# # API 요청을 위한 데이터
# data = {
#     'deviceIds': [
#         "YA.PV01.PCU01",
#         "YA.PV02.PCU01",
#         "YA.PV03.PCU01",
#         "YA.PV04.PCU01",
#         "YA.PV05.PCU01",
#         "YA.PV06.PCU01",
#         "YA.PV07.PCU01",
#         "YA.PV08.PCU01",
#         "YA.PV09.PCU01",
#         "YA.PV10.PCU01",
#         "YA.PV11.PCU01",
#         "YA.PV12.PCU01",
#         "YA.PV13.PCU01",
#         "YA.PV14.PCU01",
#         "YA.PV15.PCU01",
#         "YA.PV16.PCU01",
#         "YA.PV17.PCU01",
#         "YA.PV18.PCU01",
#         "YA.PV19.PCU01",
#         "YA.PV20.PCU01",
#         "YA.PV21.PCU01",
#         "YA.PV22.PCU01",
#         "YA.PV23.PCU01",
#         "YA.PV24.PCU01",
#         "YA.PV25.PCU01",
#         "YA.PV26.PCU01",
#         "YA.PV27.PCU01",
#         "YA.PV28.PCU01",
#         "YA.PV29.PCU01",
#         "YA.PV30.PCU01",
#         "YA.PV31.PCU01",
#         "YA.PV32.PCU01",
#         "YA.PV33.PCU01",
#         "YA.PV34.PCU01",
#         "YA.PV35.PCU01",
#         "YA.PV36.PCU01",
#         "YA.PV37.PCU01",
#         "YA.PV38.PCU01",
#         "YA.PV39.PCU01",
#         "YA.PV40.PCU01",
#         "YA.PV41.PCU01",
#         "YA.PV42.PCU01",
#         "YA.PV43.PCU01",
#         "YA.PV44.PCU01",  
#         "YA.PV45.PCU01"
#     ],
#     'types': ['StatusInfo'],
#     'unresolved': "true",
#     'startDate': '2023-03-23',
#     'tagIds': ['DIG_UNIT1_FLT_STOP_STTS']
# }

# API 요청을 위한 데이터
data = {
    'deviceIds': [
        "YA.ESS01.PCS01",
        "YA.ESS01.PCS02",        
        "YA.ESS01.PCS03",
        "YA.ESS01.PCS04",
    ],
    'types': ['Fault','StatusInfo'],
    'unresolved': False,
    'startDate': '2023-10-23',
    'tagIds': ['DIG_POFF_STTS','DIG_FLT_STTS']
}



# 요청 보내기
response = session.post(api_url, json=data, headers={'Content-Type': 'application/json'})

try:
    response.raise_for_status()
except requests.exceptions.HTTPError as errh:
    print(f'HTTP 오류 발생: {errh}')
except requests.exceptions.RequestException as err:
    print(f'요청 오류: {err}')



# JSON 응답 문자열을 파이썬 객체로 변환
result_data = response.json()

# 데이터프레임 생성
df = pd.json_normalize(result_data)
# 'statusInfoList'의 값들을 별도의 데이터프레임으로 만들기
status_info_list = []
for entry in result_data:
    for status_info in entry.get('statusInfoList', []):
        entry_dict = {
            'displayDisable': entry.get('displayDisable'),
            'statusInfoList_id': status_info.get('id'),
            'statusInfoList_value': status_info.get('value')
        }
        status_info_list.append(entry_dict)

status_info_df = pd.DataFrame(status_info_list)

# 'displayDisable' 컬럼을 기준으로 두 데이터프레임을 병합
merged_df = pd.merge(df, status_info_df, on='displayDisable', how='left')
merged_df = merged_df.drop("statusInfoList", axis=1)

merged_df.to_csv('/Users/jihyeon/Desktop/test2.csv', index=False)


# ## JSON 파싱 -> list
# json_data = response.json()

# # 빈 리스트 생성
# data_list = []


# # JSON 데이터를 리스트에 추가
# for item in json_data['statusInfoList']:
#     data_list.append(item)

# # 리스트를 데이터프레임으로 변환
# df = pd.DataFrame(data_list)
# print(df)


# display(response)
