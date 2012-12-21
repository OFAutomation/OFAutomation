#!/usr/bin/env python
'''
Created on 22-Oct-2012
    
@author: Anil Kumar (anilkumar.s@paxterrasolutions.com)

ofautomation is the main module.

'''
import sys
import os
import re
import __builtin__

global path, drivers_path, core_path, tests_path,logs_path

path = re.sub("(core|bin)$", "", os.getcwd())
drivers_path = path+"/drivers/"
core_path = path+"/core"
tests_path = path+"/tests/"
logs_path = path+"/logs/"
sys.path.append(path)
sys.path.append( drivers_path)
sys.path.append(core_path )
sys.path.append(tests_path)

from core.utilities import Utilities
from drivers.component import Component
import logging 
import datetime
from optparse import OptionParser
component_handle = Component()
class OFAutomation:
    '''
    
    OFAutomation will initiate the specified test. 
    The main tasks are : 
    * Initiate the required Component handles for the test. 
    * Create Log file  Handles.
    
    '''
    def __init__(self):
        '''
           Initialise the component handles specified in the topology file of the specified test.
          
        '''
        # Initialization of the variables.
        __builtin__.main = self
        __builtin__.path = path
        __builtin__.utilities = Utilities()
        self.TRUE = 1
        self.FALSE = 0
        self.ERROR = -1
        self.FAIL = False
        self.PASS = True
        self.CASERESULT = self.TRUE
        self.init_result = self.TRUE
        self.testResult = "Summary"
        self.stepName =""
        self.EXPERIMENTAL_MODE = False   
        self.test_target = None
        
        # Parsing of commandline options.
        optionParser = parseOptions()
        (options, args) = optionParser.parse_args()
        
        # Verifying the commandline options.
        verifyOptions(options)

        self.logger = Logger()
        self.componentDictionary = {}
        self.componentDictionary = self.topology ['COMPONENT']
        self.driversList=[]
        for component in self.componentDictionary :
            self.driversList.append(self.componentDictionary[component]['type'])
            
        self.driversList = list(set(self.driversList)) # Removing duplicates.
        # Checking the test_target option set for the component or not
        for component in self.componentDictionary.keys():
            if 'test_target' in self.componentDictionary[component].keys():
                self.test_target = component
                 
        self.logger.initlog(self)

        # Creating Drivers Handles
        initString = "\n************************************\n CASE INIT \n*************************************\n"
        self.log.exact(initString)
        self.driverObject = {}
        for component in self.componentDictionary.keys():
            self.componentInit(component)
            
    def componentInit(self,component):
        '''
        This method will initialize specified component
        '''
        global driver_options
        self.log.info("Ceating component Handle: "+component)
        #### R
         
        if 'COMPONENTS' in self.componentDictionary[component].keys():
            driver_options =self.componentDictionary[component]['COMPONENTS']
        else:
            driver_options = {}
        #driver_options = self.componentDictionary[component]['OPTIONS']
        driverName = self.componentDictionary[component]['type']
            
        classPath = self.getDriverPath(driverName.lower())
        try :
            driverModule = __import__(classPath, globals(), locals(), [driverName.lower()], -1)
            driverClass = getattr(driverModule, driverName)
            driverObject = driverClass()
            try :
                driverObject.connect(self.componentDictionary[component]['user'],self.componentDictionary[component]['host'],self.componentDictionary[component]['password'],driver_options)
                vars(self)[component] = driverObject
            except:
                self.log.error("Failed to create comonent handle for "+component)
        except(AttributeError):
            self.log.error("There is no "+driverName+" component driver")
            self.init_result = self.FAIL
                        
                        
    
    def run(self):
        '''
           The Execution of the test script's cases listed in the Test params file will be done here. 
           And Update each test case result. 
           This method will return TRUE if it executed all the test cases successfully, 
           else will retun FALSE
        '''
        self.testCaseResult = {}
        self.TOTAL_TC_RUN = 0
        self.TOTAL_TC_NORESULT = 0
        self.TOTAL_TC_FAIL = 0
        self.TOTAL_TC_PASS = 0
        self.stepCount = 0
        self.CASERESULT = self.TRUE
        result = self.TRUE
        for self.CurrentTestCaseNumber in self.testcases_list:
            result = self.runCase(self.CurrentTestCaseNumber)
        return result
    
    def runCase(self,testCaseNumber):
        self.CurrentTestCaseNumber = testCaseNumber
        result = self.TRUE
        self.stepCount = 1
        self.EXPERIMENTAL_MODE = self.FALSE
        self.addCaseHeader()
                
        try :
            methodToCall = getattr(self.testObject, "CASE"+str(self.CurrentTestCaseNumber))
            methodToCall(self)
            self.testCaseResult[str(self.CurrentTestCaseNumber)] = self.CASERESULT
            self.logger.updateCaseResults(self)
        except(AttributeError):
            self.log.error("CASE "+ str(self.CurrentTestCaseNumber) +" not defined in test script")
            result = self.FALSE
        return result
    
    def addCaseHeader(self):
        caseHeader = "\n*****************************\n Result summary for Testcase"+str(self.CurrentTestCaseNumber)+"\n*****************************\n"
        self.log.exact(caseHeader) 
        caseHeader = "\n*************************************************\nStart of Test Case"+str(self.CurrentTestCaseNumber)+" : " 
        for driver in self.driversList:
            vars(self)[driver].write(caseHeader)
    
    def addCaseFooter(self):
        if self.stepCount-1 > 0 :
            previousStep = " "+str(self.CurrentTestCaseNumber)+"."+str(self.stepCount-1)+": "+ str(self.stepName) + ""
            stepHeader = "\n-------------------------------------------------\nEnd of Step "+previousStep+"\n-------------------------------------------------\n"
            
        caseFooter = "\n*************************************************\nEnd of Test case "+str(self.CurrentTestCaseNumber)+"\n*************************************************\n"
            
        for driver in self.driversList:
            vars(self)[driver].write(stepHeader+"\n"+caseFooter)

    def cleanup(self):
        '''
           Release all the component handles and the close opened file handles.
           This will return TRUE if all the component handles and log handles closed properly,
           else return FALSE

        '''
        result = self.TRUE
        self.logger.testSummary(self)
        
        try :
            self.reportFile.close()
            # Closing all the driver's session files
            for driver in self.driversList:
                vars(self)[driver].close()
        except:
            print " There is an issue with the closing log files"
        
        utilities.send_mail()
        try :
            for component in self.componentDictionary.keys():
                tempObject  = vars(self)[component]    
                tempObject.disconnect(tempObject.handle)
                tempObject.execute(cmd="exit",prompt="(.*)",timeout=120) 

        except(Exception):
            #print " There is an error with closing hanldes"
            result = self.FALSE
                    
        return result
        
    
    def getDriverPath(self,driverName):
        '''
           Based on the component 'type' specified in the params , this method will find the absolute path ,
           by recursively searching the name of the component.
        '''
        import commands
        #if main.test_target &&  :
        #   if 
            
        cmd = "find "+drivers_path+" -name "+driverName+".py"
        result = commands.getoutput(cmd)
        
        result_array = str(result).split('\n')
        result_count = 0
        for drivers_list in result_array:
            #print drivers_list
            result_count = result_count+1
        if result_count > 1 :
            #if main.test_target :
            print "found "+driverName+" "+ str(result_count) + "  times"+str(result_array)
            sys.exit()
            
        result = re.sub("(.*)drivers","",result)
        result = re.sub("\.py","",result)
        result = re.sub("\.pyc","",result)
        result = re.sub("\/",".",result)
        result = "drivers"+result
        return result
    

    def step(self,stepDesc):
        '''
           The step information of the test-case will append to the logs.
        '''
        previousStep = " "+str(self.CurrentTestCaseNumber)+"."+str(self.stepCount-1)+": "+ str(self.stepName) + ""
        self.stepName = stepDesc
        stepName = " "+str(self.CurrentTestCaseNumber)+"."+str(self.stepCount)+": "+ str(stepDesc) + ""
        self.log.step(stepName)
        stepHeader = ""
        if self.stepCount > 1 :
            stepHeader = "\n-------------------------------------------------\nEnd of Step "+previousStep+"\n-------------------------------------------------\n"
        
        stepHeader += "\n-------------------------------------------------\nStart of Step"+stepName+"\n-------------------------------------------------\n" 
        for driver in self.driversList:
            vars(self)[driver].write(stepHeader)
            
        self.stepCount = self.stepCount+ 1
       
    def case(self,testCaseName):
        '''
           Test's each test-case information will append to the logs.
        '''
        self.CurrentTestCase = testCaseName 
        testCaseName = " " + str(testCaseName) + ""
        self.log.case(testCaseName)
        caseHeader = testCaseName+"\n*************************************************\n" 
        for driver in self.driversList:
            vars(self)[driver].write(caseHeader)
        
    def testDesc(self,description):
        '''
           Test description will append to the logs.
        '''
        description = "Test Description : " + str (description) + ""
        self.log.info(description)
        
    def _getTest(self):
        '''
           This method will parse the test script to find required test information.
        '''
        testFile = self.tests_path + "/"+self.TEST + "/"+self.TEST + ".py"
        testFileHandler = open(testFile, 'r')
        testFileList = testFileHandler.readlines()
        #self.TOTAL_TC_PLANNED = 0
        counter = 0
        for index in range(len(testFileList)):
            lineMatch = re.match('\s+def CASE(\d+)(.*):',testFileList[index],0)
            if lineMatch:
                counter  = counter + 1
                self.TOTAL_TC_PLANNED = counter

