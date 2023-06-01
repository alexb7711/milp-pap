# System Modules

# Developed Modules
from constraint import Constraint

##===============================================================================
#
class GBChargePropagation(Constraint):
        ##=======================================================================
        # PUBLIC

        ##-----------------------------------------------------------------------
        # Input:
        #                       m     : Gurobi model
        #                       params: Model parameters
        #                       d_var : Model decision variables
        #                       i     : constraint id
        #
        # Output:
        #                       NONE
        #
        def constraint(self, model, params, d_var, i, j):
                # Extract parameters
                Q   = self.params['Q']
                gam = self.params['gamma']
                r   = self.params['r']
                l   = self.params['l']

                # Extract decision vars
                eta = self.d_var['eta']
                g   = self.d_var['g']

                if gam[i] >= 0:
                        model.addConstr(eta[i] + sum(g[i][q]*r[q] for q in range(Q)) - l[i] == eta[gam[i]], \
                                                                                  name="{0}_{1}".format(self.name,i))

                return
