# System Modules

# Developed Modules
from constraint import Constraint

##===============================================================================
#
class FinalCharge(Constraint):
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
		self.name = "final_charge"
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
		beta  = self.params['beta']
		kappa = self.params['kappa']

		# Extract decision vars
		eta = self.d_var['eta']
		g   = self.d_var['g']

		if beta[i] > 0:
			model.addConstr(eta[i] >= beta[i]*kappa[G[i]], \
											name="{0}_{1}".format(i,self.name))

		return
