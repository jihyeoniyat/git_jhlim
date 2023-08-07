import requests
from requests_toolbelt import MultipartEncoder
import pandas as pd
import csv
from pytz import timezone
from azure.storage.blob import BlobServiceClient
from datetime import datetime, timedelta
import argparse
import os


def main(
    site: str,
    key: str
):
    now = datetime.now(timezone("Asia/Seoul"))
    yesterday = now - timedelta(days=1)
    
    ## 1. O&M 로그인
    session = login()

    # site_id / yesterdays
    aliases = site
    fromDate = yesterday.strftime('%Y-%m-%d')

    ## 2. 일 발전량 조회 GET
    data = get_data(session, aliases, fromDate)
    
    ## 3. dataframe으로 변경
    df = make_dataframe(data)

    #  csv 저장 -> blob에 저장
    azure_key = key
    load_csv(azure_key,df,aliases,fromDate)


def login():
    """
    O&M 로그인
    """

    # 세션 생성
    session = requests.Session()

    ## Login
    url_login = "https://essonm.ls-electric.com/api/login"
    m = MultipartEncoder(fields = {'username': 'majin', 'password': '12345'}, encoding='utf-8')

    response_login = session.post(url_login, data=m, headers={'Content-Type': m.content_type})

    response_login.raise_for_status()  # 오류 발생 시 예외 처리

    return session

def get_data(session, aliases, fromDate):
    """
    어제(yesterday) 일 발전량 조회 데이터 호출
    """

    api_url = "https://essonm.ls-electric.com/api/vpp/history/daily"

    try:

        ## 파라미터 설정
        params = {
            'aliases': aliases,
            'fromDate': fromDate
        }

        ## 요청 보내기 (세션을 사용하여 인증 정보를 자동으로 추가)
        response = session.get(api_url, params=params)

        response.raise_for_status()  # 오류 발생 시 예외 처리

        ## JSON 파싱 -> list
        json_data = response.json()

        # json_data가 비어 있는 경우
        if not json_data:  
            print("데이터가 없습니다. 작업을 건너뜁니다.")
            return None

        ## 인덴트를 사용하여 JSON 데이터 출력 -> str
        #jd = json.dumps(json_data, indent=4, ensure_ascii=False)
        #print(jd, type(jd))  

        return json_data
    except requests.exceptions.RequestException as e:
        print(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
        return None

def make_dataframe(data):
    """
    JSON 형태 -> 데이터프레임 변경
    """

    location_name = data[0]["alias"]
    datetime = data[0]["dateTime"]
    datetime, _ = datetime.split('T')
    error_rate = data[0]["errorRate"]

    arr = []
    for temp in data[0]["data"]:

        forecastInput = temp["forecastInput"]
        renamed = dict((f"input_{key}", val) for key, val in forecastInput.items())

        del temp["forecastInput"]

        temp.update(renamed)
        arr.append(temp)
    
    df = pd.DataFrame(arr)

    df["location_name"] = location_name
    df["datetime"] = datetime
    df["error_rate"] = error_rate
    df["tradeHour"] = df["tradeHour"] - 1

    return df

def load_csv(azure_key, df, aliases, fromDate):

    # Blob Storage 정보
    STORAGEACCOUNTNAME = 'dlsvppprod'
    CONTAINERNAME = 'raw'

    # BlobServiceClient 초기화
    blob_service_client = BlobServiceClient(account_url=f"https://{STORAGEACCOUNTNAME}.blob.core.windows.net", credential=azure_key)

    # DataFrame을 CSV 파일로 저장
    file_name = f"kpx_history_{aliases}_{fromDate}.csv"
    df.to_csv(file_name, index=False)

    year, month, _ = fromDate.split('-')

    # Blob 업로드
    save_dir = f"/kpx/daily/ver02/{aliases}/{year}/{month}"
    blob_client = blob_service_client.get_blob_client(container=CONTAINERNAME, blob=f"{save_dir}/{file_name}")

    with open(file_name, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

    os.remove(file_name)

    print("CSV 파일이 Azure Blob Storage에 업로드되었습니다.")


if __name__ == "__main__":

    ### 로컬 환경 ver
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--site", type=str)
    # parser.add_argument("--key", type=str)
    # args = parser.parse_args()

    # main(**vars(args))

    ### Databricks 노트북 환경 ver
    # Databricks 노트북 환경에서 변수 입력
    dbutils.widgets.text("site", "")
    dbutils.widgets.text("key", "")

    # 변수 값을 가져옴
    site = dbutils.widgets.get("site")
    key = dbutils.widgets.get("key")

    # main 함수 호출
    main(site, key)

