#!/usr/bin/env python
import pexpect
import struct
import fcntl
import os
import signal
import re
import sys
import core.ofautomation
sys.path.append("../")
from drivers.common.cli.emulatordriver import Emulator
from drivers.common.clidriver import CLI

import pydoc
pydoc.writedoc('mininet')

class Mininet(Emulator):
    '''
        mininet is the basic driver which will handle the Mininet functions
    '''
    def __init__(self):
        super(Emulator, self).__init__()
        self.handle = self
        self.wrapped = sys.modules[__name__]

    def connect(self,user_name, ip_address, pwd,options):
        # Here the main is the OFAutomation instance after creating all the log handles.
        self.handle = super(Emulator, self).connect(user_name, ip_address, pwd)
        if self.handle :
            #self.handle.logfile = sys.stdout
            self.handle.expect("openflow")
            main.log.info("Clearing any residual state or processes")
            result = self.execute(cmd="sudo mn -c",timeout=120,prompt="[p|P]assword")

            main.log.info("Password providing for running at sudo mode")
            result2 = self.execute(cmd="openflow",timeout=120,prompt="openflow@ETH-Tutorial:~\$")
            #preparing command to launch mininet
            main.log.info("Launching netwrok using mininet")   
            cmdString = "sudo mn --topo "+options['topo']+","+options['topocount']+" --mac --switch "+options['switch']+" --controller "+options['controller']
            result4 = self.execute(cmd=cmdString,timeout=120,prompt="mininet")
            pattern = '[p|P]assword'
            result3 = ''
            if utilities.assert_matches(expect=pattern,actual=result4,onpass="Asking for password",onfail="not asking for Password"):
                result3 = self.execute(cmd="openflow",timeout=120,prompt="openflow@ETH-Tutorial:~\$")
            else:
                result3 = result4
                main.log.info("Network is launching")

        else :
            main.log.error("Connection failed to the host"+user_name+"@"+ip_address) 
            main.log.error("Failed to connect to the Mininet")
                       
    def pingall(self):
        '''
           Verifies the reachability of the hosts using pingall command.
        '''
        if self.handle :
            main.log.info("Checking reachabilty to the hosts using pingall")
            response = self.execute(cmd="pingall",prompt="mininet>",timeout=120)
            pattern = 'Results\:\s0\%\sdropped\s\(0\/\d+\slost\)\s*$'
            if utilities.assert_matches(expect=pattern,actual=response,onpass="All hosts are reaching",onfail="Unable to reach all the hosts"):
                return main.TRUE
            else:
                return main.FALSE
        else :
            main.log.error("Connection failed to the host") 
        
    def checkIP(self,host):
        '''
            Verifies the host's ip configured or not.
        '''
        if self.handle :
            main.log.info("Pinging host "+host) 
            response = self.execute(cmd=host+" ifconfig",prompt="mininet>",timeout=120)

            pattern = "inet\s(addr|Mask):([0-1]{1}[0-9]{1,2}|2[0-4][0-9]|25[0-5]|[0-9]{1,2}).([0-1]{1}[0-9]{1,2}|2[0-4][0-9]|25[0-5]|[0-9]{1,2}).([0-1]{1}[0-9]{1,2}|2[0-4][0-9]|25[0-5]|[0-9]{1,2}).([0-1]{1}[0-9]{1,2}|2[0-4][0-9]|25[0-5]|[0-9]{1,2})"
            if utilities.assert_matches(expect=pattern,actual=response,onpass="Host Ip configured properly",onfail="Host IP didn't found") :
                return main.TRUE
            else:
                return main.FALSE
        else :
            main.log.error("Connection failed to the host") 
            

    def exit(self,handle):
        response = ''
        if self.handle:
            self.handle = handle
            response = self.execute(cmd="exit",prompt="(.*)",timeout=120)
        else :
            main.log.error("Connection failed to the host")
            response = main.FALSE
        return response  

if __name__ != "__main__":
    import sys
    sys.modules[__name__] = Mininet()
