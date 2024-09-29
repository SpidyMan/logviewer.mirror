# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2017, All rights reserved                     #
# ----------------------------------------------------------------------------------------#
"""
    sealogfile

    Utils and settings

    :copyright: (c) 2017 Seagate Technology.
    :author: Chen Chao <chao.c.chen@seagate.com>
"""

import os
import re
import tempfile
import subprocess
from datetime import datetime
import zipfile
# from lib import wxwidgets #lingdi debug

# fix strptime issue
# https://stackoverflow.com/questions/16309650/python-importerror-for-strptime-in-spyder-for-windows-7
datetime.strptime("20001122", "%Y%m%d")

F3LOG_HEADER_SIZE = 1024 * 512  # New products are with more debug info at beginning. Extended from 128
F3LOG_FOOTER_SIZE = 1024 * 1024 * 2

MAX_DBLOG_COUNT = 8192
BIG_STATE_SIZE = 32 * 1024 * 1024
BIG_STATE_FOOTER_SIZE = 1 * 1024 * 1024
BIG_SELFTEST_SIZE = 4 * 1024 * 1024


def split_db_table_line(line, sep=None):
    def repl(match):
        return match.group(0).decode('utf-8')#.replace(" ", "&nbsp;")
    line = line.strip()
    line = re.sub(rb'".+?"', repl, line)
    #return [s.replace("&nbsp;", " ").strip() for s in line.split(sep) if s and s.strip()]
    return [s.strip() for s in line.split(sep) if s and s.strip()]


def set_locale():
    import os
    import locale

    cur_locale = str(locale.getlocale()).lower()
    if cur_locale.find("en_") > -1 or cur_locale.find("english") > -1:
        return

    # noinspection PyBroadException
    try:
        locale.setlocale(locale.LC_ALL,
                         "english" if os.name == "nt" else "en_US.utf-8")
    except Exception:
        pass


def parse_datetime(dt_string, fmt):
    return datetime(*((datetime.strptime(str(dt_string), str(fmt))).timetuple()[:6]))


def parse_NRF_file(nrf_filepath, output_file, table="", lines=-1, append=False, force=True, header=True):
    DIR_PATH = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    nrf_parser = os.path.join(os.path.abspath(os.path.join(DIR_PATH, "..")), "newresult.exe")
    if not os.path.isfile(nrf_parser):
        # print("NRF parser newresult.exe not exist")
        return -1

    nrf_parser_cmd = 'call "%s" -input "%s" -output "%s" -lines=%d -table=%s -append=%d -force=%d -header=%d' % (
        nrf_parser, nrf_filepath, output_file, lines, table,
        1 if append else 0,
        1 if force else 0,
        1 if header else 0,
    )

    # print(nrf_parser_cmd)

    return subprocess.call(nrf_parser_cmd, shell=True)


def parse_NRF_text(nrf_filename, table="", lines=-1, header=True):
    tmp_file = tempfile.TemporaryFile(suffix=".txt")
    file_name = tmp_file.name
    tmp_file.close()

    parse_NRF_file(nrf_filename, file_name, table=table, lines=lines, header=header)

    tmp_file = open(file_name, "rb")
    data = tmp_file.read()
    tmp_file.close()
    try:
        os.remove(file_name)
    except:
        pass

    return data

def parse_NRF_file_by_Python(nrf_filepath, output_file):


   
    if not zipfile.is_zipfile(nrf_filepath):
        wxwidgets.MessageBox(msg="%s is not valid zip file"%nrf_filepath)
        return -1

    #to get ZipResultsFile.py
    zf = zipfile.ZipFile(nrf_filepath,mode='r')
    path = os.path.split(output_file)[0]
    member= "ZipResultsFile.ZIP"
    #unzip
    zfpypath = zf.extract(member,path)
    #unzip ZipResultsFile.ZIP to get ZipResultsFile.py
    zfpyfile = zipfile.ZipFile(zfpypath).extract("ZipResultsFile.py", os.path.join(path, "ZPFILE"))

    

    # print(nrf_parser_cmd)
    nrf_parser_cmd = 'call "%s" "%s" -i "%s" -o "%s"' % ("python", zfpyfile, nrf_filepath, output_file,)
    ret_code = subprocess.call(nrf_parser_cmd, shell=True)
    if ret_code !=0 :    
        try:
            DIR_PATH = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
            ReportMasterPATH = os.path.abspath(os.path.join(DIR_PATH, ".."))
            f = open(os.path.join(ReportMasterPATH, "pythonExePath.txt"))
            pythonExe = f.readline()
            f.close()
            nrf_parser_cmd = 'call "%s" "%s" -i "%s" -o "%s"' % (pythonExe, zfpyfile, nrf_filepath, output_file,)
            ret_code = subprocess.call(nrf_parser_cmd, shell=True)
        except:            
            wxwidgets.MessageBox(msg="Pls Add python.exe path of python27 into environmental vars \
                                 or you can create a file named pythonExePath.txt under %s and put the python.exe path into it"%ReportMasterPATH)
            return -1

    return ret_code

# Helper function for decoding
def str_it(value):
    if isinstance(value, bytes):
        return value.decode('utf-8')
    else:
        return value