# System Modules
import sys

import gurobipy as gp
import numpy    as np

from gurobipy import GRB

np.set_printoptions(threshold=sys.maxsize)

# Developed Modules
from mat_util import *
from pretty import *

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
    def __init__(self, schedule, load_from_file):
        self.sc  = schedule
        self.lff = load_from_file
        return

    ##---------------------------------------------------------------------------
    # Input:
    #
    # Output:
    #
    def optimize(self):
        if not self.lff:
            # Local Variables
            ## Constants
            A = self.sc["A"]
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

            pretty(self.sc)
            input("Enter to continue...")

            # Objective
            print("Creating Objective...")
            model.setObjective(sum(w[i][j]*m[j] + g[i][j]*e[j] for i in range(N) for j in range(Q)), GRB.MINIMIZE)

            # Add constraints
            print("Adding Constraints...")

            ## Loop through each vehicle
            const_id  = 0

            for i in range(N+A):
                # Pack Constraints
                ## Equality Constraints
                #  model.addConstr(sum(g[i][q] for q in range(Q)) + u[i] == c[i]  , name="{6}")
                model.addConstr(p[i] + u[i] == c[i]  , name="{6}")

                ## Inequality Constraints
                for j in range(N+A):
                    if i != j:
                        model.addConstr(u[j] - u[i] - p[i] - (sigma[i][j] - 1)*T              >= 0     , name="{0}_1".format(i))
                        model.addConstr(v[j] - v[i] - s[i] - (delta[i][j] - 1)*S              >= 0     , name="{0}_2".format(i))
                        model.addConstr(sigma[i][j] + sigma[j][i] + delta[i][j] + delta[j][i] >= 1     , name="{0}_3".format(i))
                        model.addConstr(sigma[i][j] + sigma[j][i]                             <= 1     , name="{0}_4".format(i))
                        model.addConstr(delta[i][j] + delta[j][i]                             <= 1     , name="{0}_5".format(i))
                    else:
                        model.addConstr(sigma[i][j] + sigma[j][i] + delta[i][j] + delta[j][i] == 0     , name="{0}_4".format(i))
                        model.addConstr(sigma[i][j] + sigma[j][i]                             == 0     , name="{0}_5".format(i))
                        model.addConstr(delta[i][j] + delta[j][i]                             == 0     , name="{0}_6".format(i))

                model.addConstr(a[i] <= u[i]  , name="{0}_8".format(i))
                model.addConstr(u[i] <= T-p[i], name="{0}_9".format(i))

                if t[i] > 0:
                    model.addConstr(c[i] <= t[i], name="{0}_10".format(i))

                # Dynamic Constraints
                ## Equality Constraints
                if alpha[i] > 0:
                    model.addConstr(alpha[i]*kappa[G[i]] == eta[i] , name="{0}_11".format(i))

                model.addConstr(v[i]                           == sum((q+1)*w[i][q] for q in range(Q)) , name="{0}_12".format(i))
                model.addConstr(sum(w[i][q] for q in range(Q)) == 1                                    , name="{0}_13".format(i))

                if gam[i] > 0:
                    model.addConstr(eta[i] + sum(g[i][q]*r[q] for q in range(Q)) - l[i] == eta[gam[i]] , name="{0}_14".format(i))

                    for q in range(Q):
                        model.addConstr(g[i][q]                   <= p[i]    , name="{0}_{1}_16".format(i , q))
                        model.addConstr(g[i][q] + (1 - w[i][q])*M >= p[i]    , name="{0}_{1}_17".format(i , q))
                        model.addConstr(M*w[i][q]                 >= g[i][q] , name="{0}_{1}_18".format(i , q))
                        model.addConstr(0                         <= g[i][q] , name="{0}_{1}_19".format(i , q))

                ## Inequality Constraints
                model.addConstr(eta[i] + sum(g[i][q]*r[q] for q in range(Q))          <= kappa[G[i]]    , name="{0}_15".format(i))
                model.addConstr(eta[i] + sum(g[i][q]*r[q] for q in range(Q)) - l[i]   >= nu*kappa[G[i]] , name="{0}_16".format(i))

                if beta[i] > 0:
                    model.addConstr(eta[i] >= beta[i]*kappa[G[i]], name="{0}_21".format(i))

                const_id += 1

            # Uncomment to print model to disk
            #  model.write("model.lp")

            # Optimize
            print("Optimizing...")
            model.optimize()

            # Save Results
            results = \
            {
                ## Constants
                "A"     : A,
                "N"     : N,
                "Q"     : Q,
                "T"     : T,

                ## Input Vars
                "Gamma" : G,
                "a"     : a,
                "alpha" : alpha,
                "beta"  : beta,
                "gamma" : gam,
                "l"     : l,
                "r"     : r,
                "t"     : t,

                ## Decision Vars
                "c"     : c.X,
                "delta" : delta.X,
                "eta"   : eta.X,
                "p"     : p.X,
                "sigma" : sigma.X,
                "u"     : u.X,
                "v"     : v.X,
                "w"     : w.X,
                "g"     : g.X,
            }


            np.save('results.npy', results)
        else:
            results = np.load("results.npy", allow_pickle='TRUE').item()

        return results

