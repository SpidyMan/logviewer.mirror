#-------------------------------------------------------------------------------
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001-2011 Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
#-------------------------------------------------------------------------------
# Description: Process defined error code descriptions
#   PLEASE REGISTER NEW ERROR DESCRIPTIONS WITH SCSS
#   http://amkwebscss.eng.ang.sing.seagate.com:8080/WebSCSS/index.do
#
# $File: //depot/TSE/PF3/work/branches/ESG_PF4/scripts/proc_codes.h $
# $Revision: #7 $
# $Change: 509539 $
# $DateTime: 2012/11/19 14:18:36 $
# $Author: alan.a.hewitt $
# $Header: //depot/TSE/PF3/work/branches/ESG_PF4/scripts/proc_codes.h#7 $
# Level: Common
#-------------------------------------------------------------------------------

#define EC  10090   /* Proc M.E.-Bad .prm Parameter File */
#define EC  10096   /* Wt/Rd Cal-Bad Delta Offset Margin */
#define EC  10149   /* Tester Comm Mgr-Communications Failure */
#define EC  10279   /* Drv Misc-Log Data Out of Spec */
#define EC  10326   /* Proc M.E.-Missing Drive F/W File(s) */
#define EC  10345   /* Proc M.E.-No SCN File */
#define EC  10605   /* Tester Pwr/Temp Ctrl-Chamber too hot */
#define EC  10606   /* Tester Pwr/Temp Ctrl-Chamber too cold */
#define EC  11044   /* Process ME-Script Exception */
#define EC  11176   /* Tester Misc-Missing PCBA HSA Part Number */
#define EC  11178   /* CAP file missing PCBA part/serial number */
#define EC  11179   /* Drv Misc-Capacity below requirement */
#define EC  11180   /* Drv Head - Contact Detect Inconsistent */
#define EC  11181   /* Drv PCBA-CAP WWN Not Valid for Interface */
#define EC  11186   /* Drv Head - Min Clearance Not Met */
#define EC  11187   /* Proc Oper-RIM_TYPE/Valid Oper Mismatch */
#define EC  11188   /* Proc M.E.-Incorrect Fiji Rev */
#define EC  11189   /* Proc M.E.-Unrecognized PCBA Part Number */
#define EC  11200   /* Drv F/W-Report_table_row() Error */
#define EC  11201   /* Proc M.E.-Required Attribute is Missing */
#define EC  11206   /* Drv Head-Max Clearance Exceeded*/
#define EC  11249   /* Drv Misc - VPD Attribute is Incorrect */
#define EC  11251   /* Drv Misc - Ctrl 0 is not XO */
#define EC  11252   /* Drv Misc - LUN Creation Failed */
#define EC  11253   /* Drv Misc - Unable to determine XO or NXO */
#define EC  11257   /* Write+Heat Mode OD/ID Delta Exceeded*/
#define EC  12150   /* Proc Misc - Waterfall failed */
#define EC  12168   /* Drv Misc - Auto-Waterfall Rezone */
#define EC  12169   /* Drv Misc - Auto-Waterfall Depopped */
#define EC  12179   /* Proc Functional - Diode cert temp check error */
#define EC  12383   /* Proc Misc - Kwai Prep Failed */
#define EC  12411   /* Proc Misc - Verify WWN fail */
#define EC  12412   /* Proc Misc - Verify ATA SPEED fail */
#define EC  12413   /* Proc Misc - Unable to set xfer rate */
#define EC  12513   /* Proc Misc - CIT Not Buffer Compare */
#define EC  12517   /* Proc Final - Two Temp Cert Failure */
#define EC  12518   /* Proc Misc-Two Temp Cert Diode Failure */
#define EC  12525   /* Proc CIT - Default Miscompare failure code*/
#define EC  12653   /* Random DMA read fail */
#define EC  12656   /* Sequential DMA read fail*/
#define EC  12657   /* Sequential DMA write fail */
#define EC  12664   /* Random DMA write fail */
#define EC  12674   /* Full read verify fail */
#define EC  12716   /* Cit SingleBitMis MIS1 */
#define EC  12717   /* Cit MultiBitMis MIS2 */
#define EC  12718   /* Cit 50 IOEDC MIS3 */
#define EC  12719   /* Cit Not 50 IOEDC MIS4 */
#define EC  12720   /* Cit IO Not MIS I/O1 */
#define EC  12721   /* Cit IO UNK MIS I/O2 */
#define EC  12753   /* Proc Misc - Encryption Blk Chk Fail */
#define EC  12754   /* Proc Misc - Unable to get KwaiPrep settings */
#define EC  13306   /* Proc Misc - NVC validation failed */
#define EC  13370   /* Hi-Low Seek fail */
#define EC  13371   /* Funnel Seek fail */
#define EC  13372   /* Random Seek fail */
#define EC  13373   /* Sony Screen Test fail */
#define EC  13374   /* Track to Track Seek fail */
#define EC  13381   /* Linear Verify fail */
#define EC  13382   /* MQM - Agitation CleanUp fail */
#define EC  13383   /* MQM - SWOT Test fail */
#define EC  13384   /* MQM - Encro Test fail */
#define EC  13385   /* MQM - Random Write fail */
#define EC  13386   /* MQM - Random Read fail */
#define EC  13387   /* Drive failed for UDE at ID screening */
#define EC  13401   /* Proc Misc - CPC Interface FPGA Code Dnld Failed */
#define EC  13402   /* Proc Misc - CPC Code Ver and Config Ver Mismatch */
#define EC  13403   /* dependency check error*/
#define EC  13404   /* Proc VBAR - VBAR Capability Failed */
#define EC  13405   /* Proc VBAR - VBAR Performance Failed */
#define EC  13406   /* Proc VBAR - VBAR Capacity Failed */
#define EC  13408   /* Proc VBAR - VBAR fail head count */
#define EC  13409   /* Proc VBAR - VBAR Head Saturation Failed */
#define EC  13410   /* 03 CRC error bit is set during a write command */
#define EC  13411   /* 04 Write address outside user-accessible address space */
#define EC  13412   /* 05 Write command aborted */
#define EC  13413   /* 06 Undetermined write error */
#define EC  13414   /* 07 CRC error bit set during read command */
#define EC  13415   /* 08 Uncorrectable data during read */
#define EC  13416   /* 09 Read address outside user-accessible address space */
#define EC  13417   /* 10 Read command aborted */
#define EC  13418   /* 12 Undetermined read error */
#define EC  13419   /* 11 Verification of WWN Failed*/
#define EC  13420   /* 13 generic CPC IdentifyDevice() error*/
#define EC  13421   /* 14 Set Features failed */
#define EC  13422   /* 15 Generic Read Write Error */
#define EC  13423   /* 16 Generic Get Buffer Error */
#define EC  13424   /* 17 Drive failed to power on and come ready in Interface*/
#define EC  13425   /* Drive failed current BG and cannot commit to any other BG */
#define EC  13426   /* SPT Diagnostic command failed */
#define EC  13450   /* 18 Access Time out of Spec Error */
#define EC  13452   /* 19 Command Set test Error */
#define EC  13453   /* Capacity & Model No. Screen Fail? */
#define EC  13454   /* 20 Power Mode Idle/Standby/Sleep Error*/
#define EC  13455   /* Failed Smart Verify Thresholds*/
#define EC  13456   /* Failed Smart Critical Event Log*/
#define EC  13457   /* Failed Smart DOS Reset*/
#define EC  13458   /* Failed Smart DST Short - Drive Self Test*/
#define EC  13459   /* Failed Smart DST Long - Drive Self Test*/
#define EC  13460   /* 21 DRam Screen, Miscompare screen*/
#define EC  13501   /* Carrier ID's length is not 8*/
#define EC  13502   /* Unable to select port on carrier */
#define EC  14001   /* Iface SATA - Undefined Error */
#define EC  14180   /* RAW_ERROR_DELTA out of spec */
#define EC  14183   /* CRASH_STOP_CYL out of spec */
#define EC  14184   /* RAW_ERROR_RATE out of spec */
#define EC  14185   /* HEATER_RESISTANCE out of spec */
#define EC  14186   /* DELTA_SER out of spec */
#define EC  14187   /* OTF_ERROR_RATE out of spec */
#define EC  14188   /* OTF_BER_DELTA out of spec */
#define EC  14201   /* Drv Misc - Unable to login */
#define EC  14202   /* Drv Misc - Ifconfig: IP out of range */
#define EC  14203   /* Drv Misc - Ifconfig: IP/Bcast not found */
#define EC  14204   /* Drv Misc - Ifconfig: MAC addr not found */
#define EC  14205   /* Drv Misc - Ifconfig: eth0/eth1 not found */
#define EC  14206   /* Drv Misc - Ifconfig data not found */
#define EC  14211   /* Drv Misc - Unable to stop autoboot */
#define EC  14212   /* Drv Misc - Unable to turn off battery */
#define EC  14513   /* Drv Misc - Invalid LUN Parameters */
#define EC  14514   /* Drv Misc - Set VPD Failed */
#define EC  14515   /* Drv Misc - Get VPD Failed */
#define EC  14516   /* Drv Misc - Invalid Controller Selected */
#define EC  14517   /* Drv Misc - Available LUNs Exceeded */
#define EC  14518   /* Drv Misc - XO and NXO have the same IP */
#define EC  14522   /* Drv Misc - Unable to Determine MDA Type */
#define EC  14524   /* Drv F/W - General SIM Read Failure */
#define EC  14526   /* Proc M.E. - Invalid key in dictionary */
#define EC  14527   /* Proc M.E. - Object missing attribute */
#define EC  14529   /* Drv Misc - Invalid ISE Part Number */
#define EC  14530   /* Drv Misc - Low Battery Expected Life */
#define EC  14531   /* Drv Misc - Mixed MDA Type */
#define EC  14542   /* Drv Misc - Reformat ISE Failure */
#define EC  14543   /* DRV MISC - BPI average below spec */
#define EC  14551   /* Proc M.E. - Unknown Initiator code */
#define EC  14554   /* Proc M.E. - Invalid List Index */
#define EC  14555   /* Proc M.E. - Undefined Global Name */
#define EC  14559   /* Proc M.E. - Failed Burnish Check */
#define EC  14570   /* Proc M.E. - Burnish inconsistent */
#define EC  14571   /* Proc M.E. - Burnish Retry Failed */
#define EC  14574   /* Proc M.E. - BER change, as measured by quickErrRate, exceeded limit */
#define EC  14575   /* Proc Misc - Invalid Preamp and AAB Type */
#define EC  14576   /* Proc M.E. - Burnish Check Cap Exceed Max */
#define EC  14581   /* Proc Misc - Failed to retrieve TD_SID from FIS */
#define EC  14586   /* Heat Only Mode OD/ID Delta Exceeded */
#define EC  14599   /* Wt/Rd Misc - Delta MR Resistance over limit */
#define EC  14601   /* Proc Misc - Failed to unlock serial port */
#define EC  14612   /* Poor Average QBER per head */
#define EC  14615   /* Drv F/W - Download Checksum Mismatch */
#define EC  14629   /* Self-Test Failed to Execute */
#define EC  14634   /* Failed BER full encroachment */
#define EC  14635   /* Failed BER side encroachment */
#define EC  14644   /* Proc VBAR - VBAR Generic Failed */
#define EC  14651   /* Failed for low OTF during format */
#define EC  14652   /* Failed for excessive write retries during format */
#define EC  14654   /* VBAR bad single Sector error */
#define EC  14655   /* Final VBAR squeeze test failure */
#define EC  14656   /* Absolute Squeeze SER Threshold Failure */
#define EC  14658   /* Poor QBER per zone */
#define EC  14659   /* Failed QBER screening */
#define EC  14662   /* Exceed delta VGA limit in read screen2*/
#define EC  14673   /* 1 million writes BER Prediction */
#define EC  14680   /* Clearance Screen Failure PFL1139 */
#define EC  14682   /* ST35 return servo twiddle error */
#define EC  14683   /* Drive failed for clearance contamination at the ID */
#define EC  14686   /* Drv Head - Insufficient Areal Density Capability */
#define EC  14691   /* HIRP StDev Between Zones Exceeds Limit */
#define EC  14692   /* HIRP Adjacent Zones Failed */
#define EC  14704   /* Brinks 62kHz OD Contact Mod Scrn Failure */
#define EC  14706   /* V3BAR Number Retries Exceeded */
#define EC  14709   /* Retrieval of MDW TPI from FIS and Gemini local DB Failed */
#define EC  14714   /* Exceeded delta defect count limit */
#define EC  14718   /* Failed Smart Pending Defect List*/
#define EC  14719   /* Failed Smart Grown Defect List*/
#define EC  14722   /* TCS Spec Limit Violated */
#define EC  14725   /* Proc Misc - Failed to unlock interface port */
#define EC  14726   /* Exceeded Dice Audit StdDevFitError limit */
#define EC  14727   /* Calculation Error FW and PF3 */
#define EC  14728   /* Dynamic Rim Type Mismatch with temp req  */
#define EC  14729   /* RimType not in Dynamic Rim Type list */
#define EC  14733   /* Cannot change BG on the fly. Reprocess drive at CMT2 */
#define EC  14734   /* Proc M.E. - Failed for Heater DAC value screening */
#define EC  14737   /* Proc Misc - Failed to verify the drive in WR_VERIFY */
#define EC  14746   /* Drv Misc - Failed to pass C410_Screen test */
#define EC  14760   /* Misc - LBA not divisible by number of heads  */
#define EC  14761   /* Drv Misc - Failed CSetDriveConfigAttributes */
#define EC  14798   /* Drive Thermistor value out of spec range */
#define EC  14799   /* Attempting to rerun VBAR more than once */
#define EC  14765   /* Failed Grading at CTQ0  */
#define EC  14766   /* Failed Grading at CTQ1  */
#define EC  14767   /* Failed Grading at CTQ2  */
#define EC  14768   /* Failed Grading at CTQ3  */
#define EC  14769   /* Failed Grading at CTQ4  */
#define EC  14770   /* Failed Grading at CTQ5  */
#define EC  14771   /* Failed Grading at CTQ6  */
#define EC  14772   /* Failed Grading at CTQ7  */
#define EC  14773   /* Failed Grading at CTQ8  */
#define EC  14774   /* Failed Grading at CTQ9  */
#define EC  14775   /* Failed Grading at CTQ10 */
#define EC  14776   /* Failed Grading at CTQ11 */
#define EC  14777   /* Failed Grading at CTQ12 */
#define EC  14778   /* Failed Grading at CTQ13 */
#define EC  14779   /* Failed Grading at CTQ14 */
#define EC  14780   /* Failed Grading at CTQ15 */
#define EC  14781   /* Failed Grading at CTQ16 */
#define EC  14782   /* Failed Grading at CTQ17 */
#define EC  14783   /* Failed Grading at CTQ18 */
#define EC  14784   /* Failed Grading at CTQ19 */
#define EC  14785   /* Failed Grading at CTQ20 */
#define EC  14786   /* Failed Grading at CTQ21 */
#define EC  14787   /* Failed Grading at CTQ22 */
#define EC  14788   /* Failed Grading at CTQ23 */
#define EC  14789   /* Failed Grading at CTQ24 */
#define EC  14790   /* Failed Grading at CTQ25 */
#define EC  14791   /* Failed Grading at CTQ26 */
#define EC  14792   /* Failed Grading at CTQ27 */
#define EC  14793   /* Failed Grading at CTQ28 */
#define EC  14794   /* Failed Grading at CTQ29 */
#define EC  14795   /* Failed Grading at CTQ30 */
#define EC  14796   /* Failed Grading at CTQ31 */
#define EC  14800   /* Consistency Check Exceeded Retries And Failed  */
#define EC  14801   /* Proc Misc - Fail Drive Reconfig RPM check */
#define EC  14802   /* Proc Misc - Failed to reconfigure FDE drive to STD drive.  */
#define EC  14803   /* FAILVBAR does not meet squeeze SER limit */
#define EC  14804   /* Failed TI ATE Screen */
#define EC  14805   /* Weak Write Scrn - defect found on H0 */
#define EC  14806   /* Weak Write Scrn - defect found on H1 */
#define EC  14807   /* Weak Write Scrn - defect found on H2 */
#define EC  14808   /* Weak Write Scrn - defect found on H3 */
#define EC  14809   /* Encroachment Scrn - defect found on H0 */
#define EC  14810   /* Encroachment Scrn - defect found on H1 */
#define EC  14811   /* Encroachment Scrn - defect found on H2 */
#define EC  14812   /* Encroachment Scrn - defect found on H3 */
#define EC  14813   /* Delay write fail */
#define EC  14823   /* Unsupported Request from drive */
#define EC  14824   /* Unrecognized test number */
#define EC  14826   /* Heater Cap - Bad Single Sector Error */
#define EC  14827   /* Prevent passing audit test drive from shipping */
#define EC  14828   /* Asus Idle 1 Test Failed */
#define EC  14829   /* Asus S4 Test Failed */
#define EC  14830   /* Various Idle Mode Test Failed */
#define EC  14831   /* Copy Station Test Failed */
#define EC  14832   /* SIE FITS Fitness Test Failed */
#define EC  14833   /* SIE FITS Write Read Compare Test Failed */
#define EC  14834   /* Mayhem File Copy Compare Simulation Test Failed */
#define EC  14835   /* Fitness Cache Simulation Test Failed */
#define EC  14836   /* Combo Spec Scrn - WPP and BER */
#define EC  14837   /* Reconfig Business Group is not allowed */
#define EC  14839   /* Test 135 Contact DAC less Start DAC */
#define EC  14840   /* Four Stream Test Failed */
#define EC  14842   /* Media Cache Control */
#define EC  14843   /* Fujitsu HDD Diagnostic Test Failed */
#define EC  14844	  /* TPM Returned a failing sense code in download. Check log for sense code and description.*/
#define EC  14845	  /* Fail to change drive UDR2 Unwritten Drive Recovery */
#define EC  14849   /* Apple LTOS Test Failed */
#define EC  14850   /* Delay Random Read Test Failed */
#define EC  14851   /* HP WRC Test Failed */
#define EC  14852   /* HP Integration Simulation Test Failed */
#define EC  14853   /* Apple Stone Cutter Test Failed */
#define EC  14856   /* Absolute Squeeze SER Threshold Failure */
#define EC  14857   /* NEC Performance Test Failed */
#define EC  14858   /* FDE drive not in USE or MFG Mode */
#define EC  14859   /* Unsupported customer */
#define EC  14860   /* Unsupported customer config dlfile */
#define EC  14861   /* Test 621 STE Screen Failed  */
#define EC  14872   /* min ramp cyl for all heads detected */
#define EC  14873   /* Ramp cyl odd/even head delta exceeded */
#define EC  14862   /* Proc Misc - TCG Prep Error */
#define EC  14863   /* Proc Misc - Wrong PN vs Drv Sector Size */
#define EC  14876   /* WIJIA - Head Stability Screen Fail� */
#define EC  14877   /* Test 198 Skip Write Detect */
#define EC  14881   /* Dynamic Rim Type replug count exceeded */
#define EC  14882   /* Primary CAP does not match Secondary CAP */
#define EC  14883   /* Primary RAP does not match Secondary RAP */
#define EC  14884   /* Primary SAP does not match Secondary SAP */
#define EC  14886   /* CCV - ME CCV Process Setup Error */
#define EC  14888   /* Svo Startup-02/04F0 Not Ready Super Certify in Progr */
#define EC  14889   /* Proc M.E.-05/26/00/04 Invalid Param-CheckModePage */
#define EC  14890   /* Proc M.E.-05/26/00/0B Invalid-BuildTranslateAddrPg */
#define EC  14891   /* Proc M.E.-05/26/00/81 Invalid-Input Head */
#define EC  14892   /* Proc M.E.-05/26/02/10 DIAG-Invalid command */
#define EC  14893   /* Proc M.E.-05/26/02/13 DIAG-Unsupported DIAG Cmd */
#define EC  14894   /* Proc M.E.-05/26/9A/00 SED DNLD-Invalid Param */
#define EC  14895   /* Drv Startup-06/29/01/xx Pwr On Reset */
#define EC  14896   /* Drv F/W-06/2A/01/xx Mode Params Changed */
#define EC  14897   /* Drv F/W-07/20/02/00 Access Denied SED Locked LBA */
#define EC  14898   /* Drv F/W-07/27/00/xx Wt Protect */
#define EC  14899   /* Proc M.E.-03/31/91/xx Corrupt WWN in DIF */
#define EC  14900   /* Wt/Rd Def's-04/32/00/xx No Spares Available */
#define EC  14901   /* Drv CPF-04/1C/00/xx Defect List Not Found */
#define EC  14902   /* Drv F/W-0E/1D/00/xx Data Miscompare During Verify */
#define EC  14903   /* Proc M.E.-06/3F/91/xx ETF CAP WWN Mismatch */
#define EC  14910   /* RimProxy - Data CRC Mismatch */
#define EC  14911   /* RimProxy - Got Wrong Tray */
#define EC  14912   /* RimProxy - EP2OUT not EMPTY */
#define EC  14913   /* RimProxy - xyrc No Response From Cell */
#define EC  14914   /* RimProxy - xyrc Driver Error */
#define EC  14915   /* HP Store Self Test Interrupt Failed */
#define EC  14917   /* Adjacent zone xfer rate delta exceeded */
#define EC  14919   /* Apple Write Read Compare Test Failed */
#define EC  14920   /* Acer S3 Test Failed */
#define EC  14921   /* Acer S4 Test Failed */
#define EC  14922   /* Acer S5 Test Failed */
#define EC  14926   /* Write/Read SMART (WrRdSmt) Test Failed */
#define EC  14930   /* Drv Head - Channel Opti BER Limit Exceeded */
#define EC  14931   /* HP DST Performance Test Failed */
#define EC  14933   /* GOTF Thermal Clearance Coefficient 1 Out Of Spec  */
#define EC  14934   /* GOTF Mean 3 Sigma RRO Out Of Spec  */
#define EC  14954   /* Write Read IOPS Comp Performance   */
#define EC  14956   /* Rim type to riser type mismatch  */
#define EC  14957   /* Drv Head-Stability Test Failed */
#define EC  15002   /* Delta LOAD_PEAK_CUR from T25 over limit*/
#define EC  42162   /* SSD Attrib 231 Life Left Failed Limit */
#define EC  42166   /* Capacitance Value Out of Limits */
#define EC  42167   /* ESR Value Out of Limits */
#define EC  42187   /* Burnish Chk Insufficient Data */

