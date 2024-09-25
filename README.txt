How it works...
Logviewer in this project there are 3 major parts.
  -> History views
  -> Text Log viewer
  -> Log Parse

why current logviewer is too slow? 
  -> History views and LogParse are webservice based. 
      -> history of each MD will be query from all. so this data maybe huge.
  -> Log Parse.. Input parameters for the web service will be SN and TS. 
      -> our MD sometime they have reset TS( transequence) so that why we have duplicate data in the log viewer.
  -> Text Log viewer (not a problem it's still very fast compare.)


Why we need to re-write ?
- Logviewer able to do many things they can parse the st parameters, plot the data , download CMS config and else.  this is very complex task to re-edit the code.
- Logviewer writen based on python2.x which obsolated so we need something new.
- switching from web based history query to the direct sql query is much simple.

How did i do ?
Seperated the project into 3 portion.
1.History query. 
   -> SQL query (which done in previous project just add new query command to query history)
   *** need user name and password.
2.LogParser .. ( Thanks P'Mol for the modules)
3.LogViewer .. there are a module in current version of logviewer that we can use as a reference.   
                anyway the original code is very complex so most of the feature will not work in new version.
   --> one thing that logviewer look great is the text highlighting and tree structure. then i just modify the code from python2 to python3 and modify some structure to support the new one.
