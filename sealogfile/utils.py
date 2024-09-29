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

# Helper function for decoding
def str_it(value):
    if isinstance(value, bytes):
        return value.decode('utf-8')
    else:
        return value

def split_db_table_line(line, sep=None):
    # Define the replacement function for bytes
    def repl(match):
        return match.group(0).replace(b" ", b"&nbsp;")
    
    # Ensure the line is stripped of leading/trailing whitespace (in bytes)
    line = line.strip()
    
    # Apply regex substitution, using byte literals for the pattern
    line = re.sub(b'".+?"', repl, line)  # Replace spaces within quoted substrings (byte regex)
    
    # Split the line and replace &nbsp; back with space, then decode if needed
    return [s.replace(b"&nbsp;", b" ").strip() for s in line.split(sep) if s and s.strip()]

def set_locale():
    import os
    import locale

    cur_locale = str(locale.getlocale()).lower()
    if cur_locale.find("en_") > -1 or cur_locale.find("english") > -1:
        return

    # noinspection PyBroadException
    try:
        locale.setlocale(locale.LC_ALL,
                         "english" if os.name is "nt" else "en_US.utf-8")
    except Exception:
        pass


def parse_datetime(dt_string, fmt):
    return datetime(*((datetime.strptime(str_it(dt_string), str_it(fmt))).timetuple()[:6]))


# Helper function for decoding
def str_it(value):
    if isinstance(value, bytes):
        return value.decode('utf-8')
    else:
        return value