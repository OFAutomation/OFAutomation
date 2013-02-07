#!/usr/bin/env python
'''
Created on 20-Dec-2012
    
@author: Anil Kumar (anilkumar.s@paxterrasolutions.com)

cli will provide the CLI shell for ofautomation framework.

'''


"""
A simple command-line interface for OFAutomation.

The OFAutomation CLI provides a simple console which
makes it easy to launch the test. For example, the command run will execute the test.

ofautomation> run test DpctlTest
Several useful commands are provided.
"""

from subprocess import call
from cmd import Cmd
from os import isatty
import sys
import re
import os
import time
import threading
import __builtin__
import pprint
dump = pprint.PrettyPrinter(indent=4)
__builtin__.testthread = False
introduction = "OFAutomation is the testing framework \nDeveloped by Paxterra Solutions (www.paxterrasolutions.com)"

path = re.sub("ofautomation$", "", os.getcwd())
sys.path.append(path+"/Core")
sys.path.append("../")
from core.ofautomation import * 

class CLI( threading.Thread,Cmd,object ):
    "command-line interface to execute the test."

    prompt = 'ofautomation> '

    def __init__( self, ofautomation, stdin=sys.stdin ):
        self.ofa = ofautomation
        
        self._mainevent = threading.Event()
        threading.Thread.__init__(self)
        self.main_stop = False
        self.locals = { 'test': ofautomation }
        self.stdin = stdin
        Cmd.__init__( self )
        self.pause = False
        self.stop = False
        __builtin__.cli = self

    def emptyline( self ):
        "Don't repeat last command when you hit return."
        pass

    helpStr = (
              " ofautomation help"
    )

    def do_help( self, line ):
        "Describe available CLI commands."
        Cmd.do_help( self, line )
        if line is '':
            output( self.helpStr )
    def do_run(self,args):
        '''
        run command will execute the test with following optional command line arguments
        logdir <directory to store logs in>
        testcases <list of testcases separated by comma or range of testcases separated by hypen>
        mail <mail-id or list of mail-ids seperated by comma>
        example 1, to execute the examples specified in the ~/examples diretory.
        '''
        args = args.split()
        options = {}
        options = self.parseArgs(args,options)
        options = dictToObj(options)
        if not testthread:
            test = TestThread(options)
            test.start()
        else :
            print main.TEST+ " test execution paused, please resume that before executing to another test"
                    
    def do_resume(self, line):
        '''
        resume command will continue the execution of paused test.
        ofautomation>resume
        [2013-01-07 23:03:44.640723] [PoxTest] [STEP]  1.1: Checking the host reachability using pingHost
        2013-01-07 23:03:44,858 - PoxTest - INFO - Expected Prompt Found
        ....
        '''
        if testthread:
            testthread.play()
        else :
            print "There is no test to resume"
    
    def do_nextstep(self,line):
        '''
        nextstep will execute the next-step of the paused test and 
        it will pause the test after finishing of step.
        
        ofautomation> nextstep
        Will pause the test's execution, after completion of this step.....
        
        ofautomation> [2013-01-07 21:24:26.286601] [PoxTest] [STEP]  1.8: Checking the host reachability using pingHost
        2013-01-07 21:24:26,455 - PoxTest - INFO - Expected Prompt Found
        .....
        ofautomation>
        
        '''
        if testthread:
            main.log.info("Executing the nextstep, Will pause test execution, after completion of the step")
            testthread.play()
            time.sleep(.1)
            testthread.pause()
        else:
            print "There is no paused test "
        
    def do_dumpvar(self,line):
        '''
        dumpvar will print all the test data in raw format.
        usgae : 
        ofautomation>dumpvar main
        Here 'main' will be the test object.
        
        ofautomation>dumpvar params 
        here 'params' will be the parameters specified in the params file.
        
        ofautomation>dumpvar topology
        here 'topology' will be topology specification of the test specified in topo file.
        '''
        if testthread:
            if line == "main":
                dump.pprint(vars(main))
            else :
                try :
                    dump.pprint(vars(main)[line])
                except KeyError,e:
                    print e
        else :
            print "There is no paused test "
            
    def do_currentcase(self,line):
        '''
        currentcase will return the current case in the test execution.
        
        ofautomation>currentcase
        Currently executing test case is: 2
         
        '''
        if testthread:
            print "Currently executing test case is: "+str(main.CurrentTestCaseNumber)
        else :
            print "There is no paused test "
            
            
    def do_currentstep(self,line):
        '''
        currentstep will return the current step in the test execution.
         
        ofautomation>currentstep
        Currently executing test step is: 2.3
        '''
        if testthread:
            print "Currently executing test step is: "+str(main.CurrentTestCaseNumber)+'.'+str(main.stepCount)
        else :
            print "There is no paused test "
    
    
    def do_stop(self,line):
        '''
        Will stop the paused test, if any !
        '''
        if testthread:
            testthread.stop()
            
        return 'exited by user command'
        
    def do_gettest(self,line):
        '''
        gettest will return the test name which is under execution or recently executed.
        
        Test under execution:
        ofautomation>gettest 
        Currently executing Test is: PoxTest
        
        Test recently executed:
        Recently executed test is: MininetTest
        '''
        try :
            if testthread :
                print "Currently executing Test is: "+main.TEST
            else :
                print "Recently executed test is: "+main.TEST
            
        except NameError:
            print "There is no previously executed Test"
            
    def do_showlog(self,line):
        '''
        showlog will show the test's Log
        ofautomation>showlog
        Last executed test's log is : //home/openflow/OFAutomation/logs/PoxTest_07_Jan_2013_21_42_11/PoxTest_07_Jan_2013_21_42_11.log
        .....
        ofautomation>showlog
        Currently executing Test's log is: /home/openflow/OFAutomation/logs/PoxTest_07_Jan_2013_21_46_58/PoxTest_07_Jan_2013_21_46_58.log
        .....
        '''
        try :
            if testthread :
                print "Currently executing Test's log is: "+main.LogFileName
                
            else :
                print "Last executed test's log is : "+main.LogFileName
            
            logFile = main.LogFileName
            logFileHandler = open(logFile, 'r')
            for msg in logFileHandler.readlines() :
                print msg,
                
            logFileHandler.close()
            
        except NameError:
            print "There is no previously executed Test"
            
    
            
    def parseArgs(self,args,options):
        '''
        This will parse the command line arguments.
        '''
        options = self.initOptions(options)
        try :
            for index, option in enumerate(args):
                if index > 0 :
                    if re.match("logdir|mail|example|testdir|testcases", option, flags = 0):
                        index = index+1
                        options[option] = args[index]
                        options = self.testcasesInRange(index,option,args,options)
                else :
                    options['testname'] = option
        except IndexError,e:
            print e
            
        return options
    
    def initOptions(self,options):
        '''
        This will initialize the commandline options.
        '''
        options['logdir'] = None
        options['mail'] = None
        options['example'] = None
        options['testdir'] = None
        options['testcases'] = None
        return options   
    
    def testcasesInRange(self,index,option,args,options):
        '''
        This method will handle testcases list,specified in range [1-10].
        '''
        if re.match("testcases",option,1):
            testcases = []
            args[index] = re.sub("\[|\]","",args[index],0)
            m = re.match("(\d+)\-(\d+)",args[index],flags=0)
            if m:
                start_case = eval(m.group(1))
                end_case = eval(m.group(2))
                if (start_case <= end_case):
                    i = start_case
                    while i <= end_case:
                        testcases.append(i)
                        i= i+1         
                else :
                    print "Please specify testcases properly like 1-5"
            else :
                options[option] = args[index]
                return options
            options[option] = str(testcases)
            
        return options
    
    def cmdloop(self, intro=introduction):
        print introduction
        while True:
            try:
                super(CLI, self).cmdloop(intro="")
                self.postloop()
            except KeyboardInterrupt:
                testthread.pause()

    def do_echo( self, line ):
        '''
        Echoing of given input.
        '''
        output(line)

    def do_sh( self, line ):
        '''
        Run an external shell command
        sh pwd
        sh ifconfig etc.
        '''
        call( line, shell=True )


    def do_py( self, line ):
        '''
        Evaluate a Python expression.
        
        py main.log.info("Sample Log Information")
        2013-01-07 12:07:26,804 - PoxTest - INFO - Sample Log Information
        
        '''
        try:
            exec( line )
        except Exception, e:
            output( str( e ) + '\n' )
            
    def do_interpret(self,line):
        '''
        interpret will translate the single line openspeak statement to equivalent python script.
        
        ofautomation> interpret ASSERT result EQUALS main.TRUE ONPASS "Ping executed successfully" ONFAIL "Ping failed"
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Ping executed successfully",onfail="Ping failed")
 
        '''
        from core import openspeak
        ospk = openspeak.OpenSpeak()
        try :
            translated_code = ospk.interpret(text=line)
            print translated_code
        except AttributeError, e:
            print 'Dynamic params are not allowed in single statement translations'
        
    def do_do (self,line):
        '''
        Do will translate and execute the openspeak statement for the paused test.
        do <OpenSpeak statement>
        '''
        if testthread:
            from core import openspeak
            ospk = openspeak.OpenSpeak()
            try :
                translated_code = ospk.interpret(text=line)
                eval(translated_code)
            except (AttributeError,SyntaxError), e:
                print 'Dynamic params are not allowed in single statement translations'
        else :
            print "Do will translate and execute the openspeak statement for the paused test.\nPlease use interpret to translate the OpenSpeak statement."
            
    def do_compile(self,line):
        '''
        compile will translate the openspeak (.ospk) file into OFAutomation test script (python).
        It will receive the openspeak file path as input and will generate 
        equivalent test-script file in the same directory. 
        
        usage:
        -----
        ofautomation>compile /home/openflow/OFAutomation/PoxTest.ospk
        
        Auto-generated test-script file is /home/openflow/OFAutomation/PoxTest.py
        '''
        from core import openspeak
        openspeak = openspeak.OpenSpeak()      
        openspeakfile = line
        if os.path.exists(openspeakfile) :
            openspeak.compiler(openspeakfile=openspeakfile,writetofile=1)
            print "Auto-generated test-script file is "+ re.sub("ospk","py",openspeakfile,0)
        else:
            print 'There is no such file : '+line

    def do_exit( self, _line ):
        "Exit"
        if testthread:
            testthread.stop()
            
        sys.exit()

        return 'exited by user command'

    def do_quit( self, line ):
        "Exit"
        return self.do_exit( line )

    def do_EOF( self, line ):
        "Exit"
        output( '\n' )
        return self.do_exit( line )

    def isatty( self ):
        "Is our standard input a tty?"
        return isatty( self.stdin.fileno() )

    def do_noecho( self, line ):
        "Run an interactive command with echoing turned off."
        if self.isatty():
            quietRun( 'stty -echo' )
        self.default( line )
        if self.isatty():
            quietRun( 'stty echo' )

    def do_source( self, line ):
        '''
        Read shell commands from an input file and execute them sequentially.
        cmdsource.txt :
        
        "pwd
         ls "
         
        ofautomation>source /home/openflow/cmdsource.txt
        /home/openflow/OFAutomation/bin/
        cli.py  __init__.py
        
        '''
        
        args = line.split()
        if len(args) != 1:
            error( 'usage: source <file>\n' )
            return
        try:
            self.inputFile = open( args[ 0 ] )
            while True:
                line = self.inputFile.readline()
                if len( line ) > 0:
                    call( line, shell=True )
                else:
                    break
        except IOError:
            error( 'error reading file %s\n' % args[ 0 ] )
    
    def do_updatedriver(self,line):
        '''
         updatedriver will update the given driver name which exists into mentioned config file.
         It will receive two optional arguments :
         
         1. Config File Path 
         2. Drivers List to be updated.
        
         Default : config file = "~/OFAutomation/config/updatedriver" ,
                   Driver List = all drivers specified in config file .
        '''
        args = line.split()
        config = ''
        drivers = ''
        try :
            for index, option in enumerate(args):
                if option == 'config':
                    index = index + 1
                    config = args[index]
                elif option == 'drivers' :
                    index = index + 1 
                    drivers = args[index]
        except IndexError:
            pass        
        import updatedriver
        converter = updatedriver.UpdateDriver()
        
        if config == '':
            path = re.sub("(bin)$", "", os.getcwd())
            config = path + "/config/updatedriver.cfg"
            configDict = converter.configparser(config)
            
        else :
            converter.configparser(config)
            configDict = converter.configparser(config)
           
            
        converter.writeDriver(drivers)
                      
       
                     
        
    def do_time( self, line ):
        "Measure time taken for any command in OFAutomation."
        start = time.time()
        self.onecmd(line)
        elapsed = time.time() - start
        self.stdout.write("*** Elapsed time: %0.6f secs\n" % elapsed)

    def default( self, line ):
        """Called on an input line when the command prefix is not recognized."""
        first, args, line = self.parseline( line )
        if not args:
            return
        if args and len(args) > 0 and args[ -1 ] == '\n':
            args = args[ :-1 ]
        rest = args.split( ' ' )

        error( '*** Unknown command: %s\n' % first )



