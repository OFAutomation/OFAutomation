#!/usr/bin/env python
import pexpect
import struct, fcntl, os, sys, signal
import sys
from drivers.common.cli.emulatordriver import Emulator
import pydoc
pydoc.writedoc('pox')

class POX(Emulator):
    '''
        pox driver provides the basic functions of POX controller
    '''
    def __init__(self):
        super(Emulator, self).__init__()
        self.handle = self
        
    def connect(self,user_name, ip_address, pwd,options):
        self.handle = super(Emulator, self).connect(user_name, ip_address, pwd)
        if self.handle :
            self.handle.expect("openflow")
            self.handle.sendline("cd pox")
            self.handle.sendline("\r")
            self.handle.expect("pox")
            self.handle.sendline("./pox.py log.level --"+options['log_level']+" "+options['component'])
            self.handle.sendline("\r")
            #handle.expect("DEBUG:samples.of_tutorial:Controlling")
            return self.handle
        else :
            main.log.error("Connection failed to the host"+user_name+"@"+ip_address) 
            main.log.error("Failed to connect to the POX controller")
               
    
    def exit(self,handle):
        if self.handle:
            self.handle = handle 
            self.handle.sendline("exit")
            self.handle.sendline("\r")
        else :
            main.log.error("Connection failed to the host") 
            
        
