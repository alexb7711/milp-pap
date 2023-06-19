#!/usr/bin/python

# Standard Lib
import sys
import unittest

# Include In Path
sys.path.append("./src/util/")

# Developed
from array_util import *

##===============================================================================
#
class TestArrayModule(unittest.TestCase):
    ##-------------------------------------------------------------------------------
    #
    def test_first(self):
        arr = [1,1,2,2,2,3,3,3,4]

        self.assertEqual(first(arr, 1) , 0)
        self.assertEqual(first(arr, 2) , 2)
        self.assertEqual(first(arr, 3) , 5)
        self.assertEqual(first(arr, 4) , 8)

        return

    ##-------------------------------------------------------------------------------
    #
    def test_final(self):
        arr = [1,1,2,2,2,3,3,3,4]

        self.assertEqual(final(arr, 1) , 1)
        self.assertEqual(final(arr, 2) , 4)
        self.assertEqual(final(arr, 3) , 7)
        self.assertEqual(final(arr, 4) , 8)

        return

    ##-------------------------------------------------------------------------------
    #
    def test_adjust(self):
        arr = [1,2,3,4,5,6,7,8,9]
        lb  = 5
        self.assertEqual(adjustArray(lb, arr) , [-1, -1, -1, -1, 4, 5, 6, 7, 8])
        return
