#log file processer...
import re,os,math
import tempfile,ftplib
import shutil
from pathlib import Path
from sealogfile.dexer.parse_log import parse_Text_log
from sealogfile import F3LogFile
import os,io,zipfile
#========== FTP Account SETUP ==============

ConsolePrint = True
directory = os.path.dirname(os.path.realpath(__file__))
FTP_USERNAME = 'rouser'
FTP_PASSWORD = 'rouser@357'

class log_obj_creater():
    def __init__(self,serial,oper,ts,code,ftp_zip_path):
        self.serial = serial
        self.oper = oper
        self.ts = ts
        self.code = code
        self.ziped = ftp_zip_path
        self.txt_log = f'{self.serial}_{self.oper}_{self.ts}_{self.code}.txt'
        self.directory = os.path.dirname(os.path.realpath(__file__))
        self.logfolder = os.path.join(self.directory,'LOGFiles')
        
        ftp_zip_path = ftp_zip_path.split('/')
        self.host = ftp_zip_path[:1][0]
        self.filename = ftp_zip_path[-1:][0]
        self.path = '/'+'/'.join(ftp_zip_path[1:-1]) #+ '/'
        ## check local log first if already have file then skip download and parse.
        local_zip = os.path.join(self.logfolder, self.filename)    # path in Local PC
        local_r = Path(local_zip.strip('.zip'))
        local_txt = os.path.join(self.logfolder,self.txt_log)
   
        if os.path.exists(local_txt):
            print('local exist .. notthing to do')
            self.logobj = self.setup_logobj(local_txt)
            return


        elif not os.path.exists(local_r):  ## r file not exist.
            if not os.path.exists(local_zip):  
                self.download_file_from_ftp(self.host,self.path,self.filename,local_zip)
                self.zip_extractor(local_zip,local_r)
        self.parse_log(local_r,local_txt)
        #remove zip and r ,,, keep only txt file.
        os.remove(local_zip)
        os.remove(local_r)

        if  os.path.exists(local_txt):
            self.logobj = self.setup_logobj(local_txt)
        
    def get_obj(self):
        return self.logobj


    def __str__(self):#B049956D_COMET_113_PASS.txt
        return f'{self.txt_log}'
    
    def setup_logobj(self,txt_log):
        this_logobj = F3LogFile(txt_log)
        # let put information into logobj.
        this_logobj.Product = ''
        this_logobj.Config = ''
        this_logobj.PartNum = ''
        this_logobj.SerialNo = self.serial
        this_logobj.SBR = ''
        this_logobj.Oper = self.oper
        this_logobj.ErrorMsg = self.code
        return this_logobj
    
    def download_file_from_ftp(self,host, path, filename,local_zip_file):
        # SBR_raw_path is optional to seperate zip file by SBR ( not followed FTP path.)
        try:
            if isinstance(host, str): # host just a string means new host.
                with ftplib.FTP(host, FTP_USERNAME, FTP_PASSWORD) as ftp_server:
                    ftp_server.cwd(path)
                    filename = filename
                    os.makedirs(os.path.dirname(local_zip_file), exist_ok=True)
                    ftp_server.retrbinary("RETR " + filename, open(local_zip_file, 'wb').write)
            return local_zip_file

        except Exception as e:
            print(f'error downloading log file {e}')
            return None
    
    def zip_extractor(self,zip_file,local_r):
        
        print(f'ZipFile located here:{zip_file}')
        print(''.join(zip_file.split('\\')[-1:]))
        r_filename = (''.join(zip_file.split('\\')[-1:])).strip('.zip')
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extract(r_filename, os.path.join(self.logfolder).replace('/',os.sep))
    
        r_file = os.path.join(self.logfolder,r_filename).replace('/',os.sep)
        return r_file
    
    def parse_log(self,r_file,output_file):
        with open(output_file,'wb') as outputfile:
            parse_Text_log(r_file,outputfile)
        return output_file

# Main application
if __name__ == "__main__":
    
    #def __init__(self,serial,oper,ts,code,ftp_zip_path):
    serial = "ABCDE"
    oper = 'TEST'
    ts = 99
    code= 'PASS'
    ftp_zip_path = "teppinasv001.seagate.com/prod/none/merlin/history/COMET/20/B04D062F.4905113404.r.zip"
    logprocess = log_obj_creater(serial,oper,ts,code,ftp_zip_path)
    # print(type(logprocess.logobj))
    print(logprocess.logobj.FileName)
    