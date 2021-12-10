# System Modules

# Developed Modules
from constraint import Constraint

##===============================================================================
#
class BilinearDiscretePower(Constraint):
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
        T  = self.params['T']
        K  = self.params['K']
        tk = self.params['tk']

        # Extract decision vars
        xi  = self.d_var['xi']
        w   = self.d_var['w']
        rho = self.d_var['rho']

        for k in range(0, T, K):
            self.model.addConstr(rho[i][j][k] - xi[i][j][k] <= 0               , name="{0}_{1}_{2}_{3}".format(self.name , i , j , k))
            self.model.addConstr(rho[i][j][k] - w[i][j]     <= 0               , name="{0}_{1}_{2}_{3}".format(self.name , i , j , k))
            self.model.addConstr(rho[i][j][k] - w[i][j] - xi[i][j][k] + 1 >= 0 , name="{0}_{1}_{2}_{3}".format(self.name , i , j , k))

        return
