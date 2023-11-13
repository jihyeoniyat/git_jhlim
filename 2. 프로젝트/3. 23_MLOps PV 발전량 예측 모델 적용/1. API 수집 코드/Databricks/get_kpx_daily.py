# Databricks notebook source
# MAGIC %md
# MAGIC # KPX Daily 수집
# MAGIC
# MAGIC - O&M센터로부터 API를 이용해 데이터 수집
# MAGIC - D-3 day ~ D-1 day 수집 (KPX 계량값이 변경될 수 있으므로 3일치를 가져온다.)
# MAGIC - 52개 site 수집
# MAGIC - 수기수집 또는 bulk수집할 경우 주석(####) 참고
# MAGIC
# MAGIC - ver03 : essMeteredMap 컬럼 추가 

# COMMAND ----------

dbutils.widgets.text("id_site", "")

# COMMAND ----------

id_site = dbutils.widgets.get("id_site")
account_key = dbutils.secrets.get(scope="key-vpp-prod", key="Storage-Key-dlsvppprod")

# COMMAND ----------

from datetime import datetime, timedelta

import requests
import pandas as pd
from pytz import timezone
from requests_toolbelt import MultipartEncoder
from azure.gen2 import StorageClient
from azure.gen2.helper import upload_to_csv

# COMMAND ----------

def main(id_site: str, account_key: str):
    now = datetime.now(timezone("Asia/Seoul"))
    three_days_ago = now - timedelta(days=3)
    yesterday = now - timedelta(days=1)

    ## 1. O&M 로그인
    session = login()

    # site_id / -3days
    date_format = "%Y-%m-%d"
    base_date = now.strftime(date_format)

    from_date = three_days_ago.strftime(date_format)
    to_date = yesterday.strftime(date_format)

    #### 수기 & bulk 수집할 때 해당 변수 사용 (위 변수는 주석처리)####
    # from_date = '2023-09-30'
    # to_date = '2023-10-05'

    ## 2. 일 발전량 조회 GET
    key = dbutils.secrets.get(scope="key-vpp-prod", key="KPX-API-ServiceKey")
    data = get_data(session, id_site, from_date, to_date, key)

    if data is None:
        return

    ## 3. dataframe으로 변경

    # 날짜 문자열을 datetime 객체로 변환
    date1 = datetime.strptime(from_date, date_format)
    date2 = datetime.strptime(to_date, date_format)
    length =(date2 - date1).days

    df = make_dataframe(data, base_date, length)

    ## 4. csv 저장 -> blob에 저장
    upload_data(account_key, df, id_site, from_date, to_date)


# COMMAND ----------

def login():
    """
    O&M 로그인
    """

    # 세션 생성
    session = requests.Session()

    ## Login
    url_login = "https://essonm.ls-electric.com/api/login"
    
    account_info = MultipartEncoder(fields = {'username': 'majin', 'password': '12345'}, encoding='utf-8')

    response_login = session.post(url_login, data=account_info, headers={'Content-Type': account_info.content_type},verify=False)

    response_login.raise_for_status()  # 오류 발생 시 예외 처리

    return session


def get_data(session, id_site, from_date, to_date, key):
    """
    -3일 ~ -1일 발전량 조회 데이터 호출
    """

    api_url = "https://essonm.ls-electric.com/api/vpp/history/daily"

    try:
        ## 파라미터 설정
        params = {
            "aliases": id_site,
            "fromDate": from_date,
            "toDate" : to_date,
            "API-KEY" : key
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
        return json_data

    except requests.exceptions.RequestException as error:
        raise Exception(f"데이터를 가져오는 중 오류가 발생했습니다:\n {error}")

def make_dataframe(data, base_date, length):
    """
    JSON 형태 -> 데이터프레임 변경
    """
    list_tmp_df = []
    for num in range(length+1):
        location_name = data[num]["alias"]
        datetime = data[num]["dateTime"]
        datetime, _ = datetime.split('T')
        error_rate = data[num]["errorRate"]

        arr = []
        for temp in data[num]["data"]:
            forecast_input = temp["forecastInput"]
            renamed = dict((f"input_{key}", val) for key, val in forecast_input.items())

            del temp["forecastInput"]

            temp.update(renamed)
            arr.append(temp)

        df = pd.DataFrame(arr)

        df["location_name"] = location_name
        df["baseDate"] = base_date 
        df["datetime"] = datetime
        df["error_rate"] = error_rate

        list_tmp_df.append(df)

    df = pd.concat(list_tmp_df, ignore_index=True)

    return df


def upload_data(account_key, df, id_site, from_date, to_date):
    # Blob Storage 정보
    STORAGE_ACCOUNT_NAME = "dlsvppprod"
    CONTAINER_NAME = "raw"

    storage = StorageClient(STORAGE_ACCOUNT_NAME, account_key)

    year, month, _ = from_date.split('-')

    # DataFrame을 CSV 파일로 저장
    file_name = f"kpx_history_{id_site}_{from_date}_{to_date}.csv"

    """
    bulk 수집 파일은 {id_site} 폴더 밑에 저장해야함. (년/월 폴더 밑 X)
    """
    blob_path = f"{CONTAINER_NAME}/kpx/daily/ver03/{id_site}/{year}/{month}/{file_name}"
    #### bulk 수집할 때 해당 변수 사용 (위 변수는 주석처리) #### 
    #blob_path = f"{CONTAINER_NAME}/kpx/daily/ver02/{id_site}/{file_name}"
    
    blob = storage.get_blob(blob_path)

    upload_to_csv(blob, df, index=False)

    print("CSV 파일이 Azure Blob Storage에 업로드되었습니다.")

# COMMAND ----------

main(id_site, account_key)

# COMMAND ----------


