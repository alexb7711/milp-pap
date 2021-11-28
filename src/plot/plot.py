# System Modules
import matplotlib.pyplot as plt
import numpy             as np

from abc import ABC, abstractmethod

# Developed Modules

##===============================================================================
#
class Plotter:
	##=============================================================================
	# PUBLIC
	
	##-----------------------------------------------------------------------------
	# Static Variables

	# Constants
	A     = 0
	N     = 0
	Q     = 0
	T     = 0

	# Input Vars
	a     = []
	r     = []
	t     = 0
	Gamma = []
	gamma = []

	# Decision Vars
	c     = []
	delta = []
	eta   = []
	p     = []
	sigma = []
	u     = []
	v     = []
	w     = []

	##-----------------------------------------------------------------------------
	# Input:
	#	Example: test
	#
	# Output:
	#	Example: test
	#
	def __init__(self, name):
		self.name = name
		return
	
	##-----------------------------------------------------------------------------
	# Input:
	#			params: Model parameters
	#			d_var : Model decision variable results
	#
	# Output:
	#			NONE
	#
	def initialize(results):

		# Constants
		Plotter.A     = results['A']
		Plotter.N     = results['N']
		Plotter.Q     = results['Q']
		Plotter.T     = results['T']

		# Input Vars
		Plotter.a     = results['a']
		Plotter.r     = results['r']
		Plotter.t     = results['t']
		Plotter.Gamma = results['Gamma']
		Plotter.gamma = results['gamma']

		# Decision Vars
		Plotter.c     = results['c']
		Plotter.delta = results['delta']
		Plotter.eta   = results['eta']
		Plotter.p     = results['p']
		Plotter.sigma = results['sigma']
		Plotter.u     = results['u']
		Plotter.v     = results['v']
		Plotter.w     = results['w']

		return

	##-----------------------------------------------------------------------------
	# Input:
	#			data: Data to be utilized to plot
	#
	# Output:
	#			NONE
	#
	@abstractmethod
	def plot(self, data):
		Plot.data = data
		return
	
	##-----------------------------------------------------------------------------
	# Input:
	#			NONE
	#
	# Output:
	#			NONE
	#
	@abstractmethod
	def plot(self):
		return
	
	##-----------------------------------------------------------------------------
	# Input:
	#			NONE
	#
	# Output:
	#			name: The name of the plot
	#
	@property
	def name(self):
		return self._name

	##-----------------------------------------------------------------------------
	# Input:
	#			name: The name of the plot
	#
	# Output:
	#			NONE
	#
	@name.setter
	def name(self, name):
		self._name = name
		return
