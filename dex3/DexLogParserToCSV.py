import os, sys, getopt, glob, csv

#########################################################################################
class CP_DexLogParserToCSV():

   # ----------------------------------------------
   def __init__(self, textFileLoc=None, saveFilepath = None):

      self.fileLocation = textFileLoc
      self.save_path = saveFilepath #C:\var\merlin3\csvresults\1011-1-0   
      self.data_keys = self.gen_parser_dict()
      
      # These are used if you need to add structure into your data that isn't otherwise present.
      # For example, say you loop a test N times - this can track the measurement iteration.
      # - This could be modified to monitor an SPC_ID.. would probably be the most reasonable path.
      self.ADD_MAGIC_TRACKING_KEY     = False
      self.MAGIC_TRACKING_KEY         = 'MY_MAGIC_KEY'
      self.MAGIC_TRACKING_KEY_NUM     = 0
      self.MAGIC_TRACKING_KEY_HEADER  = 'TRACKING_HEADER'

      print('\nParsing Dex Log to CSV files...')
      self.clear_save_folder()
      self.run()
      print("--> Finished parsing - %s" %self.fileLocation)
      print("--> Stored location  - %s" %self.save_path) #may need to separate by cellindex
      
   def gen_parser_dict(self):
       #########################################################################################
       # Grab the TableDictionary.py file from /dex
       import tabledictionary as td
       data_headers = td.tableHeaders

       parser_dict  = {}
       # Translate the table dictionary into a dict. for the parser.
       # Parser needs some trigger points on each of the tables to track the data
       #  - MAGIC_NUM: Maximum number of rows to accept for each table entry.  Legacy version tracked table lengths - this is now a fail safe.
       #  - HEADER_CAPTURED:  Tracks whether the table header has been written to CSV or not.
       #  - TRIGGER: Flag stating which table is currently being parsed.  This is dynamic in the parser.
       #  - FILE_WRITTEN: Flag stating if the .CSV file has been created for the table or not.
       for key in data_headers.keys():
          parser_dict.update({
                      key:{
                         'KEY_NAME'        : data_headers[key][0],
                         'MAGIC_NUM'       : 100000,
                         'HEADER_CAPTURED' : False,
                         'TRIGGER'         : 0,
                         'FILE_WRITTEN'    : False,
                         },
                         })
       return parser_dict
   
   # ----------------------------------------------
   def clear_save_folder(self,):      
      for file in os.listdir(self.save_path):         
         if file.endswith('.csv'):            
            try:
                os.remove(os.path.join(self.save_path,file))
            except (OSError, IOError):
                pass
   
   # ----------------------------------------------
   def row_writer(self,csvfile,dataline):
      # This will save the row of data (dataline) to a csv file.
      filename = os.path.join(self.save_path, csvfile + '.csv')
      with open(filename, 'a') as f:      
        writer = csv.writer(f, dialect='excel',delimiter=',',lineterminator='\n')#, quotechar='|', quoting=csv.QUOTE_MINIMAL)
        dataline = dataline.strip()
        dataline = dataline.split()
        # For debug
        #print dataline
        #print csvfile
        writer.writerow(dataline)
   # ----------------------------------------------
   def run(self):
      """
      This is the master log reader function.
       - Function operates by reading through a logfile line by line.
       - At each line, a check is made if a table header is in line.
       - If the header is in line, a pipeline is opened to a .csv file for that table.
       - Data is routed into that file until either the log shows a line break.  (Empty row in the file).
       - Or it stops if the MAGIC_NUM is passed. ( self.data_key[key]['MAGIC_NUM'] ).
          - This is to prevent possible parsing issues.
          
      """      
      print("\n")
      print("--> Parsing %s" %self.fileLocation)
      print("\n")
      
      # File to operate on
      file_object = open(self.fileLocation, 'r')
      
      #self.output_files      = [ open( self.home+self.data_keys[key]['KEY_NAME']+".csv",'w') for key in self.data_keys.keys() ]
      self.output_files      = {}
      #print self.output_files
      for line in file_object:
         if "Drive_Temperature_Deg_C" in line:
            #for iter in range(30):
            print(line.strip())
      
         # If you're adding a data tracker, pull out the value here.
         if self.MAGIC_TRACKING_KEY in line:
            self.MAGIC_TRACKING_KEY_NUM =  line.split()[-1] 
         
         for key in self.data_keys.keys():
            
            # If a table is active, incriminate it's tracking number.  (How many rows have been added to that table)
            if self.data_keys[key]['TRIGGER'] >0:
               #print "Trigger active for: ",self.data_keys[key]['KEY_NAME']
               #print "Trigger val: ",self.data_keys[key]['TRIGGER']
               
               self.data_keys[key]['TRIGGER'] =  self.data_keys[key]['TRIGGER'] +1
      
            # If the data row is the table header... save the header to the CSV.
            if self.data_keys[key]['TRIGGER'] == 2:
               if self.data_keys[key]['HEADER_CAPTURED'] == False:
                  self.data_keys[key]['HEADER_CAPTURED'] = True
                  
                  # Adjust your header for the tracker if needed.
                  if self.ADD_MAGIC_TRACKING_KEY == True:
                     line = line +" "+ self.MAGIC_TRACKING_KEY_HEADER
            
                  #self.output_files[key].write(line)
                  self.row_writer(self.output_files[key],line)
         
            # Early exit for the table in case of a parsing issue.
            if self.data_keys[key]['TRIGGER'] > self.data_keys[key]['MAGIC_NUM']:
                  # This is probably a logical spot to add a TRIGGER reset = 0 on the following condition.
                           # if len(line.split()) == 0 
                  # This would remove the requirement for the magic numbers.
               self.data_keys[key]['TRIGGER'] = 0
               
            # If you've passed the header, save the data.
            if self.data_keys[key]['TRIGGER'] > 2:
            
               # But first check that you haven't passed the end of the table.
               if len(line.split()) == 0:
                     self.data_keys[key]['TRIGGER'] = 0
                     
               # Otherwise, ssave the data!
               if len(line.split()) != 0:
               
                  # Adjust your data for the tracker if needed.
                  if self.ADD_MAGIC_TRACKING_KEY == True:
                     line = line +" "+ self.MAGIC_TRACKING_KEY_NUM
                  self.row_writer(self.output_files[key],line)
   
            # Check for a table, and trigger opening the .csv pipeline.
            if self.data_keys[key]['KEY_NAME'] == line[:-2]:
               #print "line: ",line[:-2]
               #print "\n"
               #print "datakeys: ",self.data_keys[key]['KEY_NAME'] 
               #print "Setting Trigger for key: ",self.data_keys[key]['KEY_NAME']
               self.data_keys[key]['TRIGGER'] = 1
               
               # If this is the first time you've seen the table, create the .csv file.
               if self.data_keys[key]['FILE_WRITTEN'] == False:
                  self.output_files.update({
                                            #key: open(os.path.join(self.save_path,(self.data_keys[key]['KEY_NAME']+".csv")),'w'),
                                            key: self.data_keys[key]['KEY_NAME']
                                            })
                  self.data_keys[key]['FILE_WRITTEN'] = True
         
   # ----------------------------------------------   
#########################################################################################

if __name__ == "__main__":
  try:
    optList,argList = getopt.getopt(sys.argv[1:], 'i:d:n:c:e:f:m:thvpsbag')
  except:
    # Unrecognized option in list or not using required arg with option
    errMsg = "ERROR:  Invalid options"
    print(errMsg)
  # Set up defaults
  myOptionList = {}

  for option,args in optList:
    #PRESULTS.txt location
    if option == "-i":
      resultsFileName = args
    # Directory the results files should be put in
    elif option == "-d":
      saveFilePath = args
  
  CP_DexLogParserToCSV(resultsFileName, saveFilePath)