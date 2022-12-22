# System Modules

# Developed Modules
from constraint import Constraint

##===============================================================================
#
class ScalarToVectorQueue(Constraint):
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
		Q = self.params['Q']

		# Extract decision vars
		v = self.d_var['v']
		w = self.d_var['w']

		model.addConstr(v[i] == sum(q*w[i][q] for q in range(Q)), name="{0}_{1}".format(self.name,i))

		return
