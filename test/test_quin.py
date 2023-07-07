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
from data_manager  import DataManager
from scheduler     import Schedule
from quin_modified import QuinModified

##===============================================================================
#
class TestQuinnModified(unittest.TestCase):
    ##-------------------------------------------------------------------------------
    #
    def test_charge_ranges(self):
        # Create data manager object
        dm = DataManager()

        # Create a schedule
        s = Schedule(None, "./src/config", "./data")

        # Create Quinn Modified instance
        qm = QuinModified("./src/config")

        # Optimize
        r = qm.optimize()

        # Check the bounds
        for eta in dm['eta']:
            self.assertLessEqual(eta, dm['kappa'][0], "The charge is larger than the battery capacity.")
            self.assertGreaterEqual(eta, 0, "The charge is negative.")
        return
