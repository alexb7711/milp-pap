# System Modules

# Developed Modules
from constraint import Constraint

##===============================================================================
#
class DiscretePowerUsage(Constraint):
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
        tk = self.params['tk']

        # Extract decision vars
        c  = self.d_var['c']
        u  = self.d_var['u']
        xi = self.d_var['xi']

        for k in range(0,len(tk)):
            self.model.addConstr(u[i] - tk[k] <= T*xi[i][j][k] , name="{0}_{1}_{2}_{3}".format(self.name , i , j , k))
            self.model.addConstr(tk[k] - c[i] <= T*xi[i][j][k] , name="{0}_{1}_{2}_{3}".format(self.name , i , j , k))
            self.model.addConstr(T*(1-xi[i][j][k])  <= 0       , name="{0}_{1}_{2}_{3}".format(self.name , i , j , k))
            self.model.addConstr(T*(1-xi[i][j][k])  <= 0       , name="{0}_{1}_{2}_{3}".format(self.name , i , j , k))

        return
