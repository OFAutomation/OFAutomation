#!/usr/bin/env python
'''
Created on 26-Oct-2012

@author: Anil Kumar (anilkumar.s@paxterrasolutions.com)

Mininet is the basic driver which will handle the Mininet functions
'''

import pexpect
import struct
import fcntl
import os
import signal
import re
import sys
import core.ofautomation
sys.path.append("../")
from common.apidriver import API
import logging

sys.path.append(path+"/lib/flowvisor-test/tests")
sys.path.append(path+"/lib/flowvisor-test/src/python/")

import templatetest
import testutils
import oftest.cstruct as ofp
import oftest.message as message
import oftest.parse as parse
import oftest.action as action
import oftest.error as error
import socket

config_default = {
    "param"              : None,
    "fv_cmd"             : "/home/openflow/flowvisor/scripts/flowvisor.sh",
    "platform"           : "local",
    "controller_host"    : "127.0.0.1",
    "controller_port"    : 6633,
    "timeout"            : 3,
    "port_count"         : 4,
    "base_of_port"       : 1,
    "base_if_index"      : 1,
    "test_spec"          : "all",
    "test_dir"           : ".",
    "log_file"           : "/home/openflow/fvt.log",
    "list"               : False,
    "debug"              : "debug",
    "dbg_level"          : logging.DEBUG,
    "port_map"           : {},
    "test_params"        : "None"
}

def test_set_init(config):
    """
    Set up function for basic test classes
    @param config The configuration dictionary; see fvt
    """
    global basic_port_map
    global basic_fv_cmd
    global basic_logger
    global basic_timeout
    global basic_config
    global baisc_logger

    basic_fv_cmd = config["fv_cmd"]
    #basic_logger = logging.getLogger("fvtdriver")
    #logFileHandler = logging.FileHandler(config_default["log_file"])
    #logFileHandler.setLevel(config_default["dbg_level"])
    #basic_logger.setLevel(config_default["dbg_level"])
    #_formatter = logging.Formatter("%(asctime)s  %(name)-10s: %(levelname)-8s: %(message)s")
    #logFileHandler.setFormatter(_formatter)
    #basic_logger.addHandler(logFileHandler)

    #basic_logger.info("Initializing test set")
    basic_timeout = config["timeout"]
    basic_port_map = config["port_map"]
    basic_config = config

class FvtDriver(API,templatetest.TemplateTest):

    def __init__(self):
        super(API, self).__init__()
        print 'init'
                                                

    def connect(self,**kwargs):
        for key in kwargs:
            vars(self)[key] = kwargs[key]
        
        self.name = self.options['name']
        connect_result = super(API,self).connect()
        self.logFileName = main.logdir+"/"+self.name+".session"
        config_default["log_file"] = self.logFileName
        test_set_init(config_default)
        basic_logger = vars(main)[self.name+'log']
        basic_logger.info("Calling my test setup")
        self.setUp(basic_logger)

        (self.fv, self.sv, sv_ret, ctl_ret, sw_ret) = testutils.setUpTestEnv(self, fv_cmd=basic_fv_cmd)
        
        self.chkSetUpCondition(self.fv, sv_ret, ctl_ret, sw_ret)
        return main.TRUE

    def simplePacket(self,dl_src):
        dl_src = vars(testutils)[dl_src]
        return testutils.simplePacket(dl_src = dl_src)
   
    def genPacketIn(self, in_port, pkt):
        return testutils.genPacketIn(in_port=in_port, pkt=pkt)
     
    def ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True, hdr_only=True):
        return testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore, hdr_only)

    def disconnect(self,handle):
        return main.TRUE

    def setUp(self,basic_logger):
        self.logger = basic_logger
        #basic_logger.info("** START TEST CASE " + str(self))
        if basic_timeout == 0:
            self.timeout = None
        else:
            self.timeout = basic_timeout
        self.fv = None
        self.sv = None
        self.controllers = []
        self.switches = []

    def close_log_handles(self) :
        '''
        vars(main)[self.name+'log'].removeHandler(self.log_handler)
        if self.logfile_handler:
            self.logfile_handler.close()
        '''
        return main.TRUE