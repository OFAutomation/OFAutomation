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
import new
import xmldict
module = new.module("test")
import openspeak
global path, drivers_path, core_path, tests_path,logs_path
path = re.sub("(core|bin)$", "", os.getcwd())
drivers_path = path+"/drivers/"
core_path = path+"/core"
tests_path = path+"/tests/"
logs_path = path+"/logs/"
config_path = path + "/config/"
sys.path.append(path)
sys.path.append( drivers_path)
sys.path.append(core_path )
sys.path.append(tests_path)



from core.utilities import Utilities

import logging 
import datetime
from optparse import OptionParser

class OFAutomation:
    '''
    
    OFAutomation will initiate the specified test. 
    The main tasks are : 
    * Initiate the required Component handles for the test. 
    * Create Log file  Handles.
    
    '''
    def __init__(self,options):
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
        self.lastcommand = None
        self.testDir = tests_path 
        self.configFile = config_path + "ofa.cfg" 
        self.parsingClass = "xmlparser"
        self.parserPath = core_path + "/xmlparser"
        self.loggerPath = core_path + "/logger"
        self.loggerClass = "Logger"
        self.logs_path = logs_path
        
        self.configparser()
        verifyOptions(options)
        load_logger()
        self.componentDictionary = {}
        self.componentDictionary = self.topology ['COMPONENT']
        self.driversList=[]
        
        for component in self.componentDictionary :
            self.driversList.append(self.componentDictionary[component]['type'])
            
        self.driversList = list(set(self.driversList)) # Removing duplicates.
        # Checking the test_target option set for the component or not
        if type(self.componentDictionary) == dict:
            for component in self.componentDictionary.keys():
                if 'test_target' in self.componentDictionary[component].keys():
                    self.test_target = component
             
        # Checking for the openspeak file and test script 
            
        self.logger.initlog(self)

        # Creating Drivers Handles
        initString = "\n************************************\n CASE INIT \n*************************************\n"
        self.log.exact(initString)
        self.driverObject = {}
        if type(self.componentDictionary) == dict:
            for component in self.componentDictionary.keys():
                self.componentInit(component)
    
    def configparser(self):
        '''
        It will parse the config file (ofa.cfg) and return as dictionary
        '''
        matchFileName = re.match(r'(.*)\.cfg', self.configFile, re.M | re.I)
        if matchFileName:
            xml = open(self.configFile).read()
            try :
                self.configDict = xmldict.xml_to_dict(xml)
                return self.configDict
            except :
                print "There is no such file to parse " + self.configFile
                        
    def componentInit(self,component):
        '''
        This method will initialize specified component
        '''
        global driver_options
        self.log.info("Creating component Handle: "+component)
        #### R
        driver_options = {}         
        if 'COMPONENTS' in self.componentDictionary[component].keys():
            driver_options =dict(self.componentDictionary[component]['COMPONENTS'])

        driver_options['name']=component
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
                self.log.error("Failed to create component handle for "+component)
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
        
        import testparser
        testCaseNumber = str(testCaseNumber)
        testFile = self.tests_path + "/"+self.TEST + "/"+self.TEST + ".py"
        test = testparser.TestParser(testFile)
        main.testscript = test.testscript
        code = test.getStepCode()
        stepCount = 0
        stopped = False
        stepList = code[testCaseNumber].keys()
        self.stepCount = 0
        while self.stepCount < len(code[testCaseNumber].keys()):
            if not cli.pause:
                try :
                    step = stepList[self.stepCount]
                    exec code[testCaseNumber][step] in module.__dict__
                    self.stepCount = self.stepCount + 1
                except TypeError,e:
                    self.stepCount = self.stepCount + 1
                    self.log.error(e)
            if cli.stop:
                cli.stop = False
                stopped = True
                self.TOTAL_TC_NORESULT = self.TOTAL_TC_NORESULT + 1
                self.testCaseResult[str(self.CurrentTestCaseNumber)] = "Stopped"
                self.logger.updateCaseResults(self)
                result = self.cleanup()
                break    
        
        if not stopped :
            self.testCaseResult[str(self.CurrentTestCaseNumber)] = self.CASERESULT
            self.logger.updateCaseResults(self)
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
        
    def pause(self):
        '''
        This function will pause the test's execution, and will continue after user provide 'resume' command.
        '''
        __builtin__.testthread.pause()
    
    def onfail(self,*components):
        '''
        When test step failed, calling all the components onfail. 
        '''
         
        if not components:
            try :
                for component in self.componentDictionary.keys():
                    tempObject  = vars(self)[component]
                    result = tempObject.onfail()
            except(Exception),e:
                print str(e)
                result = self.FALSE
                
        else:
            try :
                for component in components:
                    tempObject  = vars(self)[component]
                    result = tempObject.onfail()
            except(Exception),e:
                print str(e)
                result = self.FALSE
    
    
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
            self.exit()
            
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
        if self.stepCount == 0:
            stepName = " INIT : Initializing the test case :"+self.CurrentTestCase
            
        self.log.step(stepName)
        stepHeader = ""
        if self.stepCount > 1 :
            stepHeader = "\n"+"-"*45+"\nEnd of Step "+previousStep+"\n"+"-"*45+"\n"
        
        stepHeader += "\n"+"-"*45+"\nStart of Step"+stepName+"\n"+"-"*45+"\n" 
        for driver in self.driversList:
            vars(self)[driver].write(stepHeader)
            
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
        testFileHandler.close()
        #self.TOTAL_TC_PLANNED = 0
        counter = 0
        for index in range(len(testFileList)):
            lineMatch = re.match('\s+def CASE(\d+)(.*):',testFileList[index],0)
            if lineMatch:
                counter  = counter + 1
                self.TOTAL_TC_PLANNED = counter
                
    def exit(self):
        __builtin__.testthread = None
        sys.exit()

