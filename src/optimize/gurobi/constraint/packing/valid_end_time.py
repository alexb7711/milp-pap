# System Modules

# Developed Modules
from constraint import Constraint

##===============================================================================
#
class ValidEndTime(Constraint):
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
    def constraint(self, model, params, d_var, i, j):
        # Extract parameters
        T = self.params['T']

        # Extract decision vars
        p = self.d_var['p']
        u = self.d_var['u']

        model.addConstr(u[i] <= T-p[i], name="{0}_{1}".format(self.name,i))
        return
