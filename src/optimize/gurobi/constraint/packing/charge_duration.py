# System Modules

# Developed Modules
from constraint import Constraint

##===============================================================================
#
class ChargeDuration(Constraint):
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
        # Extract decision vars
        c = self.d_var['c'] # Final charge time
        u = self.d_var['u'] # Initial charge time
        p = self.d_var['p'] # Charge duration

        model.addConstr(p[i] == c[i] - u[i], name="{0}_{1}".format(self.name,i))
        return
