# System Modules

# Developed Modules
from constraint import Constraint

##===============================================================================
#
class ValidQueueVector(Constraint):
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
		self.name = "valid_queue_vector"
		return

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
		w = self.d_var['w']

		model.addConstr(sum(w[i][q] for q in range(Q)) == 1, \
									  name="{0}_{1}".format(self.name,i))

		return
