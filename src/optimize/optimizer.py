# System Modules
import sys

import gurobipy as gp
import numpy    as np
import time

from gurobipy import GRB

np.set_printoptions(threshold=sys.maxsize)

# Developed Modules
from pretty import *

##===============================================================================
#
class Optimizer:
	##===========================================================================
	# PUBLIC

	##---------------------------------------------------------------------------
	# Input:
	#	A        : A matrix
	#	b        : b vector
	#	x        : x vector
	#	schedule : All schedule variables
	#
	# Output:
	#	Example: test
	#
	def __init__(self, model, params, d_var, load_from_file):
		self.model      = model
		self.params     = params
		self.d_var      = d_var
		self.lff        = load_from_file
		self.constr     = []
		self.objective  = []
		self.iterations = 1
		return

	##-----------------------------------------------------------------------------
	# Input:
	#
	# Output:
	#
	def optimize(self):
		if not self.lff:
			# Gurobi Model
			model = self.model

			#  pretty(self.sc)
			#  input("Enter to continue...")

			# Objective
			print("====================================================================")
			print("Creating Objective...")
			print("====================================================================")
			for o in self.objective:
				print("Adding {0}...".format(o.name))
				o.addObjective()
			#  model.setObjective(sum(w[i][j]*m[j] + g[i][j]*e[j] for i in range(N) for j in range(Q)), GRB.MINIMIZE)

			# Add constraints
			print("====================================================================")
			print("Adding Constraints")
			print("====================================================================")

			for i in range(self.iterations):
				t0 = time.time()
				print("Iteration {0}".format(i))

				for c in self.constr: 
					print("Adding {0}...".format(c.name))
					c.addConstr(i)

				t1 = time.time()
				print("----------------------- Speed: {0} seconds -----------------------".format(t1-t0))

			# Uncomment to print model to disk
			#  model.write("model.lp")

			# Optimize
			print("Optimizing...")
			model.optimize()

			# Save Results
			results = \
			{
				## Constants
				"A"     : self.params['A'],
				"N"     : self.params['N'],
				"Q"     : self.params['Q'],
				"T"     : self.params['T'],

				## Input Vars
				"Gamma" : self.params['Gamma'],
				"a"     : self.params['a'],
				"alpha" : self.params['alpha'],
				"beta"  : self.params['beta'],
				"gamma" : self.params['gamma'],
				"l"     : self.params['l'],
				"r"     : self.params['r'],
				"t"     : self.params['t'],

				## Decision Vars
				"c"     : self.d_var['c'].X,
				"delta" : self.d_var['delta'].X,
				"eta"   : self.d_var['eta'].X,
				"p"     : self.d_var['p'].X,
				"sigma" : self.d_var['sigma'].X,
				"u"     : self.d_var['u'].X,
				"v"     : self.d_var['v'].X,
				"w"     : self.d_var['w'].X,
				"g"     : self.d_var['g'].X,
			}

			np.save('results.npy', results)
		else:
			results = np.load("results.npy", allow_pickle='TRUE').item()

		return results
	
	##---------------------------------------------------------------------------
	# Input:
	#			i: Number of iterations to apply constraints
	#
	# Output:
	#			NONE
	#
	def setIterations(self,i):
		self.iterations = i
		return

	##---------------------------------------------------------------------------
	# Input:
	#			constr: Constraint object
	#
	# Output:
	#			NONE
	#
	def subscribeConstraint(self, constr):
		self.constr.append(constr)
		return
	
	##---------------------------------------------------------------------------
	# Input:
	#			objective: Objective object
	#
	# Output:
	#			NONE
	#
	def subscribeObjective(self, objective):
		self.objective.append(objective)
		return
