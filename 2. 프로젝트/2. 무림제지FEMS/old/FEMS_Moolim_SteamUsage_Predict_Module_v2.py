#===============================================================================#
#   0) Import Lib
#   1) Connect to MariaDB
#   2) Data Load                                                                                                           
#   3) Process : 파생변수 생성                    
#   4) Inference : 예측 모델 적용 및 결과 생성
#   5) Storage                                

#   정확도 성능(MAPE) 검토 로직은 제외     
#===============================================================================#

###### 0) Import Lib

import pandas as pd
import joblib
import sys
import pymysql



###### 1) Connect to MariaDB

try:
    conn = pymysql.connect(
        user="fcstuser",
        password="fcstuser1!",
        host="ap.kfems.net",
        port=13306,
        database="fems"
    )
    print("Connect Success")
    
except pymysql.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()



###### 2) Data Load

# (1) 조회 query
select_query = """SELECT DateTime
    , STEAM
    , `320FIA7505:av`
    , `320LIC7525:con`
    , `320LIC7526:con`
    , `320LIC7527:con`
    , `320LIC7527:me`
    , `320LIC7528:con`
    , `320LIC7537:con`
    , `320LIC7537:me`
    , `320PIC7509:me`
    , `320PIC7510:con`
    , `320PIC7510:me`
    , `320PIC7511:con`
    , `320PIC7511:me`
    , `320PIC7533:con`
    , `320PIC7533:me`
    , `320PIC7544:con`
    , `320PIC7544:me`
    , `320TIC7540:me`
    , `320TIC7545:con`
    , `320TIC7545:me`
    , `PM3_AFTERDRYER_OP`
    , `PM3_ASH_FLOW_OP`
    , `PM3_ASH_FLOW_PV`
    , `PM3_ASH_PV`
    , `PM3_BASIS_WEIGHT_PV`
    , `PM3_BASIS_WEIGHT_PV2`
    , `PM3_CW_PV`
    , `PM3_MOISTURE_PV`
    , `PM3_MOISTURE_PV2`
    , `PM3_PREDRYER_OP`
    , `PM3_PREDRYER_PV`
    , `PM3_STOCK_CONSISTENCY_PV`
    , `PM3_STOCK_FLOW_PV`
    , `PM3_STOCK_VALVE_P_PV`
    , `PM3_AFTERDRYER_PV`
    , `320PIC7514:me`
    , `320PIC7513:me`
FROM (
        SELECT READ_DTTM AS DateTime
            , GROUP_CONCAT(IF(TAG_ID = 'STEAM', READ_VAL, NULL))                      AS STEAM
            , GROUP_CONCAT(IF(TAG_ID = '320LIC7525:con' , READ_VAL, NULL))            AS `320LIC7525:con`
            , GROUP_CONCAT(IF(TAG_ID = '320LIC7526:con' , READ_VAL, NULL))            AS `320LIC7526:con`
            , GROUP_CONCAT(IF(TAG_ID = '320LIC7527:con' , READ_VAL, NULL))            AS `320LIC7527:con`
            , GROUP_CONCAT(IF(TAG_ID = '320LIC7527:me' , READ_VAL, NULL))             AS `320LIC7527:me`
            , GROUP_CONCAT(IF(TAG_ID = '320LIC7528:con' , READ_VAL, NULL))            AS `320LIC7528:con`
            , GROUP_CONCAT(IF(TAG_ID = '320LIC7537:con' , READ_VAL, NULL))            AS `320LIC7537:con`
            , GROUP_CONCAT(IF(TAG_ID = '320LIC7537:me' , READ_VAL, NULL))             AS `320LIC7537:me`
            , GROUP_CONCAT(IF(TAG_ID = '320PIC7509:me' , READ_VAL, NULL))             AS `320PIC7509:me`
            , GROUP_CONCAT(IF(TAG_ID = '320PIC7510:con' , READ_VAL, NULL))            AS `320PIC7510:con`
            , GROUP_CONCAT(IF(TAG_ID = '320PIC7510:me' , READ_VAL, NULL))             AS `320PIC7510:me`
            , GROUP_CONCAT(IF(TAG_ID = '320PIC7511:con' , READ_VAL, NULL))            AS `320PIC7511:con`
            , GROUP_CONCAT(IF(TAG_ID = '320PIC7511:me' , READ_VAL, NULL))             AS `320PIC7511:me`
            , GROUP_CONCAT(IF(TAG_ID = '320PIC7533:con' , READ_VAL, NULL))            AS `320PIC7533:con`
            , GROUP_CONCAT(IF(TAG_ID = '320PIC7533:me' , READ_VAL, NULL))             AS `320PIC7533:me`
            , GROUP_CONCAT(IF(TAG_ID = '320PIC7544:con' , READ_VAL, NULL))            AS `320PIC7544:con`
            , GROUP_CONCAT(IF(TAG_ID = '320PIC7544:me' , READ_VAL, NULL))             AS `320PIC7544:me`
            , GROUP_CONCAT(IF(TAG_ID = '320TIC7540:me' , READ_VAL, NULL))             AS `320TIC7540:me`
            , GROUP_CONCAT(IF(TAG_ID = '320TIC7545:con' , READ_VAL, NULL))            AS `320TIC7545:con`
            , GROUP_CONCAT(IF(TAG_ID = '320TIC7545:me' , READ_VAL, NULL))             AS `320TIC7545:me`
            , GROUP_CONCAT(IF(TAG_ID = 'PM3_AFTERDRYER_OP' , READ_VAL, NULL))         AS `PM3_AFTERDRYER_OP`
            , GROUP_CONCAT(IF(TAG_ID = 'PM3_ASH_FLOW_OP' , READ_VAL, NULL))           AS `PM3_ASH_FLOW_OP`
            , GROUP_CONCAT(IF(TAG_ID = 'PM3_ASH_FLOW_PV' , READ_VAL, NULL))           AS `PM3_ASH_FLOW_PV`
            , GROUP_CONCAT(IF(TAG_ID = 'PM3_ASH_PV' , READ_VAL, NULL))                AS `PM3_ASH_PV`
            , GROUP_CONCAT(IF(TAG_ID = 'PM3_BASIS_WEIGHT_PV' , READ_VAL, NULL))       AS `PM3_BASIS_WEIGHT_PV`
            , GROUP_CONCAT(IF(TAG_ID = 'PM3_BASIS_WEIGHT_PV2' , READ_VAL, NULL))      AS `PM3_BASIS_WEIGHT_PV2`
            , GROUP_CONCAT(IF(TAG_ID = 'PM3_CW_PV' , READ_VAL, NULL))                 AS `PM3_CW_PV`
            , GROUP_CONCAT(IF(TAG_ID = 'PM3_MOISTURE_PV' , READ_VAL, NULL))           AS `PM3_MOISTURE_PV`
            , GROUP_CONCAT(IF(TAG_ID = 'PM3_MOISTURE_PV2' , READ_VAL, NULL))          AS `PM3_MOISTURE_PV2`
            , GROUP_CONCAT(IF(TAG_ID = 'PM3_PREDRYER_OP' , READ_VAL, NULL))           AS `PM3_PREDRYER_OP`
            , GROUP_CONCAT(IF(TAG_ID = 'PM3_PREDRYER_PV' , READ_VAL, NULL))           AS `PM3_PREDRYER_PV`
            , GROUP_CONCAT(IF(TAG_ID = 'PM3_STOCK_CONSISTENCY_PV' , READ_VAL, NULL))  AS `PM3_STOCK_CONSISTENCY_PV`
            , GROUP_CONCAT(IF(TAG_ID = 'PM3_STOCK_FLOW_PV' , READ_VAL, NULL))         AS `PM3_STOCK_FLOW_PV`
            , GROUP_CONCAT(IF(TAG_ID = 'PM3_STOCK_VALVE_P_PV' , READ_VAL, NULL))      AS `PM3_STOCK_VALVE_P_PV`
            , GROUP_CONCAT(IF(TAG_ID = '320FIA7505:av' , READ_VAL, NULL))             AS `320FIA7505:av`
            , GROUP_CONCAT(IF(TAG_ID = 'PM3_AFTERDRYER_PV' , READ_VAL, NULL))         AS `PM3_AFTERDRYER_PV`
            , GROUP_CONCAT(IF(TAG_ID = '320PIC7514:me' , READ_VAL, NULL))             AS `320PIC7514:me`
            , GROUP_CONCAT(IF(TAG_ID = '320PIC7513:me' , READ_VAL, NULL))             AS `320PIC7513:me`
        FROM (
                SELECT 'STEAM' AS TAG_ID
                    , TOT_DTTM AS READ_DTTM
                    , SUM(TOT_VAL) AS READ_VAL
                FROM EMS_ECC_TOT_DATA
                WHERE COM_ID = 'MRPAP'
                AND TOT_DTTM > DATE_SUB(STR_TO_DATE('20221220180000','%Y%m%d%H%i%s'), INTERVAL 450 MINUTE)    /*'20221220180000' 현재시각 변수처리*/
                AND TOT_DTTM <= STR_TO_DATE('20221220180000','%Y%m%d%H%i%s')                                  /*'20221220180000' 현재시각 변수처리*/
                AND ECC_ID = 'ECC000009'        /* FIXED */
                AND READ_OBJ_ID = 'ROI000003'   /* FIXED */
                GROUP BY TOT_DTTM
                UNION ALL
                SELECT T.TAG_ID
                    , T.READ_DTTM
                    , T.READ_VAL
                FROM EMS_TAG_READ_RAW_DATA T
                INNER JOIN EMS_ENRG_FCST_VAR V
                    ON T.COM_ID = V.COM_ID
                AND T.TAG_ID = V.TAG_ID 
                AND V.FCST_ID = '1'          /* FIXED */
                WHERE T.COM_ID = 'MRPAP'       /* FIXED */
                AND T.READ_DTTM > DATE_SUB(STR_TO_DATE('20221220180000','%Y%m%d%H%i%s'), INTERVAL 450 MINUTE)
                AND T.READ_DTTM <= STR_TO_DATE('20221220180000','%Y%m%d%H%i%s')
            ) A
        GROUP BY READ_DTTM
        ) A
WHERE STEAM >= 0
ORDER BY DateTime"""


