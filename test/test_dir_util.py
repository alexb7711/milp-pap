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
import dir_util

##===============================================================================
#
class TestDirUtil(unittest.TestCase):
    ##-------------------------------------------------------------------------------
    #
    def test_dir_exists(self):
        self.assertFalse(dir_util.dir_exists("./dir_not_here"))
        self.assertTrue(dir_util.dir_exists("./src"))
        return

    ##-------------------------------------------------------------------------------
    #
    def test_create_dir(self):
        # Variables
        tmp = "./test/tmp"

        # Create directory
        dir_util.create_dir(tmp)

        # Ensure the tmp dir exists
        self.assertTrue(dir_util.dir_exists(tmp))

        # Delete it
        os.rmdir(tmp)

        # Ensure its gone
        self.assertFalse(dir_util.dir_exists(tmp))
        return
