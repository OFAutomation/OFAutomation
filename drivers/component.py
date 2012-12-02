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
        self = self
        
    def log_message(self,handle,message):
        str2 = str(handle).split()
        str2=re.split("(\.)+", str2[0])
        temp = str2[len(str2)-1]
        #vars(main)[temp].write(self,message)
        
    def experimentRun(self,**kwargs):
        args = utilities.parse_args(["RETURNS"],**kwargs)
        return  args["RETURNS"]    


if __name__ != "__main__":
    import sys
    sys.modules[__name__] = Component()
