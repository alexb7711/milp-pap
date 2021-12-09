# System Modules

# Developed Modules
from constraint import Constraint

##===============================================================================
#
class ValidInitialTime(Constraint):
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
		a = self.params['a']

		# Extract decision vars
		u = self.d_var['u']

		model.addConstr(a[i] - u[i] <= 0 , name="{0}_{1}".format(self.name,i))
		return
