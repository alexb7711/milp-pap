# System Modules

# Developed Modules
from constraint import Constraint

##===============================================================================
#
class SpaceBigO(Constraint):
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
        model.update()
        # Extract parameters
        Q = self.params['Q']
        s = self.params['s']

        # Extract decision vars
        delta = self.d_var['delta']
        v     = self.d_var['v']

        if i != j:
            model.addConstr(v[i] - v[j] - s[j] - (delta[i][j] - 1)*Q >= 0, \
                                      name="{0}_{1}_{2}".format(self.name,i,j))
        return
