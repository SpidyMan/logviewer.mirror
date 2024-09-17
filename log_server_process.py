#log file processer...
import re,os,math
import tempfile,ftplib
import shutil
from history_frame import history_frame
from sealogfile.dexer.parse_log import parse_Text_log
import os,io,zipfile
#========== FTP Account SETUP ==============

ConsolePrint = True
directory = os.path.dirname(os.path.realpath(__file__))
logfile = 'processinglog.log'
FTP_USERNAME = 'rouser'
FTP_PASSWORD = 'rouser@357'
class log_server_process():
    def __init__(self,ftp_zip_path):
        self.ziped = ftp_zip_path
        self.directory = os.path.dirname(os.path.realpath(__file__))
        self.logfolder = os.path.join(self.directory,'LOG')
        ftp_zip_path = ftp_zip_path.split('/')
        self.host = ftp_zip_path[:1][0]
        self.filename = ftp_zip_path[-1:]
        self.path = '\\'.join(ftp_zip_path[1:-1]) + '\\'
        print(self.path)
        print(self.host)
        self.zip_file = self.download_file_from_ftp(self.host,self.path,self.filename)
        self.r_file = self.zip_extractor(self.zip_file)
        parse_Text_log(self.r_file,'TEST_OUTPUT')

    def download_file_from_ftp(self,host, path, filename):
        # SBR_raw_path is optional to seperate zip file by SBR ( not followed FTP path.)
        try:
            if isinstance(host, str): # host just a string means new host.
                print('xxxxxxxxxxxxxxxxx')
                print(host)

                with ftplib.FTP(host, FTP_USERNAME, FTP_PASSWORD) as ftp_server:
                    
                    print(path)
                    ftp_server.cwd(f"\{path}")
                    path_to_load = os.path.join(path, filename)             # path in FTP server
                    local_path = os.path.join(self.logfolder, path, filename)    # path in Local PC
                    print('xyxyxyx')
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    print('============')
                    tmp_file = tempfile.NamedTemporaryFile(delete=False) 
                    with tmp_file:
                        ftp_server.retrbinary(f'RETR {filename}', tmp_file.write)
                        tmp_local_path = tmp_file.name
                        shutil.move(tmp_local_path, local_path)
            print(local_path)
            return local_path

        except Exception as e:
            print('error downloading log file')
            return None
    
    def zip_extractor(self,zip_file):
        
        print(f'ZipFile located here:{zip_file}')
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extract(zip_file.strip('.zip'), os.path.join(self.logfolder).replace('\\',os.sep))
        r_file = os.path.join(self.logfolder,self.filename.strip('.zip')).replace('\\',os.sep)
        print(r_file)
        return r_file
    
    def parse_log(r_file,output_file):
        with open(output_file,'wb') as outputfile:
            parse_Text_log(r_file,output_file)

        return output_file


# Main application
if __name__ == "__main__":
    path_log = "teppinasv001.seagate.com/prod/none/merlin/history/COMET/20B04D062F.4905113404.r.zip"

    logprocess = log_server_process(path_log)
    print(logprocess)
    