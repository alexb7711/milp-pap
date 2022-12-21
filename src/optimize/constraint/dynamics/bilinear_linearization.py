# System Modules

# Developed Modules
from constraint import Constraint

##===============================================================================
#
class BilinearLinearization(Constraint):
	##=======================================================================
	# PUBLIC

	##-----------------------------------------------------------------------
	# Input:
	#
	# Output:
	#			NONE
	#
	def constraint(self, model, params, d_var, i, j):
		# Extract parameters
		M   = self.params['T']
		Q   = self.params['Q']
		gam = self.params['gamma']

		# Extract decision vars
		w = self.d_var['w']
		p = self.d_var['p']
		g = self.d_var['g']

		if gam[i] >= 0:
			for q in range(Q):
				model.addConstr(g[i][q] <= p[i]                   , name="{0}_{1}".format(self.name,i  ))
				model.addConstr(g[i][q] >= p[i] - (1 - w[i][q])*M , name="{0}_{1}".format(self.name,i+1))
				model.addConstr(g[i][q] <= M*w[i][q]              , name="{0}_{1}".format(self.name,i+2))
				model.addConstr(g[i][q] >= 0                      , name="{0}_{1}".format(self.name,i+3))
		return
