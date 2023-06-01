# System Modules

# Developed Modules
from constraint import Constraint

##===============================================================================
#
class GBTimeBigO(Constraint):
	##=======================================================================
	# PUBLIC

	##-----------------------------------------------------------------------
	# Input:
	#			m     : Gurobi model
	#			params: Model parameters
	#			d_var : Model decision variables
	#			i     : constraint id
	#
	# Output:
	#			NONE
	#
	def constraint(self, model, params, d_var, i, j):
		# Extract parameters
		T = params['T']

		# Extract decision vars
		sigma = self.d_var['sigma']
		p     = self.d_var['p']
		u     = self.d_var['u']

		if i != j:
			model.addConstr(u[i] - u[j] - p[j] - (sigma[i][j] - 1)*T >= 0, \
					name="{0}_{1}_{2}".format(self.name,i,j))
		return
