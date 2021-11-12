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
	#	Example: test
	#
	# Output:
	#	Example: test
	#
	def __init__(self):
		self.name = "bilinear_linearization"
		return

	##-----------------------------------------------------------------------
	# Input:
	#
	# Output:
	#			NONE
	#
	def constraint(self, model, params, d_var, i, j):
		# Extract parameters
		M = self.params['T']
		Q = self.params['Q']

		# Extract decision vars
		w = self.d_var['w']
		p = self.d_var['p']
		g = self.d_var['g']

		for q in range(Q):
			model.addConstr(g[i][q]                   <= p[i]   , name="{0}_{1}".format(self.name,i  ))
			model.addConstr(g[i][q] + (1 - w[i][q])*M >= p[i]   , name="{0}_{1}".format(self.name,i+1))
			model.addConstr(M*w[i][q]                 >= g[i][q], name="{0}_{1}".format(self.name,i+2))
			model.addConstr(0                         <= g[i][q], name="{0}_{1}".format(self.name,i+3))

		return