def verifyOptions(options):
    '''
    This will verify the command line options and set to default values, if any option not given in command line.
    '''
    import pprint
    pp = pprint.PrettyPrinter(indent=4)

    #pp.pprint(options)
    verifyTest(options)
    verifyExample(options)
    verifyTestScript(options)
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
        main.classPath = "examples."+main.TEST+"."+main.TEST
    else :
        print "Test or Example not specified please specify the --test <test name > or --example <example name>"
        self.exit()

def verifyExample(options):
    if options.example:
        main.testDir = path+'/examples/'
        main.tests_path = path+"/examples/"
        main.classPath = "examples."+main.TEST+"."+main.TEST
               
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
    elif main.params.has_key('mail'):
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
        
def verifyTestScript(options):
    '''
    Verifyies test script.
    '''
    main.openspeak = openspeak.OpenSpeak()        
    openspeakfile = main.testDir+"/" + main.TEST + "/" + main.TEST + ".ospk"
    testfile = main.testDir+"/" + main.TEST + "/" + main.TEST + ".py"
    if os.path.exists(openspeakfile) :
        main.openspeak.compiler(openspeakfile=openspeakfile,writetofile=1)
    elif os.path.exists(testfile):
        print ''
    else:
        print "\nThere is no :\""+main.TEST+"\" test, Please Provide OpenSpeak Script/ test script"
        __builtin__.testthread = None
        main.exit()
              
    try :
        testModule = __import__(main.classPath, globals(), locals(), [main.TEST], -1)
    except(ImportError):
        print "There is no test like "+main.TEST
        main.exit()       
    #try :
    testClass = getattr(testModule, main.TEST)
    #except(AttributeError):
    #   print main.TEST+ " module object has no attribute :"+main.TEST
    #    main.exit()
    main.testObject = testClass()
    load_parser()
    #testHandler = TestHandler()
    main.params = main.parser.parseParams(main.classPath)     #testHandler.parseParams(main.classPath)
    main.topology = main.parser.parseTopology(main.classPath) #testHandler.parseTopology(main.classPath)

def verifyParams():
    try :
        main.params = main.params['PARAMS']
    except(KeyError):
        print "Error with the params file: Either the file not specified or the format is not correct"
        main.exit()            
    
    try :
        main.topology = main.topology['TOPOLOGY']
    except(KeyError):
        print "Error with the Topology file: Either the file not specified or the format is not correct"
        main.exit()
        