def parseOptions():
    '''
    This will parse the commandline options and retirn the optionParser object.
    '''
    optionParser = OptionParser()
    optionParser.add_option("-t", "--test", dest="testname",
                 help="test for execution", metavar="")
    optionParser.add_option("-d", "--testdir", dest="testdir",
                 help="Tests Directory", metavar="Directory")
    optionParser.add_option("-l", "--logdir", dest="logdir",
                 help="Logs Directory", metavar="Directoy")
    optionParser.add_option("-e", "--example", dest="example",
                 help="Example Tests Execution", metavar="Option to execute Examples")
    optionParser.add_option("-c", "--testcases", dest="testcases",
                 help="Test Cases for execution", metavar="Test Cases for execution")
    optionParser.add_option("-m", "--mail", dest="mail",
                 help="mailing list, seperated by comma", metavar="mailing list, seperated by comma")
    
    return optionParser


def verifyOptions(options):
    '''
    This will verify the command line options and set to default values, if any option not given in command line.
    '''
    verifyTest(options)
    verifyTestScript()
    verifyParams()
    verifyLogdir(options)
    verifyMail(options)
    verifyTestCases(options)
    

    
def verifyTest(options):
    if options.testname:
        main.TEST = options.testname
        main.classPath = "tests."+main.TEST+"."+main.TEST
        main.tests_path = tests_path
    elif options.example :
        main.TEST = options.example
        main.tests_path = path+"/examples/"
        classPath = "examples."+main.TEST+"."+main.TEST
    else :
        print "Test or Example not specified please specify the --test <test name > or --example <example name>"
        sys.exit(0)
        
