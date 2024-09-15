from flask import Flask, request,Response,send_file
import zipfile
from dexer.parse_log import parse_Text_log
from log_survivor_service_ultimate import download_file_from_ftp
import sql_query
import os,io
import urllib
import pandas as pd
app = Flask(__name__)
#http://tkddosfeh.kor.thai.seagate.com/drv/eventhist/eh.asp?serial_num=B040273T&site=TTP&unit_type=CET&server_type=ODS&rows_per_page=50
#http://ttcomet-logserv01.tep.thai.seagate.com
#/logservice/serial,transaction/B040273T,1925/text?line_length=512

myhome_setup = False
if myhome_setup:
    bypass_oracleSql = False
    directory = os.path.dirname(os.path.realpath(__file__))
    BASE_DIR = os.path.join(directory,'Log_survivor_data').replace('\\',os.sep)
else:
    bypass_oracleSql = False
    BASE_DIR = os.path.join('C:\\','Log_survivor_data').replace('\\',os.sep)

SESSION_FILE_DIR = os.path.join(BASE_DIR, 'logs', 'session').replace('\\',os.sep)
local_dir = os.path.join(BASE_DIR, 'local_server','Downloaded').replace('\\',os.sep)

@app.route('/fakelogservice/<path:datafilters>/<path:valuetofill>/text')
def fakelogservice(datafilters,valuetofill):
    
    # Split the serial_and_eventid path to separate serial and eventid
    selected = valuetofill.lower().split(',')
    filters = datafilters.lower().split(',')

    for idx,filter in enumerate(filters):
        print(f'{filter} = {selected[idx]}')
    serial = None
    trans = None
    if 'serial' in filters: serial = selected[filters.index('serial')].upper()
    if 'transaction'in filters: trans = selected[filters.index('transaction')]
    
    # Get the query parameter
    line_length = request.args.get('line_length')
    qery = ''
    print(f'serial {serial}, trans {trans}')
    if serial and trans:
        query = sql_query.query_file_loc(serial_num=serial,ts = trans,show_query = True)
        ## now we have file path and location.. let look into local pc if the file exist.
        print(query)
        query.to_csv("dddd.csv")
        sbr = query['SUB_BUILD_GROUP'][0]
        host = query['HOST'][0]
        path = query['PATH'][0]
        file_name = query['FILE_NAME'][0]
        # let check on raw data folder first...
        session_folder_file = os.path.join(SESSION_FILE_DIR,sbr,'raw',file_name).replace('\\',os.sep)
        local_download_file =os.path.join(local_dir,path,file_name).replace('\\',os.sep)
        local_processing_dir =os.path.join(local_dir).replace('\\',os.sep)
        print('======================')
        print(session_folder_file)
        print(local_download_file)
        zip_file = None
        if os.path.isfile(session_folder_file):
            zip_file = session_folder_file 
        if os.path.isfile(local_download_file):
            zip_file = local_download_file 
        if zip_file == None:
            print("no local file found.. lets download from FTP")
            zip_file,_=download_file_from_ftp(host = host,path = path,filename=file_name,local_dir=local_processing_dir)

        print(f'ZipFile located here:{zip_file}')
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extract(file_name.strip('.zip'), os.path.join(local_dir).replace('\\',os.sep))
        r_file = os.path.join(local_dir,file_name.strip('.zip')).replace('\\',os.sep)
        temp_output_buffer = io.BytesIO()
        parse_Text_log(r_file,temp_output_buffer)
        temp_output_buffer.seek(0)
        print(temp_output_buffer)
        return send_file(temp_output_buffer, as_attachment=False,mimetype='text/plain')
    else:
        return('missing serial or transtraction')


@app.route('/fakelogservice/serial/~/history', methods=['POST'])
def historyservice():
    # Get the raw POST data
    df = pd.DataFrame
    print('running here ==============')
    batch_data = request.form.get('_batchData')
    batch_url = request.form.get('_batchUrl')
    print('here....')
    # Extract the serial (drivesn) from batch_data or URL if needed
    serial = batch_data
    if serial:
        
        print(serial)
        df = sql_query.logservice_history(serial)
        print(df)
        df.to_csv('tmp_file.csv',index=False)
        return send_file('tmp_file.csv', as_attachment=False,mimetype='text/plain')



@app.route('/fakelogservice/serial/~/list', methods=['POST'])
def listservice():
    # Get the raw POST data
    df = pd.DataFrame
    print('running here ==============')
    batch_data = request.form.get('_batchData')
    batch_url = request.form.get('_batchUrl')
    print('here....')
    # Extract the serial (drivesn) from batch_data or URL if needed
    serial = batch_data
    if serial:
        
        print(serial)
        df = sql_query.logservice_fileloc(serial)
        print(df)
        df.to_csv('tmp_file.csv',index=False)
        return send_file('tmp_file.csv', as_attachment=False,mimetype='text/plain')


@app.route('/fakehistory', methods=['POST'])
def fakehistory():
    # Get the query parameter
    serial = request.args.get('serial')
    df = pd.DataFrame
    print(f'serial {serial}')
    if serial :
        df = sql_query.query_user_files(serial_num=serial,show_query = True)
        return Response(df.to_json(orient="records"), mimetype='application/json')
        #return send_file(r"c:\var\merlin\cfgs\MARLINBPLOS--MAS_230901_WC\scripts\Dex\rocker.txt")
    else:
        return('missing serial or transtraction')
    
if __name__ == '__main__':
    app.run(debug=True)


