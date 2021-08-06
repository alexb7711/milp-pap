#!/usr/bin/python

# Standard Lib
import gurobipy as gp
import numpy as np
import sys

# Include In Path
sys.path.append("./src/genmat/")
sys.path.append("./src/schedule/")
sys.path.append("./src/util/")

# Developed
from gen_mat          import GenMat
from schedule_manager import Schedule

##===============================================================================
#
def test_A_pack_eq():
    m        = gp.Model("test")
    s        = Schedule(m)
    schedule = s.generate()
    gm       = GenMat(schedule)

    A     = schedule['A']
    N     = schedule['N']
    Q     = schedule['Q']

    # A
    m,n = gm.a_pack_eq.shape
    assert m == 3*N
    assert n == 2*N+N*Q

    # x
    m = gm.x_pack_eq.shape[0]
    print("======")
    print(m)
    assert m == 2*N+N*Q

    # b
    m = gm.b_pack_eq.shape[0]
    assert m == 3*N

    return

##===============================================================================
#
def test_A_dyn_eq():
    m        = gp.Model("test")
    s        = Schedule(m)
    schedule = s.generate()
    gm       = GenMat(schedule)

    A     = schedule['A']
    N     = schedule['N']
    Q     = schedule['Q']

    # A
    m,n = gm.a_dyn_eq.shape
    assert m ==
    assert n ==

    # x
    m = gm.x_dyn_eq.shape[0]
    assert m ==

    # b
    m = gm.b_dyn_eq.shape[0]
    assert m

    return
