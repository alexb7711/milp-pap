# Standard Lib
import gurobipy as gp
import numpy as np
import random

from gurobipy import GRB

def b2c1():
    # Create Gurobi model
    model = gp.Model("2B1C")

    # Input Variables
    A         = 2
    Gamma     = np.array([0,1,0],         dtype = int)
    beta      = 0.98
    H_min     = 0.25
    N         = 3
    Q         = 1
    T         = 5
    dis_rat   = np.array([1, 1],          dtype = float)
    a         = np.array([1, 3, 4],       dtype = float)
    e         = np.array([1],             dtype = float)
    final_arr = np.array([2, 1],          dtype = int)
    gamma     = np.array([2, -1, -1],     dtype = int)
    alpha     = np.array([0.95, 0.95],    dtype = float)
    l         = np.array([10, 10, 10],    dtype = float)
    m         = np.array([1],             dtype = float)
    r         = np.array([2],             dtype = float)
    t         = np.array([2, 4, 5],       dtype = float)

    # Input Variables
    ## Initial charge time
    u = model.addMVar(shape=N, vtype=GRB.CONTINUOUS, name="u")

    ## Assigned queue
    v = model.addMVar(shape=N, vtype=GRB.CONTINUOUS, name="v")

    ## Detatch timodel.
    c = model.addMVar(shape=N, vtype=GRB.CONTINUOUS, name="c")

    ## Charge timodel.
    p = model.addMVar(shape=N, vtype=GRB.CONTINUOUS, name="p")

    ## Lineriztion term
    g = model.addMVar(shape=(N,Q), vtype=GRB.CONTINUOUS, name="g")

    ## Initial charge
    eta = model.addMVar(shape=N, vtype=GRB.CONTINUOUS, name="eta")

    ## Vector representation of queue
    w = model.addMVar(shape=(N,Q), vtype=GRB.BINARY, name="w")

    ## Sigma
    sigma = model.addMVar(shape=(N,N), vtype=GRB.BINARY, name="sigma")

    ## Delta
    delta = model.addMVar(shape=(N,N), vtype=GRB.BINARY, name="delta")

    schedule = \
            {
                ## Input Variables
                'A'     : A,
                'Gamma' : Gamma,
                'beta'  : beta,       # [%]
                'N'     : N,
                'Q'     : Q,
                'S'     : 1.0,
                'T'     : T,
                'a'     : a,
                'e'     : e,
                'fa'    : final_arr,
                'gamma' : gamma,
                'alpha' : alpha,
                'l'     : l,
                'm'     : m,
                'r'     : r,
                's'     : np.ones(N),
                't'     : t,

                ## Decision Variables
                'c'     : c,
                'delta' : delta,
                'eta'   : eta,
                'g'     : g,
                'p'     : p,
                'sigma' : sigma,
                'u'     : u,
                'v'     : v,
                'w'     : w,

                # Model
                'model' : model,
            }

    return schedule