#!/usr/bin/env python
import pexpect
import struct
import fcntl
import os
import sys
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
        
    def connect(self,user_name, ip_address, pwd,options):
        # Here the main is the OFAutomation instance after creating all the log handles.
        self.handle = super(Emulator, self).connect(user_name, ip_address, pwd)
        if self.handle :
            self.handle.logfile = sys.stdout
            self.handle.expect("openflow")
            main.log.info("Clearing any residual state or processes")
            self.handle.sendline("sudo mn -c")
            i = self.handle.expect([".ssword:*", pexpect.EOF])
            if i==0:
                main.log.info("Providing the password for sudo user")
                self.handle.sendline(pwd)

            if i==1:
                print self.handle.before
                
            self.handle.sendline("\r")
            self.handle.expect("openflow")
            main.log.info("Creating Virtual network in the VirtualMachine")
            self.handle.sendline("sudo mn --topo "+options['topo']+","+options['topocount']+" --mac --switch "+options['switch']+" --controller "+options['controller'])
            i = self.handle.expect([".ssword:*","mininet", pexpect.EOF])
            if i==0:
                main.log.info("Providing the password for sudo user")
                self.handle.sendline(pwd)
                self.handle.expect("mininet")
                main.log.info("Virtual network Created Successfully")

            if i==1:
                main.log.info("Virtual network Created Successfully")
            
            if i==3:
                main.log.error("Failed to create Virtual network")
            
            return self.handle
        else :
            main.log.error("Connection failed to the host"+user_name+"@"+ip_address) 
            main.log.error("Failed to connect to the Mininet")
                       
    def pingall(self):
        '''
           Verifies the reachability of the hosts using pingall command.
        '''
        if self.handle :
            main.log.info("Checking reachabilty to the hosts using pingall")
            self.handle.sendline("pingall")
            self.handle.expect("mininet")
            pattern = 'Results\:\s0\%\sdropped\s\(0\/\d+\slost\)\s*$'
            result=self.handle.before
            if utilities.assert_matches(expect=pattern,actual=result,onpass="All hosts are reaching",onfail="Unable to reach all the hosts"):
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
            self.handle.sendline(host+" ifconfig")
            self.handle.expect("mininet")
            pattern = "inet\s(addr|Mask):([0-1]{1}[0-9]{1,2}|2[0-4][0-9]|25[0-5]|[0-9]{1,2}).([0-1]{1}[0-9]{1,2}|2[0-4][0-9]|25[0-5]|[0-9]{1,2}).([0-1]{1}[0-9]{1,2}|2[0-4][0-9]|25[0-5]|[0-9]{1,2}).([0-1]{1}[0-9]{1,2}|2[0-4][0-9]|25[0-5]|[0-9]{1,2})"
            result=self.handle.before
            if utilities.assert_matches(expect=pattern,actual=result,onpass="Host Ip configured properly",onfail="Host IP didn't found") :
                return main.TRUE
            else:
                return main.FALSE
        else :
            main.log.error("Connection failed to the host") 
            
        
    def exit(self,handle):
        if self.handle:
            self.handle = handle 
            self.handle.sendline("exit")
            self.handle.sendline("\r")
        else :
            main.log.error("Connection failed to the host") 
            