#/usr/bin/env python
'''
Created on 26-Nov-2012
       
@author: Raghav Kashyap(raghavkashyap@paxterrasolutions.com)

DPCTL driver class provides the basic functions of DPCTL controller
'''
import pexpect
import struct, fcntl, os, sys, signal
import sys
from drivers.common.cli.toolsdriver import Tools
import pydoc
#pydoc.writedoc('pox')
from drivers.common.clidriver import CLI
import re
import os
import sys

class DPCTL(Tools):
    '''
     pox driver's template class provides the basic functions of POX controller
    '''
    def __init__(self):
        super(DPCTL, self).__init__()
        self.handle = self
        self.wrapped = sys.modules[__name__]
    
    def connect(self,user_name, ip_address, pwd,options):
        # Here the main is the OFAutomation instance after creating all the log handles.
        self.handle = super(DPCTL, self).connect(user_name, ip_address, pwd)
        if self.handle :
            main.log.info("Network is launching")
        else :
            main.log.error("Connection failed to the host"+user_name+"@"+ip_address) 
            main.log.error("Failed to connect to the Mininet")


    def addFlow(self,**flowParameters):
        '''
         addFlow create a new flow entry into flow table using "dpctl"
        '''
        args = utilities.parse_args(["TCPIP","TCPPORT","INPORT","ACTION","TIMEOUT"],**flowParameters)
        cmd = "dpctl add-flow tcp:"
        tcpIP = args["TCPIP"] if args["TCPIP"] != None else "127.0.0.1"
        tcpPort = args["TCPPORT"] if args["TCPPORT"] != None else "6634"
        timeOut = args["TIMEOUT"] if args["TIMEOUT"] != None else 120
        cmd = cmd + tcpIP + ":" + tcpPort + " in_port=" + str(args["INPORT"]) + ",idle_timeout=" + str(args["TIMEOUT"]) +",actions=" + args["ACTION"]   
        response = self.execute(cmd=cmd,prompt="\~\$",timeout=60 )
        if utilities.assert_matches(expect="openflow",actual=response,onpass="Flow Added Successfully",onfail="Adding Flow Failed!!!"):
            return main.TRUE
        else :
            return main.FALSE

    def showFlow(self,**flowParameters):
        '''
         showFlow dumps the flow entries of flow table using "dpctl"
        '''
        args = utilities.parse_args(["TCPIP","TCPPORT"],**flowParameters)
        tcpIP = args["TCPIP"] if args["TCPIP"] != None else "127.0.0.1"
        tcpPort = args["TCPPORT"] if args["TCPPORT"] != None else "6634"
        command = "dpctl show tcp:" + str(tcpIP) + ":" + str(tcpPort)
        response = self.execute(cmd=command,prompt="get_config_reply",timeout=240)
        if utilities.assert_matches(expect='features_reply',actual=response,onpass="Show flow executed",onfail="Show flow execution Failed"):
            return main.TRUE
        else :
            return main.FALSE

    def dumpFlow(self,**flowParameters):
        '''
         dumpFlow  gives installed flow information
        '''
        args = utilities.parse_args(["TCPIP","TCPPORT"],**flowParameters)
        tcpIP = args["TCPIP"] if args["TCPIP"] != None else "127.0.0.1"
        tcpPort = args["TCPPORT"] if args["TCPPORT"] != None else "6634"
        command = "dpctl dump-flows tcp:" + str(tcpIP) + ":" + str(tcpPort)
        response = self.execute(cmd=command,prompt="(flow)",timeout=240) 
        print response
        return response 

        return main.TRUE
  
    def showStatus(self,**flowParameters):
        '''
         showStatus will provide the Status of given parmetes using "dpctl" 
        '''
        return main.TRUE

if __name__ != "__main__":
    import sys
    sys.modules[__name__] = DPCTL()