//F3 sense translation EC's

#define EC  39197   /* 05/2699, FRU 1D - Invalid Unlock tags in Flash Download Source Customer does not match installed firmware */
#define EC  39198   /* 05/2699, FRU 1D - Invalid Unlock tags in Flash Download Destination Customer not allowed */
#define EC  39199   /* 05/2699, FRU 1D - Invalid Unlock tags in Flash Download Checksum failed */
#define EC  39200   /* 05/2699, FRU 20 - Trying to download older firmware over newer firmware */
#define EC  39201   /* 05/2699, FRU 21 - Downloaded overlay is incompatible with curent CFW */
#define EC  39202   /* 05/2699, FRU 22 - Overlay download failure 1 */
#define EC  39203   /* 05/2699, FRU 23 - Overlay download failure 2 */
#define EC  39204   /* 05/2699, FRU 24 - Download does not support this feature or handling */
#define EC  39205   /* 05/2699, FRU 25 - General download failure */
#define EC  39206   /* 05/2699, FRU 26 - Trying to download bridge file for the incorrect product family */
#define EC  39207   /* 05/2699, FRU 27 - Factory Flags mismatch - *** CheckFWTags( ) *** */
#define EC  39208   /* 05/2699, FRU 28 - Illegal combination, Missing BootFW module. */
#define EC  39209   /* 05/2699, FRU 29 - Illegal combination, Missing Customer FW Feature Flags module. */
#define EC  39210   /* 05/2699, FRU 2A - Illegal combination, Programmable Inquiry download only not supported. */
#define EC  39211   /* 05/2699, FRU 2B - Illegal combination, Missing CustomerFW module. */
#define EC  39212   /* 05/2699, FRU 2C - Download Congen header failure. */
#define EC  39214   /* 05/2699, FRU 2E - Download Congen XML failure. */
#define EC  39215   /* 05/2699, FRU 2F - Download Congen version failure. */
#define EC  39216   /* 05/2699, FRU 30 - Download Congen XML SIM MakeLocalFile failure. */
#define EC  39217   /* 05/2699, FRU 31 - Download Congen mode data failure - could not save mode header. */
#define EC  39218   /* 05/2699, FRU 32 - Download Congen mode data failure - mode page had sent length/spec length miscompare. */
#define EC  39219   /* 05/2699, FRU 33 - Download Congen mode data failure - mode page had invalid contents. */
#define EC  39220   /* 05/2699, FRU 34 - Download Congen mode data failure - mode page tried to change contents not allowed by change mask. */
#define EC  39221   /* 05/2699, FRU 35 - Download Congen mode data failure - save all mode pages could not write to media. */
#define EC  39222   /* 05/2699, FRU 36 - Download Congen mode data failure - save partial mode pages could not write to media. */
#define EC  39223   /* 05/2699, FRU 37 - Download Congen mode data failure - mode change callbacks did not complete successfully. */
#define EC  39224   /* 05/2699, FRU 38 - Package Enforcement Failure - Package didn't contain valid SFW component */
#define EC  39225   /* 05/2699, FRU 39 - Invalid link rate in SaveProgrammablePhyMinMaxLinkRateToFlash */
#define EC  39232   /* 05/2699, FRU 40 - Illegal Cross Brand Download Attempted */
#define EC  39248   /* 05/2699, FRU 50 - Download header length invalid - *** DownloadFirmware( ) *** */
#define EC  39249   /* 05/2699, FRU 51 - Download length is not a multiple of the buffer word size - *** DownloadFirmware( ) *** */
#define EC  39250   /* 05/2699, FRU 52 - Download length and segment length mismatch - *** DownloadFirmware( ) *** */
#define EC  39329   /* 05/2699, FRU A1 - Unknow fw tag type in checkfwtag routine. */


