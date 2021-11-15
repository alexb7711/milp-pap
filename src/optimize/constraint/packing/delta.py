# System Modules

# Developed Modules
from constraint import Constraint

##===============================================================================
#
class Delta(Constraint):
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

		# Extract decision vars
		delta = self.d_var['delta']

		if i != j:
			model.addConstr(delta[i][j] + delta[j][i] <= 1, \
											name="{0}_{1}_{2}".format(self.name,i,j))
		return
