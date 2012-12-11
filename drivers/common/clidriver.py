#!/usr/bin/env python
import pexpect
import struct, fcntl, os, sys, signal
import sys, re
sys.path.append("../")

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
        child = super(CLI, self).connect(self)
        ssh_newkey = 'Are you sure you want to continue connecting'
        refused = "ssh: connect to host "+ip_address+" port 22: Connection refused"
        self.handle =pexpect.spawn('ssh '+user_name+'@'+ip_address)
        self.handle.logfile = vars(main)[child]
        i=self.handle.expect([ssh_newkey,'password:',pexpect.EOF,pexpect.TIMEOUT,refused],120)
        
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
            return main.FALSE
        elif i==3: #timeout
            main.log.error("No route to the Host "+user_name+"@"+ip_address)
            return main.FALSE
        elif i==4:
            main.log.error("ssh: connect to host "+ip_address+" port 22: Connection refused")
            return main.FALSE

        self.handle.sendline("\r")
        #self.handle.logfile = sys.stdout
        
        return self.handle
    
    def disconnect(self):
        result = super(CLI, self).disconnect(self)
        result = self.execute(cmd="exit",timeout=120,prompt="(.*)")
    
    
    def execute(self, **execparams):
        '''
        It facilitates the command line execution of a given command. It has arguments as :
        cmd => represents command to be executed,
        prompt => represents expect command prompt or output,
        timeout => timeout for command execution,
        more => to provide a key press if it is on.

        It will return output of command exection.
        '''
        result = super(CLI, self).execute(self)
        defaultPrompt = '.*[$>\#]'
        args = utilities.parse_args(["CMD", "TIMEOUT", "PROMPT", "MORE"], **execparams)
        expectPrompt = args["PROMPT"] if args["PROMPT"] else defaultPrompt
        self.LASTRSP = ""
        timeoutVar = args["TIMEOUT"] if args["TIMEOUT"] else 10
        cmd = ''
        if args["CMD"]:
            cmd = args["CMD"]
        else :
            return 0
        if args["MORE"] == None:
            args["MORE"] = " "
        self.handle.sendline(cmd)
        self.lastCommand = cmd
        index = self.handle.expect([expectPrompt, "--More--", 'Command not found.', pexpect.TIMEOUT], timeout = timeoutVar)
        if index == 0:
            self.LASTRSP = self.LASTRSP + self.handle.before
            main.log.info("Expected Prompt Found")
        elif index == 1:
            self.LASTRSP = self.LASTRSP + self.handle.before
            self.handle.send(args["MORE"])
            main.log.info("Found More screen to go , Sending a key to proceed")
            indexMore = self.handle.expect(["--More--", expectPrompt], timeout = timeoutVar)
            while indexMore == 0:
                main.log.info("Found anoother More screen to go , Sending a key to proceed")
                self.handle.send(args["MORE"])
                indexMore = self.handle.expect(["--More--", expectPrompt], timeout = timeoutVar)
                self.LASTRSP = self.LASTRSP + self.handle.before
        elif index ==2:
            main.log.error("Command not found")
            self.LASTRSP = self.LASTRSP + self.handle.before
        elif index ==3:
            main.log.error("Expected Prompt not found , Time Out!!") 
            return main.FALSE
        return self.LASTRSP
        
    def runAsSudoUser(self,handle,pwd,default):
        
        i = handle.expect([".ssword:*",default, pexpect.EOF])
        if i==0:
            handle.sendline(pwd)
            handle.sendline("\r")

        if i==1:
            handle.expect(default)
        
        if i==2:
            main.log.error("Unable to run as Sudo user")
            
        return handle
        
    def log(self,message):
        child = super(CLI, self).log_message(self)
        vars(main)[child].write(message)
    

    def secureCopy(self,user_name, ip_address,filepath, pwd,dst_path):
        
        #scp openflow@192.168.56.101:/home/openflow/sample /home/paxterra/Desktop/

        '''
           Connection will establish to the remote host using ssh.
           It will take user_name ,ip_address and password as arguments<br>
           and will return the handle. 
        '''
        ssh_newkey = 'Are you sure you want to continue connecting'
        refused = "ssh: connect to host "+ip_address+" port 22: Connection refused"
        self.handle =pexpect.spawn('scp '+user_name+'@'+ip_address+':'+filepath+' '+dst_path)
        i=self.handle.expect([ssh_newkey,'password:',pexpect.EOF,pexpect.TIMEOUT,refused],120)
        
        if i==0:    
            print "I say yes"
            self.handle.sendline('yes')
            i=self.handle.expect([ssh_newkey,'password:',pexpect.EOF])
        if i==1:
            #print "I give password",
            self.handle.sendline(pwd)
            #self.handle.expect(user_name)
            
        elif i==2:
            print "I either got key or connection timeout"
            pass
        elif i==3: #timeout
            main.log.error("No route to the Host "+user_name+"@"+ip_address)
            return main.FALSE
        elif i==4:
            main.log.error("ssh: connect to host "+ip_address+" port 22: Connection refused")
            return main.FALSE

        self.handle.sendline("\r")
        #self.handle.logfile = sys.stdout
        
        return self.handle
    