#!/usr/bin/python

# Standard Lib
import sys

# Include In Path
sys.path.append("./src/util/")

# Developed
from mat_util import *

##===============================================================================
#
def test_NQMat():
    N = 3
    Q = 1
    t = int
    assert NQMat(N,Q,t).tolist() == [[1,0,0],
                                     [0,1,0],
                                     [0,0,1]]

    N    = 3
    Q    = 2
    t    = int
    vals = [1,3]
    assert NQMat(N,Q,t).tolist()      == [[1,2,0,0,0,0],
                                          [0,0,1,2,0,0],
                                          [0,0,0,0,1,2]]
    assert NQMat(N,Q,t,vals).tolist() == [[1,3,0,0,0,0],
                                          [0,0,1,3,0,0],
                                          [0,0,0,0,1,3]]

    return
