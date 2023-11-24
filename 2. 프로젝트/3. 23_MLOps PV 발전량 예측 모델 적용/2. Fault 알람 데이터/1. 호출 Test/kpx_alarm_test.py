#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import requests
from requests_toolbelt import MultipartEncoder
import pandas as pd
from pytz import timezone
#from azure.storage.blob import BlobServiceClient


session = requests.Session()

url_login = 'https://essonm.ls-electric.com/api/login'
m = MultipartEncoder(fields = {'username': 'majin', 'password': '12345'}, encoding='utf-8')
response_login = session.post(url_login, data=m, headers={'Content-Type': m.content_type})

response_login.raise_for_status()  # 오류 발생 시 예외 처리


## api 데이터 호출
api_url = 'https://essonm.ls-electric.com/api/alarms'

# API 요청을 위한 데이터 - ESS(PCS)
data = {
    'deviceIds': [
        "YA.ESS01.PCS01",
        "YA.ESS01.PCS02",        
        "YA.ESS01.PCS03",
        "YA.ESS01.PCS04",
        "YA.ESS01.PCS05",
        "YA.ESS01.PCS06",        
        "YA.ESS01.PCS07",
        "YA.ESS01.PCS08",
        "YA.ESS01.PCS09",
        "YA.ESS01.PCS10",
        "YA.ESS01.PCS11",
        "YA.ESS01.PCS12",
        "YA.ESS01.PCS13",
        "YA.ESS01.PCS14",
        "YA.ESS01.PCS15",
        "YA.ESS01.PCS16",
        "YA.ESS01.PCS17",
        "YA.ESS01.PCS18",
        "YA.ESS01.PCS19",
        "YA.ESS01.PCS20",
        "YA.ESS01.PCS21",
        "YA.ESS01.PCS22",
        "YA.ESS01.PCS23",
        "YA.ESS01.PCS24",
        "YA.ESS01.PCS25",
        "YA.ESS01.PCS26",
        "YA.ESS01.PCS27",
        "YA.ESS01.PCS28",
        "YA.ESS01.PCS29",
        "YA.ESS01.PCS30",
        "YA.ESS01.PCS31",
        "YA.ESS01.PCS32",
        "YA.ESS01.PCS33",
        "YA.ESS01.PCS34",
        "YA.ESS01.PCS35",
        "YA.ESS01.PCS36",
        "YA.ESS01.PCS37",
        "YA.ESS01.PCS38",
        "YA.ESS01.PCS39"
    ],
    'types': ['Fault'],
    'unresolved': True,
    #'startDate': '2023-08-29',
    # 'endDate' : '2023-09-07',
    'tagIds': ['DIG_FLT_STTS'],     #'DIG_POFF_STTS' -> type,unresolved 삭제
    "pageNumber" : 1,
    "countPerPage" : 1
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


# "alarmMessageId": "DIG_FLT_STTS+0"가 포함된 딕셔너리만 남기기
filtered_fault = []

for entry in result_data:
    if 'alarmStatusList' in entry:
        entry['alarmStatusList'] = [status_dict for status_dict in entry['alarmStatusList'] if status_dict.get('alarmMessageId') == 'DIG_FLT_STTS+0']
        filtered_fault.append(entry)


# #"alarmMessageId"가 "DIG_FLT_STTS+0"인 딕셔너리만 필터링
# filtered_list = [entry for entry in result_data 
#                  if "alarmStatusList" in entry and any(status.get("alarmMessageId") == "DIG_FLT_STTS+0" for status in entry.get("alarmStatusList", []))]
        
# # "statusInfoList"가 "DIG_POFF_STTS"인 딕셔너리만 필터링
# # filtered_list = [entry for entry in result_data 
# #                  if "statusInfoList" in entry and any(status.get("id") == "DIG_POFF_STTS" for status in entry.get("statusInfoList", []))]


# 데이터프레임 생성
df = pd.json_normalize(filtered_fault)

# 'alarmStatusList'의 값들을 별도의 데이터프레임으로 만들기
alarm_status_list= []
for entry in filtered_fault:
    for alarm_status in entry.get('alarmStatusList', []):
        entry_dict = {
            'displayDisable': entry.get('displayDisable'),
            'alarmStatusList_alarmMessageId': alarm_status.get('alarmMessageId'),
            'alarmStatusList_status': alarm_status.get('status'), 
            'alarmStatusList_occurred': alarm_status.get('occurred'),
            'alarmStatusList_resolved': alarm_status.get('resolved')
        }
        alarm_status_list.append(entry_dict)

alarm_status_df = pd.DataFrame(alarm_status_list)


# 'statusInfoList'의 값들을 별도의 데이터프레임으로 만들기
status_info_list = []
for entry in filtered_fault:
    for status_info in entry.get('statusInfoList', []):
        entry_dict = {
            'displayDisable': entry.get('displayDisable'),
            'statusInfoList_id': status_info.get('id'),
            'statusInfoList_value': status_info.get('value')
        }
        status_info_list.append(entry_dict)

status_info_df = pd.DataFrame(status_info_list)


# 'displayDisable' 컬럼을 기준으로 두 데이터프레임을 병합
merged_df = pd.merge(df, alarm_status_df, on='displayDisable', how='left')
merged_df = pd.merge(merged_df, status_info_df, on='displayDisable', how='left')
merged_df = merged_df.drop("statusInfoList", axis=1)
merged_df = merged_df.drop("alarmStatusList", axis=1)


merged_df.to_csv('/Users/jihyeon/Desktop/ESS_FLT_filtered.csv', index=False)

# df.to_json('/Users/jihyeon/Desktop/ESS_filter_Resolved.json', orient='records', lines=Tru