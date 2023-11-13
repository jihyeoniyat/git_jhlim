import requests
from requests_toolbelt import MultipartEncoder
import pandas as pd
from pytz import timezone
from azure.storage.blob import BlobServiceClient
from datetime import datetime, timedelta
import argparse
import os
import xml.etree.ElementTree as ET

api_url = "https://apihub.kma.go.kr/api/typ01/url/kma_sfcdd.php"

## 파라미터 설정
params = {
    'tm' : 20230912,
    'stn' : 112,
    'help' : 0,
    'disp' : 0,
    'authKey' : 'KMdox1HpT-SHaMdR6Z_ksw'
}


# 요청 보내기 (세션을 사용하여 인증 정보를 자동으로 추가)
response = requests.get(api_url, params=params)

# 오류 발생 시 예외 처리
response.raise_for_status()

data_list = [response.text]
df = pd.DataFrame(data_list)

response.to_csv('C:/Users/임지현/Desktop/test3.csv', index=False)

# # XML 데이터 파싱
# xml_data = ET.fromstring(response.text)

# ## JSON 파싱 -> list
# json_data = response.json()

# # 빈 리스트 생성
# data_list = []


# # JSON 데이터를 리스트에 추가
# for item in json_data["estimated_actuals"]:
#     data_list.append(item)

# # 리스트를 데이터프레임으로 변환
# df = pd.DataFrame(data_list)


# display(response)
