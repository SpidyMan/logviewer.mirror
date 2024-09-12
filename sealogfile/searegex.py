# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2017, All rights reserved                     #
# ----------------------------------------------------------------------------------------#
"""
    sealogfile

    Regex defines

    :copyright: (c) 2017 Seagate Technology.
    :author: Chen Chao <chao.c.chen@seagate.com>
"""

import re


#####################
# Pattern strings
#####################
FormatDatetime = rb"%b %d %Y-%H:%M:%S"

RePatternDate = rb'(?P<date>\S{3} \d{2} \d{4}-\d{2}:\d{2}:\d{2})'

RePatternDateDetails = rb'(?P<datedetails>(?P<month>\S{3}) (?P<day>\d+) (?P<year>\d{4})' \
                     rb'-(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2}))'

RePatternStateBegin = rb'(?P<starttime>\S{3} \d{2} \d{4}-\d{2}:\d{2}:\d{2} )?' \
                    rb'(([- ]+(?P<statename>[\S_]+) : BEGIN[- ]+\r?\n.+?)' \
                    rb'|(\*+  RUNNING (?P<statename2>FAIL FUNCTION)  \*+))'

RePatternState = (
  rb'(?P<starttime>\S{3} \d{2} \d{4}-\d{2}:\d{2}:\d{2} )?' +
  rb'[- ]+(?P<statename>[\S_]+) : BEGIN[- ]+\r?\n.+?' +
  rb'\r?\n(?P<endtime>\S{3} \d{2} \d{4}-\d{2}:\d{2}:\d{2} )?' +
  rb'(' +      # end indicators
  rb'[- ]+(?P=statename) : COMPLETE[- ]+\r?\n|' +
  rb'State Sequence|' +
  rb'(?P<except>General Exception Dump)|' +
  rb'\*\*\*\*\* FAULT DETECTED \*\*\*\*\*|' +
  rb'[ *]+FAIL FUNCTION ABORTED[ *]+|' +
  rb'[ *<]+SCRIPT FAULT DETECTED|' +
  rb'[^\r\n]*END FAIL FUNCTION|' +
  rb'[^\r\n]*TEST FAULT DETECTED|' +
  rb'(?=[- ]+[\S_]+ : BEGIN[- ]+)' +
  rb')'
)

RePatternSTStart = rb'( Execution Parameter:(?P<exec_param>[^\r\n]+?)){0,1}' \
                 rb'(\r|\n)+[^\r\n]+?-----(>|&gt;)  S T A R T I N G.+?'

RePatternSTEnd = rb'((?P<except> E X C E P T I O N   testNo: (?P<stnum2>\d+)  testTime: (?P<time2>\S+))|' \
               rb'(?P<finish>  F I N I S H E D [^\r\n]+?' \
               rb'\((?P<stnum>\d+)\), Test Stat: (?P<stat>\d+), Test Time: (?P<time>\S+)  (<|&lt;)-----))'

RePatternSuppressTest = rb'Suppress test (?P<stnum>\d+): (?P<exec_param>[^\r\n]+?)' \
                        rb'.+?TestCompleted=(?P<stnum2>\d+),(?P<time>\S+)'

RePatternSTParam = rb'Parameters( |)==(>|&gt;)(  | )(?P<param>\(.+?\}\))(\r|)\n'
RePatternSPCID = rb"\*\*SPC_ID32=(?P<spc>\S+)\s\sCMT=(?P<cmt>.+?)(\r|)\n"

RePatternDBLog = rb'(?P<dblogname>((P([\dX]+){0,1}_[\S_]*?)|(TEST_TIME_BY_TEST(_XXXX)?|TEST_TIME_BY_STATE)))' \
                 rb'(?P<tablecode>\s\d+){0,1}\:\s*\r?\n' \
                 rb'(?P<dblogdesp>[\S ]+?)\r?\n(?P<dblogdata>.*?)' \
                 rb'(?=(\n\s*\n|P([\dX]+){0,1}_[\S_]*?\:|\n\S|\S{3} \d{2} \d{4}-\d{2}:\d{2}:\d{2}))'

RePatternSTWinFOF = rb'Test (?P<stnum2>\d+)  \(Start Time : (?P<time2>[\s\S]+?)\).+?' + \
                  rb'((?P<except>FOFResultsProcessingFailure)|' + \
                  rb'(\*\*\*\*\* Test: (?P<stnum>\d+);  ErrorCode: (?P<stat>\d+);  ' \
                  rb'TestTime: (?P<time>\S+) \*\*\*\*\*))'