# (2-1) query를 DB 서버에 전달 & 배열 형식으로 다 읽어와
cur.execute(select_query)
resultset = cur.fetchall()

# (2-2) dataframe 형으로 변환
raw = pd.DataFrame(resultset, columns=['DateTime'
    , 'STEAM'
    , '320FIA7505:av'
    , '320LIC7525:con'
    , '320LIC7526:con'
    , '320LIC7527:con'
    , '320LIC7527:me'
    , '320LIC7528:con'
    , '320LIC7537:con'
    , '320LIC7537:me'
    , '320PIC7509:me'
    , '320PIC7510:con'
    , '320PIC7510:me'
    , '320PIC7511:con'
    , '320PIC7511:me'
    , '320PIC7533:con'
    , '320PIC7533:me'
    , '320PIC7544:con'
    , '320PIC7544:me'
    , '320TIC7540:me'
    , '320TIC7545:con'
    , '320TIC7545:me'
    , 'PM3_AFTERDRYER_OP'
    , 'PM3_ASH_FLOW_OP'
    , 'PM3_ASH_FLOW_PV'
    , 'PM3_ASH_PV'
    , 'PM3_BASIS_WEIGHT_PV'
    , 'PM3_BASIS_WEIGHT_PV2'
    , 'PM3_CW_PV'
    , 'PM3_MOISTURE_PV'
    , 'PM3_MOISTURE_PV2'
    , 'PM3_PREDRYER_OP'
    , 'PM3_PREDRYER_PV'
    , 'PM3_STOCK_CONSISTENCY_PV'
    , 'PM3_STOCK_FLOW_PV'
    , 'PM3_STOCK_VALVE_P_PV'
    , 'PM3_AFTERDRYER_PV'
    , '320PIC7514:me'
    , '320PIC7513:me'])

