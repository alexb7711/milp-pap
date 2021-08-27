# System Modules
import sys

import gurobipy as gp
import numpy    as np

from gurobipy import GRB

np.set_printoptions(threshold=sys.maxsize)

# Developed Modules
from mat_util import *

##===============================================================================
#
class Optimizer:
    ##===========================================================================
    # PUBLIC

    ##---------------------------------------------------------------------------
    # Input:
    #	A        : A matrix
    #	b        : b vector
    #	x        : x vector
    #	schedule : All schedule variables
    #
    # Output:
    #	Example: test
    #
    def __init__(self, Aeq, Aineq, beq, bineq, xeq, xineq, schedule, mats):
        self.Aeq   = Aeq
        self.Aineq = Aineq
        self.beq   = beq
        self.bineq = bineq
        self.xeq   = xeq
        self.xineq = xineq
        self.s     = schedule
        self.mats  = mats

        return

    ##---------------------------------------------------------------------------
    # Input:
    #
    # Output:
    #
    def optimize(self):
        # Local Variables
        Aeq = self.Aeq
        xeq = self.xeq
        beq = self.beq

        Aineq = self.Aineq
        xineq = self.xineq
        bineq = self.bineq

        # Gurobi Model
        model = self.s["model"]

        # Objective
        w = NQReshape(self.s['N'], self.s['Q'], self.s['w'])
        g = NQReshape(self.s['N'], self.s['Q'], self.s['g'])
        m = self.s['m']
        e = self.s['e']

        model.setObjective(sum((w@m) + (g@e)), GRB.MINIMIZE)

        # Constraints
        ## Equality Constraints
        m,n = Aeq.shape

        ## Update model
        model.update()

        for i in range(m):
            print(sum(Aeq[i,:] * xeq[:]), " == ", beq[i])
            #  input()
            model.addConstr(sum(Aeq[i,:] * xeq[:]) == beq[i], name="eq{0}".format(i))

        ## Inequality Constraints
        m,n = Aineq.shape

        for i in range(m):
            #  print(sum(Aineq[i,:] * xineq[:]), " >= ", bineq[i])
            #  input(i)
            model.addConstr(sum(Aineq[i,:] * xineq[:]) >= bineq[i], name="ineq{0}".format(i))

        # Optimize
        model.optimize()

        return


	##=======================================================================
	# PRIVATE
