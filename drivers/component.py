#!/usr/bin/env python
import pexpect
import struct, fcntl, os, sys, signal
import sys
from logging import Logger

import pydoc
#pydoc.writedoc('component')
# Need to update the component module with all the required functionalites.

class Component(object):
    '''
    This is the tempalte class for components
    '''
    
    def __init__(self):
        self.default = ''
        
    def connect(self):
        self.handle = "Dummy"
        return self.handle
    
    def execcmd(self,cmd):
        import commands
        return commands.getoutput(cmd)
        
    def disconnect(self):
        self.handle = ""
        return
    
    def config(self):
        self = self
        # Need to update the configuration code
        
    def _devicelog(self,msg):
        Logger.info(self, msg)
    
    def cleanup(self):
        self = self
        
        
        

