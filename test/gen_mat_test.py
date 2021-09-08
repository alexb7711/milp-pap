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

    gm.genMats()

    # A
    m,n = gm.A_pack_eq.shape
    assert m == 2*N
    assert n == 2*N+N*Q

    # x
    m = gm.x_pack_eq.shape[0]
    assert m == 2*N+N*Q

    # b
    m = gm.b_pack_eq.shape[0]
    assert m == 2*N

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

    gm.genMats()

    # A
    m,n = gm.A_dyn_eq.shape
    assert m == 2*N
    assert n == 2*N + N*Q

    # x
    m = gm.x_dyn_eq.shape[0]
    assert m == 2*N + N*Q

    # b
    m = gm.b_dyn_eq.shape[0]
    assert m == 2*N

    return

##===============================================================================
#
def test_A_pack_ineq():
    m        = gp.Model("test")
    s        = Schedule(m)
    schedule = s.generate()
    gm       = GenMat(schedule)

    A   = schedule['A']
    N   = schedule['N']
    Q   = schedule['Q']
    Xi  = N*(N-1)
    Psi = int(Xi/2)

    gm.genMats()

    # A
    m,n = gm.A_pack_ineq.shape
    assert m == 2*Xi + 7*N + 3*Psi
    assert n == 4*Xi + 6*N + 3*N*Q

    # x
    m = gm.x_pack_ineq.shape[0]
    assert m == 4*Xi + 6*N + 3*N*Q

    # b
    m = gm.b_pack_ineq.shape[0]
    assert m == 2*Xi + 7*N + 3*Psi

    return

##===============================================================================
#
def test_A_dyn_ineq():
    m        = gp.Model("test")
    s        = Schedule(m)
    schedule = s.generate()
    gm       = GenMat(schedule)

    A     = schedule['A']
    N     = schedule['N']
    Q     = schedule['Q']

    gm.genMats()

    # A
    m,n = gm.A_dyn_ineq.shape
    assert m == 3*N
    assert n == 2*N+N*Q

    # x
    m = gm.x_dyn_ineq.shape[0]
    assert m == 2*N + N*Q

    # b
    m = gm.b_dyn_ineq.shape[0]
    assert m == 3*N

    return

##===============================================================================
#
def test_A_eq():
    m        = gp.Model("test")
    s        = Schedule(m)
    schedule = s.generate()
    gm       = GenMat(schedule)

    A     = schedule['A']
    N     = schedule['N']
    Q     = schedule['Q']

    gm.genMats()

    # A
    m,n = gm.A_eq.shape
    assert m == 4*N
    assert n == 4*N + 2*N*Q

    # x
    m = gm.x_eq.shape[0]
    assert m == 4*N + 2*N*Q

    # b
    m = gm.b_eq.shape[0]
    assert m == 4*N

    return

##===============================================================================
#
def test_A_ineq():
    m        = gp.Model("test")
    s        = Schedule(m)
    schedule = s.generate()
    gm       = GenMat(schedule)

    A   = schedule['A']
    N   = schedule['N']
    Q   = schedule['Q']
    Xi  = N*(N-1)
    Psi = int(Xi/2)

    gm.genMats()

    # A
    m,n = gm.A_ineq.shape
    assert m == 2*Xi + 10*N + 3*Psi
    assert n == 4*Xi + 8*N + 4*N*Q

    # x
    m = gm.x_ineq.shape[0]
    assert m == 4*Xi + 8*N + 4*N*Q

    # b
    m = gm.b_ineq.shape[0]
    assert m == 2*Xi + 10*N + 3*Psi

    return
