from .tabledictionary import tableHeaders

# Entry Format:
# <Table Index>: ('<Table Name>',
#  '<Column Names>',
#  (<Column Masks>,), '<Column Types>', (<Column Widths>,), '<Table Type>'
#

##requested = {
##   'tableName': 'P135_COMBO_TABLE3',
##   'tableCode': 2626,
##   'header': 'HD_PHYS_PSN,HD_LGC_PSN,RDR_PSN,RDR_LGC_PSN,ZONE,CTF_BOOST,CTF_FREQ,PERCENT_ZONE_FREQ,PGA_GAIN,MR_RANGE,VGA_GAIN_RANGE,TRK_INIT_GAIN_DAC,TRK_INIT_MRA_DAC,TRK_INIT_OFFSET_DAC,LC_W_SDW',
##   'mask': (0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,),
##   }

# ScriptTable template... ( tablecode:0)
# requested = {
#    'tableName': 'P982_WPM_BY_WEDGE_DATA:',
#    'tableCode': 0,
#    }
  

def get_request_from_value(val):
      request = {'tableCode':-99,
                 'tableName':'',
                 'header':'',
                 'mask':'',
                 'width':'',
                 'type':''}
      
      for key,value in tableHeaders.items():
            if val == value[0]:   # value[0] is the <Table Name> 
                  request['tableName'] = value[0]
                  request['tableCode'] = key
                  request['header'] = value[1].split(',')
                  request['mask'] = list(value[2])
                  return request
      # if the val not in tableHeaders dictionary .. maybe this is script table 
      # then return as a script table.. (tableCode : 0 , tableName : as user request )
      if val.startswith('@@@'):      # add @@@ if you want to query MatchTable
            request['tableName'] = val.strip('@@@')
            request['tableCode'] = -2
      else:
            request['tableName'] = val
            request['tableCode'] = -1
      return request

def generate_table_headerlist(output_file):
      with open(output_file,'w') as f:
            for _,value in tableHeaders.items():
                  f.write(value[0]+"\n")
                  
#print(get_request_from_value('P135_COMBO_TABLE3'))