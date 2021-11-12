# System Modules
from abc import ABC, abstractmethod

# Developed Modules

##===============================================================================
#
class Constraint(ABC):
	##=======================================================================
	# PUBLIC

	##-----------------------------------------------------------------------------
	# Input:
	#			Example: test
	#
	# Output:
	#			Example: test
	#
	def __init__(self):
		return

	##-----------------------------------------------------------------------------
	# Input:
	#
	# Output:
	#			Model constraints
	#
	def addConstr(self, i):
		for j in range(self._iterations):
			self.constraint(self.model, self.params, self.d_var, i, j)

	##-----------------------------------------------------------------------------
	# Input:
	#
	# Output:
	#			Model constraints
	#
	@abstractmethod
	def constraint(self):
			return

	##-----------------------------------------------------------------------------
	# Input:
	#			m     : Gurobi model
	#			params: Model parameters
	#			d_var : Model decision variables
	#
	# Output:
	#			Model constraints
	#
	def initialize(self, model, params, d_var):
		self.model  = model
		self.params = params
		self.d_var  = d_var
		return

	##-----------------------------------------------------------------------------
	# Input:
	#			NONE
	#
	# Output:
	#			name: The name of the constraint
	#
	@property
	def name(self):
		return self._name

	##-----------------------------------------------------------------------------
	# Input:
	#			name: The name of the constraint
	#
	# Output:
	#			NONE
	#
	@name.setter
	def name(self, name):
		self._name = name
		return

	##-----------------------------------------------------------------------------
	# Input:
	#			NONE
	#
	# Output:
	#			iterations: Number of times to apply constraint for each iteration
	#
	@property
	def iterations(self):
		return self._iterations

	##-----------------------------------------------------------------------------
	# Input:
	#			iterations: Number of times to apply constraint for each iteration
	#
	# Output:
	#			NONE
	#
	@iterations.setter
	def iterations(self, iterations):
		self._iterations = iterations
		return
	
	##=======================================================================
	# PRIVATE
	_name       = None
	_iterations = 1
