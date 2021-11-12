# System Modules

# Developed Modules
from constraint import Constraint

##===============================================================================
#
class MaxChargePropagation(Constraint):
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
		self.name = "max_charge_propagation"
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
		G     = self.params['Gamma']
		Q     = self.params['Q']
		kappa = self.params['kappa']
		r     = self.params['r']

		# Extract decision vars
		eta = self.d_var['eta']
		g   = self.d_var['g']

		model.addConstr(eta[i] + sum(g[i][q]*r[q] for q in range(Q)) <= kappa[G[i]], \
										name="{0}_{1}".format(self.name,i))

		return
