#!/usr/bin/env python
import sys,re,os
''' Launcher will launch the test by creating the instance of
    OFAutomation and calling the methods run and cleanup.
'''
path = re.sub("bin$", "", os.getcwd())
sys.path.append(path+"/Core")
sys.path.append("../")
from core.ofautomation import *
oFAutomation = OFAutomation()
result = oFAutomation.run()
result = oFAutomation.cleanup()


