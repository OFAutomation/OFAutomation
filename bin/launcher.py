#!/usr/bin/env python
''' 
Created on 22-Oct-2012

@author: Anil Kumar (anilkumar.s@paxterrasolutions.com)

Launcher will launch the test by creating the instance of
OFAutomation and calling the methods run and cleanup.
'''
import sys,re,os

path = re.sub("bin$", "", os.getcwd())
sys.path.append(path+"/Core")
sys.path.append("../")
from core.ofautomation import *
try :
    oFAutomation = OFAutomation()
    try :
        if oFAutomation.init_result:
            result = oFAutomation.run()
        
        result = oFAutomation.cleanup()
    except(KeyboardInterrupt):
        print "Recevied Interrupt,cleaning-up the logs and drivers before exiting"
        result = oFAutomation.cleanup()
        
except(KeyboardInterrupt):
    print "Recevied Interrupt, terminating Test"
    exit(0)
    
