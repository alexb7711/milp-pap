#!/usr/bin/python

# Standard Lib
import sys

# Include In Path
sys.path.append("./src/util/")

# Developed
from array_util import *

##===============================================================================
#
def test_first():
    arr = [1,1,2,2,2,3,3,3,4]

    assert first(arr, 1) == 0
    assert first(arr, 2) == 2
    assert first(arr, 3) == 5
    assert first(arr, 4) == 8

    return

##===============================================================================
#
def test_final():
    arr = [1,1,2,2,2,3,3,3,4]

    assert final(arr, 1) == 1
    assert final(arr, 2) == 4
    assert final(arr, 3) == 7
    assert final(arr, 4) == 8

    return

##===============================================================================
#
def test_adjust():
    arr = [1,2,3,4,5,6,7,8,9]
    lb  = 5
    print(adjustArray(lb,arr))
    assert adjustArray(lb, arr) == [-1, -1, -1, -1, 0, 1, 2, 3, 4]
    return