class TestThread(threading.Thread):
    '''
    TestThread class will handle the test execution and will communicate with the thread in the do_run.
    '''
    def __init__(self,options):
        self._stopevent = threading.Event()
        threading.Thread.__init__(self)
        self.is_stop = False
        self.options = options
        __builtin__.testthread = self

    def run(self):
        '''
        Will execute the test.
        '''
        while not self.is_stop :
            if not self._stopevent.isSet():
                self.ofAutomation = OFAutomation(self.options)
                try :
                    if self.ofAutomation.init_result:
                        result = self.ofAutomation.run()
                        if not self.is_stop :
                            result = self.ofAutomation.cleanup()
                        self.is_stop = True
                except(KeyboardInterrupt):
                    print "Recevied Interrupt,cleaning-up the logs and drivers before exiting"
                    result = self.ofAutomation.cleanup()
                    self.is_stop = True

        __builtin__.testthread = False       

    def pause(self):
        '''
        Will pause the test.
        '''
        print "Will pause the test's execution, after completion of this step.....\n\n\n\n"
        cli.pause = True
        self._stopevent.set()

    def play(self):
        '''
        Will resume the paused test.
        '''
        self._stopevent.clear()
        cli.pause = False
        
    def stop(self):
        '''
        Will stop the test execution.
        '''
        
        print "Stopping the test"
        self.is_stop = True
        cli.stop = True
        __builtin__.testthread = False
        
def output(msg):
    '''
    Simply, print the message in console
    '''
    print msg

def error(msg):
    '''
    print the error message.
    '''
    print msg

def dictToObj(dictionary):
    '''
    This will facilitates the converting of the dictionary to the object.
    This method will help to send options as object format to the test.
    '''
    if isinstance(dictionary, list):
        dictionary = [dictToObj(x) for x in dictionary]
    if not isinstance(dictionary, dict):
        return dictionary
    class Convert(object):
        pass
    obj = Convert()
    for k in dictionary:
        obj.__dict__[k] = dictToObj(dictionary[k])
    return obj


if __name__ == '__main__':
    if len(sys.argv) > 1:
        CLI("test").onecmd(' '.join(sys.argv[1:]))
    else:
        CLI("test").cmdloop()