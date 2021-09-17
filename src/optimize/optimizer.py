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
    def __init__(self, schedule):
        self.sc     = schedule
        return

    ##---------------------------------------------------------------------------
    # Input:
    #
    # Output:
    #
    def optimize(self):
        # Local Variables
        ## Constants
        M = self.sc["T"]
        N = self.sc["N"]
        Q = self.sc["Q"]
        S = self.sc["S"]
        T = self.sc["T"]

        # Input Vars
        G     = self.sc["Gamma"]
        nu    = self.sc["nu"]
        a     = self.sc["a"]
        alpha = self.sc["alpha"]
        beta  = self.sc["beta"]
        e     = self.sc['e']
        gam   = self.sc["gamma"]
        kappa = self.sc["kappa"]
        l     = self.sc["l"]
        m     = self.sc['m']
        r     = self.sc["r"]
        s     = self.sc["s"]
        t     = self.sc["t"]

        ## Decision Variables
        c     = self.sc["c"]
        delta = self.sc["delta"]
        eta   = self.sc['eta']
        g     = self.sc['g']
        p     = self.sc["p"]
        sigma = self.sc["sigma"]
        u     = self.sc["u"]
        v     = self.sc["v"]
        w     = self.sc['w']

        # Gurobi Model
        model = self.sc["model"]

        # Objective
        print("Creating Objective...")
        model.setObjective(sum(w[i][j]*m[j] + g[i][j]*e[j] for i in range(N) for j in range(Q)), GRB.MINIMIZE)

        # Add constraints
        print("Adding Constraints...")

        ## Loop through each vehicle
        const_id  = 0

        for i in range(N):
            # Pack Constraints
            ## Equality Constraints
            model.addConstr(sum(g[i][q] for q in range(Q)) + u[i] == c[i]  , name="{6}")

            ## Inequality Constraints
            for j in range(N):
                if i != j:
                    model.addConstr(u[j] - u[i] - p[i] - (sigma[i][j] - 1)*T              >= 0     , name="{0}_1".format(i))
                    model.addConstr(v[j] - v[i] - s[i] - (delta[i][j] - 1)*S              >= 0     , name="{0}_2".format(i))
                    model.addConstr(sigma[i][j] + sigma[j][i] + delta[i][j] + delta[j][i] >= 1     , name="{0}_3".format(i))
                    model.addConstr(sigma[i][j] + sigma[j][i]                             <= 1     , name="{0}_4".format(i))
                    model.addConstr(delta[i][j] + delta[j][i]                             <= 1     , name="{0}_5".format(i))
                else:
                    model.addConstr(sigma[i][j] + sigma[j][i] + delta[i][j] + delta[j][i] >= 0     , name="{0}_4".format(i))
                    model.addConstr(sigma[i][j] + sigma[j][i]                             <= 0     , name="{0}_5".format(i))
                    model.addConstr(delta[i][j] + delta[j][i]                             <= 0     , name="{0}_6".format(i))

            model.addConstr(a[i] <= u[i]  , name="{0}_8".format(i))
            model.addConstr(u[i] <= T-p[i], name="{0}_9".format(i))

            if t[i] > 0:
                model.addConstr(c[i] <= t[i], name="{0}_10".format(i))

            # Dynamic Constraints
            ## Equality Constraints
            if alpha[i] > 0:
                model.addConstr(alpha[i]*kappa[i] == eta[i] , name="{0}_11".format(i))

            model.addConstr(sum((q+1)*w[i][q] for q in range(Q))   == v[i] , name="{0}_12".format(i))
            model.addConstr(sum(w[i][q] for q in range(Q))         == 1    , name="{0}_13".format(i))

            if gam[i] > 0:
                model.addConstr(eta[i] + sum(g[i][q]*r[q] for q in range(Q)) - l[i] == eta[gam[i]] , name="{0}_14".format(i))

            # Inequality Constraints
            if alpha[i] > 0:
                model.addConstr(eta[i] + sum(g[i][q]*r[q] for q in range(Q))          <= kappa[G[i]]    , name="{0}_15".format(i))
                model.addConstr(eta[i] + sum(g[i][q]*r[q] for q in range(Q)) - l[i]   >= nu*kappa[G[i]] , name="{0}_16".format(i))

            for q in range(Q):
                model.addConstr(g[i][q]                        <= p[i]                    , name="{0}_{1}_16".format(i , q))
                model.addConstr(g[i][q] + (1 - w[i][q])*M      >= p[i]                    , name="{0}_{1}_17".format(i , q))
                model.addConstr(M*w[i][q]                      >= g[i][q]                 , name="{0}_{1}_18".format(i , q))
                model.addConstr(0                              <= g[i][q]                 , name="{0}_{1}_19".format(i , q))

            const_id += 1

        # Uncomment to print model to disk
        #  model.write("model.lp")

        # Optimize
        print("Optimizing...")
        model.optimize()

        # Print Solution
        print("Printing Input...")
        print("a     :\n", a)
        print("t     :\n", t)
        print("Gamma :\n", G)
        print("gamma :\n", gam)

        print("Printing Solution...")
        print("c     :\n", c.X)
        print("delta :\n", delta.X)
        print("eta :\n"  , eta.X)
        print("p     :\n", p.X)
        print("sigma :\n", sigma.X)
        print("u     :\n", u.X)
        print("v     :\n", v.X)
        print("w     :\n", w.X)
        print("g     :\n", g.X)

        return
