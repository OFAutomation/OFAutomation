#!/usr/bin/env python
import pexpect
import struct, fcntl, os, sys, signal
import sys, re
sys.path.append("../")
import pydoc
pydoc.writedoc('clidriver')

from drivers.component import Component
class CLI(Component):
    '''
        This will define common functions for CLI included.
    '''
    def __init__(self):
        super(Component, self).__init__()
        
    def connect(self,user_name, ip_address, pwd):
        '''
           Connection will establish to the remote host using ssh.
           It will take user_name ,ip_address and password as arguments<br>
           and will return the handle. 
        '''
        ssh_newkey = 'Are you sure you want to continue connecting'
        print user_name+" AAAAAAAAAAAAAA"+ip_address
        self.handle =pexpect.spawn('ssh '+user_name+'@'+ip_address)
        i=self.handle.expect([ssh_newkey,'password:',pexpect.EOF,pexpect.TIMEOUT],1)
        
        if i==0:    
            print "I say yes"
            self.handle.sendline('yes')
            i=self.handle.expect([ssh_newkey,'password:',pexpect.EOF])
        if i==1:
            #print "I give password",
            self.handle.sendline(pwd)
            self.handle.expect(user_name)
            
        elif i==2:
            print "I either got key or connection timeout"
            pass
        elif i==3: #timeout
            main.log.error("No route to the Host "+user_name+"@"+ip_address)
            return main.FALSE

        self.handle.sendline("\r")
        self.handle.logfile = sys.stdout
        
        return self.handle
        