#define EC  42163   /* ASD Performance Screen Time Out Of Spec */
#define EC	42170   /* Delta OTF Exceeds Limit */
#define EC  42182   /* Drv F/W - SED Nuke Failed */
#define EC  42183   /* Drv Head - Min Bias Voltage Not Met */
#define EC  42198   /* Drv Misc - T234 / T240 EAW Test - BER / SER Exceeded defined limit */
#define EC  42216   /* Clear Media Cache Timed-out */
#define EC  42220   /* CCV definition for tab is not defined */
#define EC  42221   /* Erase After Write degradation failure by EAW_BER_CHUNK1 */
#define EC  42231   /* Digital Flawscan SER Out Of Spec */
#define EC  48384   /* Rd/Wt-Not Enough Pts for BPI/TPI Filter */
#define EC  48401   /* Too Many TA's with Head Burnish */
#define EC  48403   /* Burnish TA Sum Amp Count Failed */
#define EC  48407   /* P Settling Summary Failed */
#define EC  48408   /* HSA BP Delta OTF Table Delta OTF Fail */
#define EC  48409   /* EAW Error Rate Fail */
#define EC  48427   /* Serial flash programming failed */
#define EC  48429   /* Drive Seal Failed */
#define EC  48431   /* Error Rate By Zone-Average Iteration Fail*/
#define EC  48436   /* Reset rim type and replug drive */
#define EC  48446   /* P150 Gain Sum Delta Table Fail*/
#define EC  48448   /* Drv Head - TCC1 OVERPOWER */
#define EC  48454   /* Proc M.E. - EAW Combo Spec Failure */
#define EC  48455   /* P315 Instability Metric Native And BTC */
#define EC  48457   /* Unverified Error Count By Head Out of Spec */
#define EC  48458   /* Combo of MAX_AMP_WIDTH & AMP7_CNT out of Spec */
#define EC  48460   /* DFS RRAW BER Out Of Spec */
#define EC  48479   /* BER failed delta BER and error rate spc */
#define EC  48480   /* Test 159 Combo Spec Failure */
