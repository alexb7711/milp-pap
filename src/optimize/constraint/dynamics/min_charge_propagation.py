# System Modules

# Developed Modules
from constraint import Constraint

##===============================================================================
#
class MinChargePropagation(Constraint):
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
		self.name = "min_charge_propagation"
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
		gam   = self.params['gamma']
		l     = self.params['l']
		kappa = self.params['kappa']
		nu    = self.params['nu']
		r     = self.params['r']

		# Extract decision vars
		eta = self.d_var['eta']
		g   = self.d_var['g']

		model.addConstr(eta[i] + sum(g[i][q]*r[q] for q in range(Q)) - l[i] >= nu*kappa[G[i]], \
										name="{0}_{1}".format(self.name,i))

		return
