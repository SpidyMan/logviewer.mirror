#log file processer...
import os
import ftplib
from pathlib import Path

from dex3 import dex_it
from sealogfile import F3LogFile
import os,zipfile
#========== FTP Account SETUP ==============
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
FTP_USERNAME=config['FTP'].get('FTP_USERNAME')
FTP_PASSWORD=config['FTP'].get('FTP_PASSWORD')
Remove_RAW_FILE = config['SETUP'].getboolean('Remove_Raw_LOG')
ConsolePrint = False
directory = os.path.dirname(os.path.realpath(__file__))

class log_obj_creater():
    def __init__(self,serial,oper,ts,code,ftp_zip_path,local_file = None):
        self.serial = serial
        self.oper = oper
        self.ts = ts
        self.code = code
        #print(f'{self.serial}_{self.oper}_{self.ts}_{self.code}-{ftp_zip_path}')
        if local_file and os.path.exists(local_file):
            self.logobj = self.setup_logobj(local_file)
            return ### just for testing  ... 

        
        self.txt_log = f'{self.serial}_{self.oper}_{self.ts}_{self.code}.txt'
        self.directory = os.path.dirname(os.path.realpath(__file__))
        self.logfolder = os.path.join(self.directory,'LOGFiles')
        local_txt = os.path.join(self.logfolder,self.txt_log)
        
        #check if local text file exist.. 
        if os.path.exists(local_txt):
            print('local exist .. notthing to do')
            self.logobj = self.setup_logobj(local_txt)
            return
        
        else: # no local file detected ... let do download or parse. if zip exist..
            self.ftp_zip_path = ftp_zip_path.split('/')
            self.host = self.ftp_zip_path[:1][0]
            self.ftp_filename = self.ftp_zip_path[-1:][0]

            self.path = '/'+'/'.join(self.ftp_zip_path[1:-1]) #+ '/'
            local_zip = os.path.join(self.logfolder, self.ftp_filename)    # path in Local PC
            local_r = Path(local_zip.strip('.zip'))
            local_txt = os.path.join(self.logfolder,self.txt_log)

        # check if r not exist.
        if not os.path.exists(local_r):  ## r file not exist.
            if not os.path.exists(local_zip):  # if zip not exist... re-download it.
                self.download_file_from_ftp(self.host,self.path,self.ftp_filename,local_zip)
                self.zip_extractor(local_zip,local_r)
                print(local_zip)

        #self.parse_log(local_r,local_txt)
        if dex_it.dex_file(local_r,local_txt) != None:
            self.logobj = self.setup_logobj(local_txt)
        if Remove_RAW_FILE:
            os.remove(local_zip)
            os.remove(local_r)

        else:
            print('Error parsing text File...')

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
        
        r_filename = (''.join(zip_file.split('\\')[-1:])).strip('.zip')
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extract(r_filename, os.path.join(self.logfolder).replace('/',os.sep))
    
        r_file = os.path.join(self.logfolder,r_filename).replace('/',os.sep)
        return r_file


# Main application
if __name__ == "__main__":
    
    #def __init__(self,serial,oper,ts,code,ftp_zip_path):
    serial = "ABCDE"
    oper = 'TEST'
    ts = 99
    code= 'PASS'
    #ftp_zip_path = "teppinasv001.seagate.com/prod/none/merlin/history/COMET/20/B04D062F.4905113404.r.zip"
    ftp_zip_path = "teppinasv001.seagate.com/prod/none/merlin/history/COMET/20/B04D062F.4905113404.r.zip"
    local_file="B04D062F_COMET_135_PASS.txt"
    logprocess = log_obj_creater(serial,oper,ts,code,ftp_zip_path,local_file)
    # print(type(logprocess.logobj))

    