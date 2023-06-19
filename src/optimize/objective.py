# System Modules
from abc import ABC, abstractmethod

# Developed Modules

##===============================================================================
#
class Objective(ABC):
	##=======================================================================
	# PUBLIC

	##-----------------------------------------------------------------------------
	# Input:
	#			Example: test
	#
	# Output:
	#			Example: test
	#
	def __init__(self, name):
		self._name = name
		return

	##-----------------------------------------------------------------------------
	# Input:
	#
	# Output:
	#			Model constraints
	#
	def addObjective(self):
		self.objective(self.model, self.params, self.d_var)

	##-----------------------------------------------------------------------------
	# Input:
	#
	# Output:
	#			Model constraints
	#
	@abstractmethod
	def objective(self):
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

	##=======================================================================
	# PRIVATE
	_name       = None

