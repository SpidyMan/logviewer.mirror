
import sealogfile as sealog
from sealogfile.utils import parse_NRF_file, split_db_table_line, parse_NRF_file_by_Python

def getpartoffile(file, startPOS, endPOS):
    # Ensure startPOS and endPOS are valid integers
    if not (isinstance(startPOS, int) and isinstance(endPOS, int)):
        raise ValueError("startPOS and endPOS must be integers")
    # Ensure the positions are valid
    if startPOS < 0 or endPOS < 0 or startPOS > endPOS:
        raise ValueError("Invalid startPOS or endPOS values")
    # Move to the start position
    file.seek(startPOS)
    # Read the specified range
    part = file.read(endPOS - startPOS)
    return part

log = sealog.F3LogFile("B04N3613_COMET_307_PASS.txt")
log.Process(skip_header_footer=True)

for state in log.TestStateList:
    print(state.StateName)
    for db in state.DBLogList:
        print(f'DB::--{db}')
    for st in state.STList:
        print(f'ST::{st}')
   
# print(f'{log.SerialNo},{log.Product},{log.TS},{log.Oper},{log.ErrorCode}')
# # with open('B04N3613_COMET_307_PASS.txt','rb') as file:
# event_date = log.TestStateList[-1].EndTime.strftime("%Y-%m-%d %H:%M:%S")
# birth_date = log.DriveInfo.get('BIRTH_DATE') or "None"
#         # now we got the state .... let go to get info from inside the state...
# data_log = ["None", log.Product, log.SerialNo, log.TS, log.Oper, log.SBR,
#                         log.PartNum, birth_date, event_date, "None", "None",
#                         "None", "None", "None", log.Config, log.ErrorCode,  "None"]
# print(data_log)

# # log.PrintLogInfo()