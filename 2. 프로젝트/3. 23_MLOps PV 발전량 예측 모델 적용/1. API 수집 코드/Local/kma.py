import os
import requests
from requests_toolbelt import MultipartEncoder
import pandas as pd
from pytz import timezone
from azure.storage.blob import BlobServiceClient
from datetime import datetime, timedelta
import argparse

api_url = "https://apihub.kma.go.kr/api/typ01/url/kma_sfctm3.php"

site = 217
date = '20231128'

try:

    ## 파라미터 설정
    #### 수기/bulk 수집할 때는 tm1, tm2에 string 형식으로 날짜 입력 (예: '202309300000', '202310052300') #### 
    params = {
        'tm1' : '202311280000',
        'tm2' : '202311282300',
        'stn' : site,
        'help' : 0,
        'authKey' : 'KMdox1HpT-SHaMdR6Z_ksw'
    }

    # 요청 보내기 (세션을 사용하여 인증 정보를 자동으로 추가)
    response = requests.get(api_url, params=params)

    # 오류 발생 시 예외 처리
    response.raise_for_status()
    data = response.text

    # 주어진 데이터를 줄 단위로 분할
    lines = data.strip().split('\n')

    # 데이터를 저장할 리스트
    data_list = []

    # 각 행을 처리하고 데이터 리스트에 추가
    for line in lines[4:-1]:  # 첫 4줄과 마지막 줄은 헤더 및 푸터 정보이므로 제외
        parts = line.split()  # 각 줄을 공백으로 분할
        data_list.append(parts)

    # 데이터 리스트를 Pandas DataFrame으로 변환
    df = pd.DataFrame(data_list, columns=[
        "TM", "STN", "WD", "WS", "GST_WD", "GST_WS", "GST_TM", "PA", "PS", "PT", "PR",
        "TA", "TD", "HM", "PV", "RN", "RN_DAY", "RN_JUN", "RN_INT", "SD_HR3", "SD_DAY", "SD_TOT", "WC", "WP", "WW",
        "CA_TOT", "CA_MID", "CH_MIN", "CT", "CT_TOP", "CT_MID","CT_LOW", "VS", "SS", "SI", "ST_GD", "TS", "TE_005", "TE_01", "TE_02", "TE_03",
        "ST_SEA", "WH", "BF", "IR", "IX"
    ])

except requests.exceptions.RequestException as e:
    raise Exception(f"데이터를 가져오는 중 오류가 발생했습니다:\n {e}")

# Blob Storage 정보
STORAGEACCOUNTNAME = 'dlsvppprod'
CONTAINERNAME = 'raw'
azure_key = 'WnK0exDjVEP4VDsuw1ixBT8TP5E2phXe++Kn0CwXTaNjeF53RxZTa8O0QQxA64ohRVruAryREreB+AStqhrrMA=='

# BlobServiceClient 초기화
blob_service_client = BlobServiceClient(account_url=f"https://{STORAGEACCOUNTNAME}.blob.core.windows.net", credential=azure_key)



# DataFrame을 CSV 파일로 저장
file_name = f"kma_history_{site}_{date}.csv"
#### 수기/bulk 수집할 때는 날짜 직접 입력 ex) 수기 수집할 때 : 20231103, bulk 수집할 때 : 20231103_20231105 ###
#file_name = f"kma_history_{site}_20231103.csv"

df.to_csv(file_name, index=False)

year = date[:4]
month = date[4:6]


# Blob 업로드
"""
bulk 수집 파일은 {site} 폴더 밑에 저장해야함. (년/월 폴더 밑 X)
"""
save_dir = f"/kma/history/asos/ver03/{site}/{year}/{month}"
#### bulk 수집할 때 해당 변수 사용 (위 변수는 주석처리)####
#save_dir = f"/kma/history/asos/ver03/{site}"

blob_client = blob_service_client.get_blob_client(container=CONTAINERNAME, blob=f"{save_dir}/{file_name}")

with open(file_name, "rb") as data:
    blob_client.upload_blob(data, overwrite=True)

os.remove(file_name)

print("CSV 파일이 Azure Blob Storage에 업로드되었습니다.")