# (3) raw 테이블 Datetime 제외 모두 float으로 변경
# (3-1) 날짜 컬럼을 index로 넘겨놓고
raw.set_index('DateTime',inplace=True)

# (3-2) 모든 컬럼 float으로 변경
raw = raw.astype('float')

# (3-3) index 리셋 
raw.reset_index(inplace=True)

print ("Select Success")



###### 3) Process

def processing_raw (raw) :
   
    # (0) 복사
    processed = raw.copy()

    # (1) 파생변수 생성 : 생산 월/일/시/분/요일
    processed['mon']=processed['DateTime'].dt.month
    processed['day']=processed['DateTime'].dt.day
    processed['hour']=processed['DateTime'].dt.hour
    processed['min']=processed['DateTime'].dt.minute
    processed['weekday']=processed['DateTime'].dt.weekday
    
    # (2) 영향인자 외 드롭
    return processed.drop(['DateTime', 'STEAM'], axis=1)



###### 4) Inference

def pred_steamusage (raw, processed) :
    
    # (1-1) XGBoost 또는,
    model = joblib.load('./FEMS_Moolim_ML_XGBoost_with_derived_variable_martV2.pkl')         # 모델 경로 지정 필요
    
    # (1-2) LightGBM
    # model = joblib.load('./FEMS_Moolim_ML_LightGBM_with_derived_variable_martV2.pkl')

    # (2) 15분 후 사용될 스팀량 예측
    y_pred = model.predict(processed)

    # (3) DateTime과 함께 테이블화
    prediction = pd.DataFrame(columns= ['DateTime', 'Y_pred'])
    prediction['DateTime'] = raw['DateTime'] + pd.Timedelta('15 minute')
    prediction['Y_pred'] = y_pred

    return prediction



###### 5) Storage

def storage (prediction) :
    ## 추가 query
    insert_query = "insert into ems_enrg_fcst_rslt \
        (COM_ID, FCST_ID, FCST_DTTM, FCST_VAL, REG_USER_NO, REG_DTTM, PROC_USER_NO, PROC_DTTM) \
        values ('MRPAP','1',%s, %s,'AI',sysdate(),'AI',sysdate())"

    # 'MRPAP','1','2022-12-22 18:15:00','5','AI',sysdate(),'AI',sysdate()

    ## for문으로 3번 결과 테이블 행길이만큼 insert반복
    row = len(prediction)

    for n in range(row):
        cur.execute(insert_query, (prediction.iloc[n,0],prediction.iloc[n,1]))
        conn.commit()

    print("insert success")
   
    # Close Connection
    conn.close()
    print("disconnect")


