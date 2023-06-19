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
for root, dirs, files in os.walk("src/", topdown=False):
    for name in dirs:
        sys.path.append(root+'/'+name)

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Developed
from data_manager import DataManager
from scheduler import Schedule

##===============================================================================
#
class TestScheduleClass(unittest.TestCase):
    ##-------------------------------------------------------------------------------
    #
    def test_schedule_generation_csv(self):
        # Create a schedule
        s = Schedule(None, "./src/config", "./src/data")
        return
