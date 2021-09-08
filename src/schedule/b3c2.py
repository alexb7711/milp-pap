# Standard Lib
import gurobipy as gp
import numpy as np
import random

from gurobipy import GRB

def b3c2():
    # Create Gurobi model
    model = gp.Model("2B1C")

    # Input Variables
    A         = 3
    Gamma     = np.array([1,1,1,1],dtype       = int)
    H_final   = 0.98
    H_min     = 0.25
    N         = 4
    Q         = 2
    T         = 7
    dis_rat   = np.array([1, 1],           dtype = float)
    a         = np.array([1, 3, 4, 6],     dtype = float)
    e         = np.array([1],              dtype = float)
    final_arr = np.array([0, 1],           dtype = int)
    gamma     = np.array([1,2,3,-1],       dtype = int)
    kappa     = np.array([0.95],           dtype = float)
    l         = np.array([10, 10, 10, 10], dtype = float)
    m         = np.array([1],              dtype = float)
    r         = np.array([1],              dtype = float)
    t         = np.array([2, 4, 5,6],      dtype = float)
    xi        = np.array([0.95],           dtype = float)

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
    g = model.addMVar(shape=N*Q, vtype=GRB.CONTINUOUS, name="g")

    ## Initial charge
    eta = model.addMVar(shape=N, vtype=GRB.CONTINUOUS, name="eta")

    ## Vector representation of queue
    w = model.addMVar(shape=N*Q, vtype=GRB.CONTINUOUS, name="w")

    ## Sigma
    sigma = model.addMVar(shape=N*(N-1), vtype=GRB.CONTINUOUS, name="sigma")

    ## Delta
    delta = model.addMVar(shape=N*(N-1), vtype=GRB.CONTINUOUS, name="delta")

    schedule = \
            {
                ## Input Variables
                'A'     : A,
                'Gamma' : Gamma,
                'H_f'   : H_final,       # [%]
                'N'     : N,
                'Q'     : Q,
                'S'     : 1,
                'T'     : T,
                'a'     : a,
                'e'     : e,
                'fa'    : final_arr,
                'gamma' : gamma,
                'kappa' : kappa,
                'l'     : l,
                'm'     : m,
                'r'     : r,
                't'     : t,
                'xi'    : xi,

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
