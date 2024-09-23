### NOTE.... this is the script to do oracle sql query ...
### this writen for personal use only ... 
## there are still security concern on sql injection 
# ( to use in real production reminded to change to do params blinding.)!!!!!!

import pandas as pd
import oracledb
from datetime import datetime
import configparser
config = configparser.ConfigParser()
config.read('config.ini')

sql_user=config['SQL'].get('sql_user')
sql_password=config['SQL'].get('sql_password')
sql_host=config['SQL'].get('sql_host')
sql_port=config['SQL'].getint('sql_port')
sql_sid=config['SQL'].get('sql_sid')

def sql_param_spliter(param): 
    ## this function will convert multiple params like abc,def or abc_def to 'abc','def'
    param = param.replace('_',',')
    _list = ["'" + s.strip() + "'" for s in param.split(',')]
    splited = ",".join(_list)
    return splited

def date_time_converter(date_time_html):
    #Example HTML_DATE_TIME_LOCAL "2024-07-18T10:25"
    g_datetime = datetime.strptime(date_time_html, '%Y-%m-%dT%H:%M')
    formatted_date = g_datetime.strftime('%d-%m-%y:%H:%M')
    return formatted_date

def query_sql(query_sql,params=None,show_query = False):
    try:
        connection = oracledb.connect(
            user=sql_user,
            password=sql_password,
            host=sql_host,
            port=sql_port,
            sid=sql_sid
        )
        cursor = connection.cursor()
        cursor.execute(query_sql, parameters=params)

        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        user_asked_df = pd.DataFrame(rows, columns=columns)

    except oracledb.DatabaseError as e:
        error, = e.args
        print(f"Database error: {error.code} - {error.message}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
        print("Database connection closed.")
        return user_asked_df



def query_file_loc(serial_num="", sbr="", start="", end="",ts = "",show_query =False):
    # Base query
    query = \
'''SELECT a.SERIAL_NUM, a.SUB_BUILD_GROUP, cast(a.TRANS_SEQ as INT) AS TRANS_SEQ, b.EVENT_DATE, a.STATUS, b.PATH, b.HOST, b.FILE_NAME
FROM ods.SUB_BUILD_GROUP a, ods.FILE_LOCATOR b
WHERE a.SERIAL_NUM = b.SERIAL_NUM  
AND a.TRANS_SEQ = b.TRANS_SEQ 
AND a.BIRTH_DATE=b.BIRTH_DATE
AND a.STATUS ='A'
'''
    # Add conditions based on the provided parameters
    if serial_num:
        serial_str = sql_param_spliter(serial_num)
        query += f" AND a.SERIAL_NUM IN ({serial_str}) "
    if sbr:
        sbr_str = sql_param_spliter(sbr)
        query += f" AND a.SUB_BUILD_GROUP in ({sbr_str}) "
    if start:
        start = date_time_converter(start)
        query += f" AND b.EVENT_DATE >= TO_DATE('{start}', 'DD-MM-YY:HH24:MI') "
    if end:
        end = date_time_converter(end)
        query += f" AND b.EVENT_DATE <= TO_DATE('{end}', 'DD-MM-YY:HH24:MI') "
    if ts:
        query+=  f" AND a.TRANS_SEQ in {ts} "
    query+=' ORDER BY b.EVENT_DATE DESC'
    return query_sql(query_sql=query,show_query = show_query)

def query_history(serial_num,trans_seq,show_query =False):
    # Base query
    query = \
'''SELECT e.FISCAL_DATE AS FD, e.TRANS_SEQ AS TS ,
e.EVENT_DATE AS DATE_TIME ,
e.EQUIP_ID AS EQP_ID ,
e.OPERATION AS OP ,
(CASE WHEN e.EVENT_STATUS ='P'
	THEN 'PASS'
	ELSE 'FAIL'
END) AS STATUS,
fl.FILE_TYPE AS RT,
fl."PATH"||'/'||fl.FILE_NAME AS LOGFILE,
'' AS "DRILL DOWN"
FROM ods.event e
LEFT outer JOIN ods.FILE_LOCATOR fl 
	ON e.SERIAL_NUM = fl.SERIAL_NUM 
	AND e.TRANS_SEQ = fl.TRANS_SEQ 
	AND e.EVENT_DATE = fl.EVENT_DATE 
WHERE e.SERIAL_NUM = :1
AND e.TRANS_SEQ = :2 
ORDER BY e.EVENT_DATE DESC
FETCH NEXT 10000 ROWS ONLY'''

    return query_sql(query_sql=query,params = [serial_num,trans_seq],show_query = show_query)

def logservice_history(serial,maxseq = None,show_query=False):
    query =\
'''SELECT e.SERIAL_NUM AS SERIAL_NUM , 
       CAST(e.TRANS_SEQ as integer) AS TRANS_SEQ,
       e.OPERATION AS OPERATION,
       '' AS RUN_TYPE,
       e.EVENT_STATUS AS EVENT_STATUS,
       '' AS ERROR_CODE,
       e.EQUIP_ID AS EQP_ID,
       e.SLOT AS SLOT,
       e.EVENT_DATE AS EVENT_DATE,
       '' AS DIAG_CODE,
       '' AS DIAG_REMARK,
       '' AS RWK_CODE,
       '' AS RWK_STATUS
FROM ods.event e
LEFT OUTER JOIN ods.FILE_LOCATOR fl 
    ON e.SERIAL_NUM = fl.SERIAL_NUM 
    AND e.TRANS_SEQ = fl.TRANS_SEQ 
    AND e.EVENT_DATE = fl.EVENT_DATE 
WHERE e.SERIAL_NUM = :1
'''
    if isinstance(maxseq,int):
        query+=f'FETCH NEXT {maxseq} ROWS ONLY'

    return query_sql(query_sql=query,params=[serial],show_query = show_query)

def logservice_fileloc(serial,show_query=False):
    query = \
'''--SERIAL_NUM,TRANS_SEQ,OPERATION,FILE_NAME,EVENT_DATE
SELECT SERIAL_NUM ,TRANS_SEQ ,OPERATION,FILE_NAME ,EVENT_DATE  FROM ods.FILE_LOCATOR fl 
WHERE SERIAL_NUM =:1
ORDER BY EVENT_DATE DESC
FETCH NEXT 10000 ROWS ONLY
'''
    return query_sql(query_sql=query,params=[serial],show_query = show_query)

def logservice_history_all(serial,maxseq = None,show_query=False):
    query = \
    '''SELECT 
    CAST(e.TRANS_SEQ as integer) as TS,
    e.EVENT_DATE as DATE_TIME,
    --e.SERIAL_NUM,
    e.EQUIP_ID as EQP_ID,
    e.OPERATION as OP,
    CASE 
        WHEN e.EVENT_STATUS = 'F' THEN COALESCE(clm.EVENT_FAIL_CODE, cum.EVENT_FAIL_CODE, pli.EVENT_FAIL_CODE,co.FAIL_CODE)
        WHEN e.EVENT_STATUS = 'P' THEN 'PASS'
        WHEN e.EVENT_STATUS = 'S' THEN 'START'
        ELSE e.EVENT_STATUS  -- This is optional if you want to keep any other status as is
    END AS STATUS,
    '' AS RT,
    CASE 
	    WHEN  fl.FILE_NAME IS not NULL THEN fl.HOST||'/' || fl."PATH" ||'/' || fl.FILE_NAME 
	    ELSE ''
	    END AS LOGFILE,
        '' AS ATTR
FROM 
    ODs.EVENT e
LEFT JOIN 
    ods.clmd clm ON e.SERIAL_NUM = clm.SERIAL_NUM 
                 AND e.TRANS_SEQ = clm.TRANS_SEQ 
                 AND e.EVENT_DATE = clm.EVENT_DATE
LEFT JOIN 
    ods.cumd cum ON e.SERIAL_NUM = cum.SERIAL_NUM 
                 AND e.TRANS_SEQ = cum.TRANS_SEQ 
                 AND e.EVENT_DATE = cum.EVENT_DATE
LEFT JOIN 
    ods.plid pli ON e.SERIAL_NUM = pli.SERIAL_NUM 
                 AND e.TRANS_SEQ = pli.TRANS_SEQ 
                 AND e.EVENT_DATE = pli.EVENT_DATE       
LEFT JOIN 
    ods.comet co ON e.SERIAL_NUM = co.SERIAL_NUM 
                 AND e.TRANS_SEQ = co.TRANS_SEQ 
                 AND e.EVENT_DATE = co.EVENT_DATE            
LEFT JOIN 
    ods.FILE_LOCATOR fl ON e.SERIAL_NUM = fl.SERIAL_NUM
                 AND e.TRANS_SEQ = fl.TRANS_SEQ  
                 AND e.EVENT_DATE = fl.EVENT_DATE          
WHERE 
    e.SERIAL_NUM = :1
AND e.EVENT_DATE > SYSDATE -100
ORDER BY 
    e.EVENT_DATE DESC
'''
    if isinstance(maxseq,int):
        query+=f'FETCH NEXT {maxseq} ROWS ONLY'

    return query_sql(query_sql=query,params=[serial],show_query = show_query)


# print(query_file_loc(serial_num="", sbr='CMTMB0MU-0,CMTMB0MU-1', start="", end="",ts = "",show_query =False))