def verifyLogdir(options):
    #Verifying Log directory option      
    if options.logdir:
        main.logdir = options.logdir
    else :
        main.logdir = main.FALSE  
        
def verifyMail(options):
    # Checking the mailing list 
    if options.mail:
        main.mail = options.mail
    elif main.params['mail']:
        main.mail = main.params['mail']
    else :
        main.mail = 'paxweb@paxterrasolutions.com'

def verifyTestCases(options):
    #Getting Test cases list 
    if options.testcases:
        testcases_list = re.sub("(\[|\])", "", options.testcases)
        main.testcases_list = eval(testcases_list+",")
    else :
        main.params['testcases'] = re.sub("(\[|\])", "", main.params['testcases'])
        main.testcases_list = eval(main.params['testcases']+",") 
        
def verifyTestScript():          
    try :
        testModule = __import__(main.classPath, globals(), locals(), [main.TEST], -1)
    except(ImportError):
        print "There is no test like "+main.TEST
        sys.exit(0)       
    try :
        testClass = getattr(testModule, main.TEST)
    except(AttributeError):
        print main.TEST+ " module object has no attribute :"+main.TEST
        sys.exit(0)
    main.testObject = testClass()
    testHandler = TestHandler()
    main.params = testHandler.parseParams(main.classPath)
    main.topology = testHandler.parseTopology(main.classPath)

