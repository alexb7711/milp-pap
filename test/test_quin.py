#!/usr/bin/python

# Standard Lib
import sys
import os
import unittest

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Include in path
#
# Recursively include in path:
# https://www.tutorialspoint.com/python/os_walk.htm
for root, dirs, files in os.walk("./src/", topdown=False):
    for name in dirs:
        sys.path.append(root+'/'+name)

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Developed
from quin_modified import QuinModified

##===============================================================================
#
class TestScheduleClass(unittest.TestCase):
    ##-------------------------------------------------------------------------------
    #
    def test_charge_ranges(self):
        return
