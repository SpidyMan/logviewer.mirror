import wx
import wx.lib.buttons as buttons
from wx.py.editor import EditWindow
# import pandas as pd
from cryptography.hazmat.primitives.kdf import pbkdf2
import encodings.idna
import re, os, sys
from sealogfile.f3logfile import F3LogFile

if __name__ == "__main__":
    log = F3LogFile('11111111_COMET_112_PASS.txt')
    with open('11111111_COMET_112_PASS.txt', 'rb') as raw_logf:
        raw_log = raw_logf.read()
    log.Process(skip_header_footer=True)
    print(log)