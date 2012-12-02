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
        self.wrapped = sys.modules[__name__]

    def connect(self,user_name, ip_address, pwd,options):
        '''
          this subroutine is to launch pox controller . It must have arguments as : 
          user_name  = host name ,
          ip_address = ip address of the host ,
          pwd = password of host ,
          options = it is a topology hash which will consists the component's details for the test run

          *** host is here a virtual mahine or system where pox framework hierarchy exists
        '''

        poxLibPath = 'default'
        command = "./pox.py " 
        for item in options.keys():
            if isinstance(options[item],dict):
                # iterate
                command = command + item
                for items in options[item].keys():
                    if options[item][items] == "None":
                        command = command + " --" + items + " "
                    else :
                        command = command + " --" + items + "=" + options[item][items] + " "
            else:
                if item == 'pox_lib_location':
                    poxLibPath = options[item]
                
        self.handle = super(Emulator, self).connect(user_name, ip_address, pwd)
        self.handle.expect("openflow")
        if self.handle :#and outputComp:
            main.log.info("Entering into POX hierarchy")
            if options['pox_lib_location'] != 'default':
                self.execute(cmd="cd "+poxLibPath,prompt="/pox\$",timeout=120)
            else:    
                self.execute(cmd="cd ~/pox/",prompt="/pox\$",timeout=120)
            main.log.info("launching POX controller with given components")
            self.execute(cmd=command,prompt="DEBUG:",timeout=120)
        else :
            main.log.error("Connection failed to the host"+user_name+"@"+ip_address)
            main.log.error("Failed to connect to the POX controller")
    
    def exit(self,handle):
        if self.handle:
            self.execute(cmd="exit()",prompt="/pox\$",timeout=120)
        else :
            main.log.error("Connection failed to the host") 



            
            
    def log_message(self,msg):
        super(Emulator, self).log_message(self,msg)
            

if __name__ != "__main__":
    import sys

    sys.modules[__name__] = POX()    
