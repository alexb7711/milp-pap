# System Modules

# Developed Modules
from constraint import Constraint

##===============================================================================
#
class GBValidDepartureTime(Constraint):
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
        t = self.params['t']

        # Extract decision vars
        c = self.d_var['c']

        model.addConstr(c[i] <= t[i], name="{0}_{1}".format(self.name,i))

        return
