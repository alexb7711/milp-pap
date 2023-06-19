#!/usr/bin/python

# Standard Lib
import sys
import unittest

# Include In Path
sys.path.append("./src/schedule/")
sys.path.append("./src/util/")

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