def verifyParams():
    try :
        main.params = main.params['PARAMS']
    except(KeyError):
        print "Error with the params file: Either the file not specified or the format is not correct"
        sys.exit(0)            
    
    try :
        main.topology = main.topology['TOPOLOGY']
    except(KeyError):
        print "Error with the Topology file: Either the file not specified or the format is not correct"
        sys.exit(0)            


class TestHandler:
    '''
       Manages authoring, parsing and execution of the test. Sub components are
       Test-Topology parser
           Module that parses the test from plain English and topology
           from a specification file and prepares for execution.
       Test sequencer 
           Module that executes the tests case by case,
           step by step adding ability for step by step pause and debug later.
       Object loader
           Module that connects and loads all the component connection objects 
           for access in the test 
    '''
    def parseParams(self,paramsPath):
        '''
        It will take the params file path and will return the params dictionary
        '''
        paramsPath = re.sub("\.","/",paramsPath)
        paramsPath = re.sub("tests|examples","",paramsPath)
        #print main.tests_path+"/"+paramsPath+".params"
        params = utilities.parse(main.tests_path+"/"+paramsPath+".params")
        paramsAsString = str(params)
        return eval(paramsAsString) 
    
    def parseTopology(self,topologyPath):
        '''
        It will take topology file path and will return topology dictionary
        '''
        topologyPath = re.sub("\.","/",topologyPath)
        topologyPath = re.sub("tests|examples","",topologyPath)
        topology = utilities.parse(main.tests_path+"/"+topologyPath+".topo")
        topoAsString = str(topology)
        return eval(topoAsString) 
        

