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
		N = self.params['N']
		A = self.params['A']
		S = self.params['S']
		s = self.params['s']

		# Extract decision vars
		delta = self.d_var['delta']
		v     = self.d_var['v']

		if i != j:
			model.addConstr(v[j] - v[i] - s[i] - (delta[i][j] - 1)*S >= 0, \
								      name="{0}_{1}_{2}".format(self.name,i,j))
		return
