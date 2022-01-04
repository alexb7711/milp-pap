# System Modules
from gurobipy import GRB

# Developed Modules
from objective import Objective

##===============================================================================
#
class MinPowerObjective(Objective):
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
        N  = params['N']
        Q  = params['Q']
        T  = params['T']
        K  = params['K']
        r  = params['r']
        dt = params['dt']

        # Extract decision vars
        psi = self.d_var['psi']
        w   = self.d_var['w']
        xi  = self.d_var['xi']

        model.setObjectiveN(sum(50*r[q]*(1-w[i][j]) *
                           (1 - (xi[i][j][k] + psi[i][j][k] - xi[i][j][k]*psi[i][j][k]))
                            for i in range(N)
                            for q in range(Q)
                            for k in range(0,T,K)), GRB.MINIMIZE)
        return

