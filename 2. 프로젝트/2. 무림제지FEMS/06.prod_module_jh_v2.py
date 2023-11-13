# 0) Import Lib & Connect to MariaDB

import pandas as pd
import joblib
import pymysql
import sys
sys.path.append('./' )    # 모듈 저장 위치 지정 
print(sys.path)
import FEMS_Moolim_SteamUsage_Predict_Module_v3 as MM
#from pandas import MultiIndex, Int64Index

# 1) Data Load
raw = MM.dataload()

# 2) Process
processed = MM.processing_raw(raw)

# 3) Inference
prediction = MM.pred_steamusage(raw, processed)

# 4) Storage
MM.storage(prediction)