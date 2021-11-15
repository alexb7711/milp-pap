# System Modules

# Developed Modules
from constraint import Constraint

##===============================================================================
#
class InitialCharge(Constraint):
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
		G     = self.params['Gamma']
		alpha = self.params['alpha']
		kappa = self.params['kappa']

		# Extract decision vars
		eta = self.d_var['eta']

		if alpha[i] > 0:
			model.addConstr(alpha[i]*kappa[G[i]] == eta[i], \
							        name="{0}_{1}".format(self.name, i))

		return
