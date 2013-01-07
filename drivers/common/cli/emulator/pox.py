#!/usr/bin/env python
'''
Created on 26-Oct-2012
       
@author: Raghav Kashyap(raghavkashyap@paxterrasolutions.com)

pox driver provides the basic functions of POX controller
'''
import pexpect
import struct, fcntl, os, sys, signal
import sys
from drivers.common.cli.emulatordriver import Emulator

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
        self.name = options['name']
        poxLibPath = 'default'
        copy = super(POX, self).secureCopy(user_name, ip_address,'/home/openflow/pox/pox/core.py', pwd,path+'/lib/pox/')
        self.handle = super(Emulator, self).connect(user_name, ip_address, pwd)
        self.handle.expect("openflow")
        if self.handle:
            command = self.getcmd(options)
            #print command       
            main.log.info("Entering into POX hierarchy")
            if options['pox_lib_location'] != 'default':
                self.execute(cmd="cd "+options['pox_lib_location'],prompt="/pox\$",timeout=120)
            else:    
                self.execute(cmd="cd ~/OFAutomation-OFAutomation-0.0.1/lib/pox/",prompt="/pox\$",timeout=120)
            ### launching pox with components    
            main.log.info("launching POX controller with given components")
            self.execute(cmd=command,prompt="DEBUG:",timeout=120)
        else :
            main.log.error("Connection failed to the host"+user_name+"@"+ip_address)
            main.log.error("Failed to connect to the POX controller")
    

        
        
    def disconnect(self,handle):
        if self.handle:
            self.execute(cmd="exit()",prompt="/pox\$",timeout=120)
        else :
            main.log.error("Connection failed to the host") 


    def get_version(self):
        file_input = path+'/lib/pox/core.py'
        version = super(POX, self).get_version()
        pattern = '\s*self\.version(.*)'
        import re
        for line in open(file_input,'r').readlines():
            result = re.match(pattern, line)
            if result:
                version = result.group(0)
                version = re.sub("\s*self\.version\s*=\s*|\(|\)",'',version)
                version = re.sub(",",'.',version)
                version = "POX "+version
            
            
        return version
            

    def getcmd(self,options):
        command = "./pox.py " 
        for item in options.keys():
            if isinstance(options[item],dict):
                command = command + item
                for items in options[item].keys():
                    if options[item][items] == "None":
                        command = command + " --" + items + " "
                    else :
                        command = command + " --" + items + "=" + options[item][items] + " "
            else:
                if item == 'pox_lib_location':
                    poxLibPath = options[item]

        return command 
            

if __name__ != "__main__":
    import sys

    sys.modules[__name__] = POX()    
