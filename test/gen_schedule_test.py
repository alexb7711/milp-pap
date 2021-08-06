#!/usr/bin/python

# Standard Lib
import gurobipy as gp
import numpy as np
import sys

# Include In Path
sys.path.append("./src/schedule/")
sys.path.append("./src/util/")

# Developed
from schedule_manager import Schedule

##===============================================================================
#
def test_gen_dims():
    m        = gp.Model("test")
    s        = Schedule(m)
    schedule = s.generate()

    # Initialize member variables
    ## Input Variables
    A     = schedule['A']
    G_idx = schedule['Gamma']
    N     = schedule['N']
    Q     = schedule['Q']
    e     = schedule['e']
    eta   = schedule['eta']
    g_idx = schedule['gamma']
    l     = schedule['l']
    t     = schedule['t']
    r     = schedule['r']

    ## Decision Variables
    a     = schedule['a']
    c     = schedule['c']
    delta = schedule['delta']
    eta   = schedule['eta']
    g     = schedule['g']
    p     = schedule['p']
    sigma = schedule['sigma']
    u     = schedule['u']
    v     = schedule['v']
    w     = schedule['w']

    # Tests
    assert G_idx.shape[0] == N
    assert a.shape[0]     == N
    assert c.shape[0]     == N
    assert delta.shape[0] == N*A
    assert e.shape[0]     == Q
    assert eta.shape[0]   == N-A
    assert g.shape[0]     == N*Q
    assert g_idx.shape[0] == N
    assert l.shape[0]     == N
    assert p.shape[0]     == N
    assert r.shape[0]     == Q
    assert sigma.shape[0] == N*A
    assert t.shape[0]     == N
    assert u.shape[0]     == N
    assert v.shape[0]     == N
    assert w.shape[0]     == N*Q

    return
