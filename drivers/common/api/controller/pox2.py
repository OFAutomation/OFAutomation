#!/usr/bin/env python
import sys
sys.path.append("../")
from drivers.common.api.controllerdriver import Controller

class POX(Controller):
    # The common functions for emulator included in emulatordriver
    def __init__(self):
        super(Controller, self).__init__()
        
    def connect(self) :
        return main.TRUE