class Logger:
    '''
        Add continuous logs and reports of the test.
        
        @author: Raghav Kashyap(raghavkashyap@paxterrasolutions.com)
    '''
    def _printHeader(self,main) :
        '''
            Log's header will be append to the Log file
        '''
        logmsg = "                               +--------------+\n" +"----------------------------- { Script And Files }  ---------------------------------\n" +"                               +--------------+\n";
        logmsg = logmsg + "\n\tScript Log File : " + main.LogFileName + ""
        logmsg = logmsg + "\n\Report Log File : " + main.ReportFileName + ""
        logmsg = logmsg + "\n\tTest Script :" + path + "Tests/" + main.TEST + ".py"+ ""
        logmsg = logmsg + "\n\tTest Params : " + path + "Tests/" + main.TEST + ".params" + ""
        logmsg = logmsg + "\n\tTopology : " + path + "Tests/" +main.TEST + ".tpl" + ""
        logmsg = logmsg + "\n                             +----------------------+\n" +"----------------------------- { Script Exec Params }  -------------------------\n" +"                             +----------------------+\n";
        values = "\n\t" + str(main.params)
        values = re.sub(",", "\n\t", values)
        values = re.sub("{", "\n\t", values)
        values = re.sub("}", "\n\t", values)
        logmsg = logmsg + values
        
        logmsg = logmsg + "\n\n                             +-----------------+\n" +"----------------------------- { Components Used }  ---------------------------------\n" +"                             +-----------------+\n"
        component_list = []
        component_list.append(None)
        
        # Listing the components in the order of test_target component should be first.
        for key in main.componentDictionary.keys():
            if main.test_target == key :
                component_list[0] = key+"-Test Target"
            else :
                component_list.append(key)
                        
        for index in range(len(component_list)) :
            if index==0:
                if component_list[index]:
                    logmsg+="\t"+component_list[index]+"\n"
            elif index > 0 :
                logmsg+="\t"+str(component_list[index])+"\n"
                
            
            
        logmsg = logmsg + "\n\n                             +--------------+\n" +"----------------------------- { Topology }  ---------------------------------\n" +"                             +--------------+\n"
        values = "\n\t" + str(main.topology['COMPONENT'])
        values = re.sub(",", "\n\t", values)
        values = re.sub("{", "\n\t", values)
        values = re.sub("}", "\n\t", values)
        logmsg = logmsg + values
        
        logmsg = logmsg + "\n------------------------------------------------------------------------------------------------------------------\n"
        
        # enter into log file all headers
        logfile = open(main.LogFileName,"w+")
        logfile.write (logmsg)
        print logmsg
        main.logHeader = logmsg
        # Adding Header for session logs
        #for driver in main.driversList:
        #    vars(main)[driver].write(logmsg)
        component_handle._updateComponentHeaders()
        #self.log.report(logmsg);
        logfile.close()
        
        #enter into report file all headers
        main.reportFile = open(main.ReportFileName,"w+")
        main.reportFile.write(logmsg)
        #reportFile.close()
        
    def initlog(self,main):
        '''
            Initialise all the log handles.
        '''
        main._getTest()
        main.STARTTIME = datetime.datetime.now() 

        currentTime = re.sub("-|\s|:|\.", "_", str(main.STARTTIME.strftime("%d %b %Y %H:%M:%S")))
        if main.logdir:
            main.logdir = main.logdir+"/" + main.TEST + "_" + currentTime
        else:
            main.logdir = logs_path + "/" + main.TEST + "_" + currentTime
            
        os.mkdir(main.logdir)
           
        main.LogFileName = main.logdir + "/" + main.TEST + "_" +str(currentTime) + ".log"
        main.ReportFileName = main.logdir + "/" + main.TEST + "_" + str(currentTime) + ".rpt"
        
        for component in main.driversList:
            vars(main)[component] = main.logdir+"/"+component+".session"
            vars(main)[component] = open(vars(main)[component],"w+")
        
        #### Add log-level - Report
        logging.addLevelName(9, "REPORT")
        logging.addLevelName(7, "EXACT")
        logging.addLevelName(10, "CASE")
        logging.addLevelName(11, "STEP")
        main.log = logging.getLogger(main.TEST)
        def report (msg):
            '''
                Will append the report message to the logs.
            '''
            main.log._log(9,msg,"OpenFlowAutoMattion","OFAutoMation")
            currentTime = datetime.datetime.now()
            currentTime = currentTime.strftime("%d %b %Y %H:%M:%S")
            newmsg = "\n[REPORT] " +"["+ str(currentTime)+"] "+msg
            print newmsg
            main.reportFile.write(newmsg)
            
        main.log.report = report 
        
        def exact (exmsg):
            '''
               Will append the raw formatted message to the logs
            '''
            main.log._log(7,exmsg,"OpenFlowAutoMattion","OFAutoMation")
            main.reportFile.write(exmsg)
            logfile = open(main.LogFileName,"a")
            logfile.write("\n"+ str(exmsg) +"\n")
            logfile.close()
            print exmsg
            
        main.log.exact = exact 
       
        
        def case(msg):
            '''
               Format of the case type log defined here.
            '''
            main.log._log(9,msg,"OpenFlowAutoMattion","OFAutoMation")
            currentTime = datetime.datetime.now()
            newmsg = "["+str(currentTime)+"] " + "["+main.TEST+"] " + "[CASE] " +msg
            logfile = open(main.LogFileName,"a")
            logfile.write("\n"+ str(newmsg) +"\n")
            logfile.close()
            #print newmsg
                        
        main.log.case = case 
        
        def step (msg):
            '''
                Format of the step type log defined here.
            '''
            main.log._log(9,msg,"OpenFlowAutoMattion","OFAutoMation")
            currentTime = datetime.datetime.now()
            newmsg = "["+str(currentTime)+"] " + "["+main.TEST+"] " + "[STEP] " +msg
            logfile = open(main.LogFileName,"a")
            logfile.write("\n"+ str(newmsg) +"\n")
            logfile.close()
            #print newmsg
                        
        main.log.step = step 
        
        main.LogFileHandler = logging.FileHandler(main.LogFileName)
        self._printHeader(main)

        ### initializing logging module and settig log level
        main.log.setLevel(logging.INFO)
        main.LogFileHandler.setLevel(logging.INFO)
       
        # create console handler with a higher log level
        main.ConsoleHandler = logging.StreamHandler()
        main.ConsoleHandler.setLevel(logging.INFO)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        main.ConsoleHandler.setFormatter(formatter)
        main.LogFileHandler.setFormatter(formatter)

        # add the handlers to logger
        main.log.addHandler(main.ConsoleHandler)
        main.log.addHandler(main.LogFileHandler)
        
    def testSummary(self,main):
        '''
            testSummary will take care about the Summary of test.
        '''

        main.ENDTIME = datetime.datetime.now()
        main.EXECTIME = main.ENDTIME - main.STARTTIME
        if (main.TOTAL_TC_PASS == 0):
            main.TOTAL_TC_SUCCESS = 0
        else:
            main.TOTAL_TC_SUCCESS = str((main.TOTAL_TC_PASS*100)/main.TOTAL_TC_RUN)
            
        if (main.TOTAL_TC_RUN == 0) :
            main.TOTAL_TC_EXECPERCENT = 0
        else :
            main.TOTAL_TC_EXECPERCENT = str((main.TOTAL_TC_RUN*100)/main.TOTAL_TC_PLANNED)
        
        testResult = "\n\n ******************************\n" + "\tTest Execution Summary\n" + "\n ******************************\n"
        testResult =  testResult + "\n Test Start           : " + str(main.STARTTIME.strftime("%d %b %Y %H:%M:%S"))
        testResult =  testResult + "\n Test End             : " + str(main.ENDTIME.strftime("%d %b %Y %H:%M:%S"))
        testResult =  testResult + "\n Execution Time       : " + str(main.EXECTIME)
        testResult =  testResult + "\n Total tests planned  : " + str(main.TOTAL_TC_PLANNED)
        testResult =  testResult + "\n Total tests RUN      : " + str(main.TOTAL_TC_RUN)
        testResult =  testResult + "\n Total Pass           : " + str(main.TOTAL_TC_PASS)
        testResult =  testResult + "\n Total Fail           : " + str(main.TOTAL_TC_FAIL)
        testResult =  testResult + "\n Total No Result      : " + str(main.TOTAL_TC_NORESULT)
        testResult =  testResult + "\n Success Percentage   : " + str(main.TOTAL_TC_SUCCESS) + "%"
        testResult =  testResult + "\n Execution Result     : " + str(main.TOTAL_TC_EXECPERCENT) + "%"
        
        #main.log.report(testResult)
        main.testResult = testResult
        main.log.exact(testResult)
                
    def updateCaseResults(self,main):
        '''
            Update the case result based on the steps execution and asserting each step in the test-case
        '''
        case = str(main.CurrentTestCaseNumber)
        
        if main.testCaseResult[case] == 2:
            main.TOTAL_TC_RUN  = main.TOTAL_TC_RUN + 1
            main.TOTAL_TC_NORESULT = main.TOTAL_TC_NORESULT + 1
            main.log.exact("\n**********************************\n Result: No Assertion Called \n**********************************\n")
        elif main.testCaseResult[case] == 1:
            main.TOTAL_TC_RUN  = main.TOTAL_TC_RUN  + 1
            main.TOTAL_TC_PASS =  main.TOTAL_TC_PASS + 1
            main.log.exact("\n**********************************\n Result: Pass \n***********************************\n")
        elif main.testCaseResult[case] == 0:
            main.TOTAL_TC_RUN  = main.TOTAL_TC_RUN  + 1
            main.TOTAL_TC_FAIL = main.TOTAL_TC_FAIL + 1
            main.log.exact("\n**********************************\n Result: Failed \n**********************************\n")

    


def _echo(self):
    print "THIS IS ECHO"

