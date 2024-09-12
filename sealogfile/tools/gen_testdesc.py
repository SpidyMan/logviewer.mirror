#!/usr/bin/env python
# coding:utf-8
# Author:  CChen 
# Purpose: a tool to generate testdesc.py from Test_number_reservation.csv
# Created: 05/18/2017

from datetime import datetime


filelist = ["Test_number_reservation.csv", ]

f = open('testdesc.py', 'w')
f.write("""#!/usr/bin/env python
# coding: utf-8
# Author:  auto generated from %s by gen_testdesc.py 
# Purpose: Descriptions of SelfTest and IOTest
# Created: %s

""" % (filelist, datetime.now()))

f.write("TestDescription = {\n")
f.write("-1 : {'TestName':r'',\n"
        "      'TestDesc': r\"\"\"No Test Description.\"\"\" },\n\n")
f.write("-2 : {'TestName':r'Drive Attributes',\n"
        "      'TestDesc': r\"\"\"Drive Attributes.\"\"\" },\n\n")

for fi in filelist:
    with open(fi, "r") as test_number_file:
        for line in test_number_file:
            line = line.split(",")
            try:
                testnum = int(line[0])
            except (IndexError, ValueError):
                continue
            testname = (line[1]).strip()
            testdesc = testname

            # 1 : {'TestName':'Start Motor', 'TestDesc': 'Start the spindle motor. ' },

            f.write("%d : {'TestName':r'%s',\n       'TestDesc': r\"\"\"%s\"\"\" },\n\n" %
                    (testnum, testname.replace('"', '').replace("'", ""), testdesc.replace('"', '').replace("'", ""))
                    )


f.write("}\n")
f.close()

from testdesc import TestDescription

for t in TestDescription:
    print((t, ':', TestDescription[t]))
