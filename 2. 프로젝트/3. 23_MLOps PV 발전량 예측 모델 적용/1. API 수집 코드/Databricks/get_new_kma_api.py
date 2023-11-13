# Databricks notebook source
# MAGIC %md
# MAGIC # KMA History 수집
# MAGIC
# MAGIC - 기존 기상청 api -> 새 api(기상청 허브:https://apihub.kma.go.kr/) 통해 수집
# MAGIC - D-1 day 수집 
# MAGIC - 52개 site 수집
# MAGIC - 수기수집 또는 bulk수집할 경우 주석(####) 참고

# COMMAND ----------

import os
import requests
from requests_toolbelt import MultipartEncoder
import pandas as pd
from pytz import timezone
from azure.storage.blob import BlobServiceClient
from datetime import datetime, timedelta
import argparse


def main(
    site: str,
    api_key: str,
    azure_key: str
):
 
    now = datetime.now(timezone("Asia/Seoul"))
    yesterday = now - timedelta(days=1)
    date = yesterday.strftime('%Y%m%d')

    # date 결과를 저장할 리스트 초기화
    tm = []

    # 00:00부터 23:00까지 1시간 간격으로 날짜 및 시간 생성 및 리스트에 추가
    for hour in range(24):
        # 어제의 날짜와 시간을 계산하여 추가
        date_time = yesterday.replace(hour=hour, minute=0, second=0).strftime("%Y%m%d%H%M")
        tm.append(date_time)

    ## 1. API 조회 GET
    """
    수기/bulk 수집시 tm 필요없음
    """
    df = get_data(site,tm,api_key)
    #### 수기/bulk 수집할 때 해당 변수 사용 (위 변수는 주석처리) #### 
    #df = get_data(site,api_key)


    if df is None:
        return

    ## 2. csv 저장 -> blob에 저장
    load_csv(azure_key,df,site,date)


def get_data(site,tm,api_key):

    api_url = "https://apihub.kma.go.kr/api/typ01/url/kma_sfctm3.php"

    try:

        ## 파라미터 설정
        #### 수기/bulk 수집할 때는 tm1, tm2에 string 형식으로 날짜 입력 (예: '202309300000', '202310052300') #### 
        params = {
            'tm1' : tm[0],
            'tm2' : tm[23],
            'stn' : site,
            'help' : 0,
            'authKey' : api_key
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

        return df
    except requests.exceptions.RequestException as e:
        raise Exception(f"데이터를 가져오는 중 오류가 발생했습니다:\n {e}")


def load_csv(azure_key,df,site,date):

    # Blob Storage 정보
    STORAGEACCOUNTNAME = 'dlsvppprod'
    CONTAINERNAME = 'raw'

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


if __name__ == "__main__":

    ## Databricks 노트북 환경 ver
    # Databricks 노트북 환경에서 변수 입력
    dbutils.widgets.text("site", "")
    dbutils.widgets.text("api_key", "")
    dbutils.widgets.text("azure_key", "")

    # 변수 값을 가져옴
    site = dbutils.widgets.get("site")
    api_key = dbutils.widgets.get("api_key")
    azure_key = dbutils.widgets.get("azure_key")

    # main 함수 호출
    main(site, api_key, azure_key)



# COMMAND ----------


