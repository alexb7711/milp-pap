# System Modules
from gurobipy import GRB

# Developed Modules
from objective import Objective

##===============================================================================
#
class MinPowerUsage(Objective):
    ##=======================================================================
    # PUBLIC

    ##-----------------------------------------------------------------------
    # Input:
    #           m     : Gurobi model
    #           params: Model parameters
    #           d_var : Model decision variables
    #           i     : constraint id
    #
    # Output:
    #           NONE
    #
    def objective(self, model, params, d_var):
        # Extract parameters
        N = params['N']
        Q = params['Q']
        e = params['e']
        m = params['m']

        # Extract decision vars
        g = self.d_var['g']
        w = self.d_var['w']

        model.setObjectiveN(sum(w[i][j]*m[j] + g[i][j]*e[j] for i in range(N) for j in range(Q)), GRB.MINIMIZE)
        return

