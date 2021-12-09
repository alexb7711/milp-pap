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
        K  = params['K']
        r  = params['r']
        dt = params['dt']

        # Extract decision vars
        xi  = self.d_var['xi']
        rho = self.d_var['rho']

        model.setObjectiveN(sum(dt*r[q]*rho[i][q][k] + (1-xi[i][q][k])
                                for i in range(N)
                                for q in range(Q)
                                for k in range(K)), GRB.MINIMIZE)
        return