RePatternConfigInfo = rb'((attributes at (?P<oper>\S+) start\r?\n)' \
                    rb'|(Testing from OPERATION: (?P<oper2>\S+),)' \
                    rb'|(HDA TEST Config Info  [*=]+))' \
                    rb'.*?CM Rev\s*: (.+?)\r?\n.*?Host Rev\s*: (.+?)\r?\n' \
                    rb'.*?EQP_ID\s*: (.+?)\r?\n.*?SLT\s*: ' \
                    rb'(\S+?)\r?\n.*?Product\s+: (?P<prod>.+?)\r?\n' \
                    rb'.*?Config\s+: (?P<config>.+?)\r?\n' \
                    rb'.*?SCN\s+: (?P<scn>.+?)\r?\n' \
                    rb'.*?Serial No\s*: (?P<sn>\S+?)\r?\n' \
                    rb'.*?SBR\s*: (?P<sbr>\S*?)\r?\n'

RePatternErrorCode = rb'\| ErrCode   ErrMsg.+?\n.+? (?P<ec>\d+)     (?P<ecmsg>.+?)\|\r{0,1}\n'

RePatternErrorCode2 = rb'Error Code:\s+(?P<ec>\d+)\s+\-\s+(?P<ecmsg>.+?)\r{0,1}\n'

RePatternDriveAttrsBlock = rb'DRIVE ATTRIBUTES:(?P<attrsblock>.+?)' + RePatternDate + rb' {1,2}Running'

RePatternDriveAttr = rb'(?P<name>\S+?):\s(?P<value>.*?)\n'

RePatternF3Diag = rb'F3 [0-9A-Z\n]>'

RePatternF3DiagResult = r"(Result from (?P<cmd>[\S\s]+?) cmd:\n(?P<result>[\S\s]+?)F3 [0-9A-Z\n]>)" \
                        r"|(F3 [0-9A-Z\n]>)"

#####################
# Complied regex
#####################
RegexDateDetails = re.compile(RePatternDateDetails, re.DOTALL)
RegexStateBegin = re.compile(RePatternStateBegin, re.DOTALL)
RegexState = re.compile(RePatternState, re.DOTALL)
RegexDBLog = re.compile(RePatternDBLog, re.DOTALL)
RegexST = re.compile(RePatternSTStart + RePatternSTEnd, re.DOTALL | re.IGNORECASE)
RegexST_WinFOF = re.compile(RePatternSTWinFOF, re.DOTALL)
RegexSuppressTest = re.compile(RePatternSuppressTest, re.DOTALL)
RegexSTParam = re.compile(RePatternSTParam, re.DOTALL)
RegexConfigInfo = re.compile(RePatternConfigInfo, re.DOTALL)
RegexConfigInfo2 = re.compile(RePatternConfigInfo.replace(rb'\r\n', rb'\n'), re.DOTALL)
RegexErrorCode = re.compile(RePatternErrorCode, re.DOTALL)
RegexErrorCode2 = re.compile(RePatternErrorCode2, re.DOTALL)
RegexDriveAttrsBlock = re.compile(RePatternDriveAttrsBlock, re.DOTALL)
RegexDriveAttr = re.compile(RePatternDriveAttr, re.DOTALL)
RegexF3Diag = re.compile(RePatternF3Diag, re.DOTALL)
RegexF3DiagResult = re.compile(RePatternF3DiagResult, re.DOTALL)

RePatternNamedDBLog = rb'(?P<dblogname>%s)(?P<tablecode>\s\d+){0,1}\:\s*\r?\n(?P<dblogdesp>[\S ]+?)\r?\n(?P<dblogdata>.*?)' \
                    rb'(?=(\n\s*\n\S|P([\dX]+){0,1}_[\S_]*?\:|\n\S|\S{3} \d{2} \d{4}-\d{2}:\d{2}:\d{2}))'

RePatternNamedST = rb'-----(>|&gt;)  S T A R T I N G   st\(%(st)s\).+?' \
                 rb'((?P<except> E X C E P T I O N   ' \
                 rb'testNo: (?P<stnum2>%(st)s)  testTime: (?P<time2>\S+))|' \
                 rb'(?P<finish>  F I N I S H E D [^\r\n]+?' \
                 rb'\((?P<stnum>%(st)s)\), Test Stat: (?P<stat>\d+), ' \
                 rb'Test Time: (?P<time>\S+)  (<|&lt;)-----))'

RePatternNamedSTWinFOF = rb'Test (?P<stnum2>%(st)s)  \(Start Time : (?P<time2>[\s\S]+?)\).+?' \
                       rb'((?P<except>FOFResultsProcessingFailure)|' \
                       rb'(\*\*\*\*\* Test: (?P<stnum>%(st)s);  ErrorCode: (?P<stat>\d+);  ' \
                       rb'TestTime: (?P<time>\S+) \*\*\*\*\*))'
