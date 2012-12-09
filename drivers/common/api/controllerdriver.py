#!/usr/bin/env python
import sys
sys.path.append("../")
from drivers.common.apidriver import API

class Controller(API):
    # The common functions for emulator included in emulatordriver
    def __init__(self):
        super(API, self).__init__()
        