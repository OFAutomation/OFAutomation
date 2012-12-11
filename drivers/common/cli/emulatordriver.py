#!/usr/bin/env python
import pexpect
import struct, fcntl, os, sys, signal
import sys
sys.path.append("../")
from drivers.common.clidriver import CLI

class Emulator(CLI):
    # The common functions for emulator included in emulatordriver
    def __init__(self):
        super(CLI, self).__init__()
        