def load_parser() :
    '''
    It facilitates the loading customised parser for topology and params file.
    It loads parser mentioned in tab named parser of ofa.cfg file.
    It also loads default xmlparser if no parser have specified in ofa.cfg file.

    '''
    confighash = main.configDict
    if 'file' in confighash['config']['parser'] and 'class' in confighash['config']['parser']:
        if confighash['config']['parser']['file'] != None or confighash['config']['parser']['class']!= None :
            if os.path.exists(confighash['config']['parser']['file']) :
                module = re.sub(r".py\s*$","",confighash['config']['parser']['file'])
                moduleList = module.split("/")
                newModule = ".".join([moduleList[len(moduleList) - 2],moduleList[len(moduleList) - 1]])
                try :
                    parsingClass = confighash['config']['parser']['class']
                    parsingModule = __import__(newModule, globals(), locals(), [parsingClass], -1)
                    parsingClass = getattr(parsingModule, parsingClass)
                    main.parser = parsingClass()
                    #hashobj = main.parser.parseParams(main.classPath)
                    if hasattr(main.parser,"parseParams") and hasattr(main.parser,"parseTopology") and hasattr(main.parser,"parse") :
                        
                        pass
                    else:
                        
                        main.exit()

                except ImportError:
                    print sys.exc_info()[1]
                    main.exit()
            else :
                print "No Such File Exists !!"+ confighash['config']['parser']['file']
                main.exit()
        elif confighash['config']['parser']['file'] == None or confighash['config']['parser']['class'] == None :  
            load_defaultParser() 
    else:
        load_defaultParser()

def load_defaultParser():
    '''
    It will load the default parser which is xml parser to parse the params and topology file.
    '''
    moduleList = main.parserPath.split("/")
    newModule = ".".join([moduleList[len(moduleList) - 2],moduleList[len(moduleList) - 1]])
    try :
        parsingClass = main.parsingClass 
        parsingModule = __import__(newModule, globals(), locals(), [parsingClass], -1)
        parsingClass = getattr(parsingModule, parsingClass)
        main.parser = parsingClass()
        if hasattr(main.parser,"parseParams") and hasattr(main.parser,"parseTopology") and hasattr(main.parser,"parse") :
            pass
        else:
            main.exit()


    except ImportError:
        print sys.exc_info()[1]


def load_logger() :
    '''
    It facilitates the loading customised parser for topology and params file.
    It loads parser mentioned in tab named parser of ofa.cfg file.
    It also loads default xmlparser if no parser have specified in ofa.cfg file.

    '''
    confighash = main.configDict
    if 'file' in confighash['config']['logger'] and 'class' in confighash['config']['logger']:
        if confighash['config']['logger']['file'] != None or confighash['config']['logger']['class']!= None :
            if os.path.exists(confighash['config']['logger']['file']) :
                module = re.sub(r".py\s*$","",confighash['config']['logger']['file'])
                moduleList = module.split("/")
                newModule = ".".join([moduleList[len(moduleList) - 2],moduleList[len(moduleList) - 1]])
                try :
                    loggerClass = confighash['config']['logger']['class']
                    loggerModule = __import__(newModule, globals(), locals(), [loggerClass], -1)
                    loggerClass = getattr(loggerModule, loggerClass)
                    main.logger = loggerClass()
                    #hashobj = main.parser.parseParams(main.classPath)

                except ImportError:
                    print sys.exc_info()[1]
            else :
                print "No Such File Exists !!"
                main.exit()
        elif confighash['config']['parser']['file'] == None or confighash['config']['parser']['class'] == None :  
            load_defaultlogger() 
    else:
        load_defaultlogger()

def load_defaultlogger():
    '''
    It will load the default parser which is xml parser to parse the params and topology file.
    '''
    moduleList = main.loggerPath.split("/")
    newModule = ".".join([moduleList[len(moduleList) - 2],moduleList[len(moduleList) - 1]])
    try :
        loggerClass = main.loggerClass 
        loggerModule = __import__(newModule, globals(), locals(), [loggerClass], -1)
        loggerClass = getattr(loggerModule, loggerClass)
        main.logger = loggerClass()

    except ImportError:
        print sys.exc_info()[1]
        main.exit()    

def _echo(self):
    print "THIS IS ECHO"

