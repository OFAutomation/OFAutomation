#!/usr/bin/env python
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
            return getattr(self.wrapped, name)
        except AttributeError:
            def experimentHandling(**kwargs):
                if main.EXPERIMENTAL_MODE == main.TRUE:
                    result = self.experimentRun(**kwargs)
                    main.log.info("EXPERIMENTAL MODE. API "+str(name)+" not yet implemented. Returning dummy values")
                    return result 
                else:
                    return main.FALSE
            return experimentHandling
        
        
    def connect(self,child):
        child = str(child).split()
        child=re.split("(\.)+", child[0])
        child = child[len(child)-1]
        
        return child
    
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
        return main.TRUE
    
    def _updateComponentHeaders(self):
        for driver in main.driversList:
            vars(main)[driver].write(main.logHeader)
            
        
    def log_message(self,child):
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
