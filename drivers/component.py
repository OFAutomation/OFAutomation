#!/usr/bin/env python
'''
Created on 24-Oct-2012
    
@authors: Anil Kumar (anilkumar.s@paxterrasolutions.com),
          Raghav Kashyap(raghavkashyap@paxterrasolutions.com)
          
'''

import re
from logging import Logger

# Need to update the component module with all the required functionalites.

class Component(object):
    '''
    This is the tempalte class for components
    '''
    def __init__(self):
        self.default = ''
        self.wrapped = sys.modules[__name__]

    
    def __getattr__(self, name):
        '''
         This will invoke, if the attribute wasn't found the usual ways.
          Here it will look for assert_attribute and will execute when AttributeError occurs.
          It will return the result of the assert_attribute.
        '''
        try:
            main.lastcommand = name
            return getattr(self.wrapped, name)
        except AttributeError:
            try:
                def experimentHandling(**kwargs):
                    if main.EXPERIMENTAL_MODE == main.TRUE:
                        result = self.experimentRun(**kwargs)
                        main.log.info("EXPERIMENTAL MODE. API "+str(name)+" not yet implemented. Returning dummy values")
                        return result 
                    else:
                        return main.FALSE
                return experimentHandling
            except TypeError,e:
                main.log.error("Arguments for experimental mode does not have key 'retruns'" + e)
        
        
    def connect(self,child):
        child = str(child).split()
        child=re.split("(\.)+", child[0])
        child = child[len(child)-1]
        return child
    
    def execute(self,cmd):
        return main.TRUE
        #import commands
        #return commands.getoutput(cmd)
        
    def disconnect(self):
        return main.TRUE 
    
    def config(self):
        self = self
        # Need to update the configuration code
        
    def _devicelog(self,msg):
        Logger.info(self, msg)
    
    def cleanup(self):
        return main.TRUE
    
    def _updateComponentHeaders(self):
        for driver in main.driversList:
            vars(main)[driver].write(main.logHeader)
            
        
    def log(self,child):
        '''
        Here finding the for the component to which the 
        log message based on the called child object.
        Need to update here.
        '''
        child = str(child).split()
        child=re.split("(\.)+", child[0])
        child = child[len(child)-1]
        return child
    
    def get_version(self):
        return "Version unknown"

    def experimentRun(self,**kwargs):
        args = utilities.parse_args(["RETURNS"],**kwargs)
        return  args["RETURNS"]    


if __name__ != "__main__":
    import sys
    sys.modules[__name__] = Component()
