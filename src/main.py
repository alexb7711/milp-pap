#!/usr/bin/python

# Standard Lib
import gurobipy as gp
import sys

from gurobipy import GRB

# Include in path
sys.path.append("optimize/")
sys.path.append("optimize/constraint/")
sys.path.append("optimize/constraint/dynamics/")
sys.path.append("optimize/constraint/packing/")
sys.path.append("optimize/objective/")
sys.path.append("schedule/generate/")
sys.path.append("schedule/load/")
sys.path.append("util/")

# Developed
from schedule_manager import Schedule
from optimizer        import Optimizer
from plot             import Plotter

# Constraints
## Packing
from charge_duration      import ChargeDuration
from delta                import Delta
from sigma                import Sigma
from sigma_delta          import SigmaDelta
from space_big_o          import SpaceBigO
from time_big_o           import TimeBigO
from valid_departure_time import ValidDepartureTime
from valid_end_time       import ValidEndTime
from valid_initial_time   import ValidInitialTime

## Dynamic
from bilinear_linearization import BilinearLinearization
from charge_propagation     import ChargePropagation
from final_charge           import FinalCharge
from initial_charge         import InitialCharge
from max_charge_propagation import MaxChargePropagation
from min_charge_propagation import MinChargePropagation
from scalar_to_vector_queue import ScalarToVectorQueue
from valid_queue_vector     import ValidQueueVector

## Static schedules
from b2c1          import *
from b3c2          import *
from yaml_schedule import YAMLSchedule

##===============================================================================
#
def initialize(constraints, model, params, d_var):
	for c in constraints:
		c.initialize(model, params, d_var)
	return

##===============================================================================
#
def subscribe(constraints, optimizer_obj):
	for c in constraints:
		optimizer_obj.subscribeConstraint(c)
	return

##===============================================================================
#
def schedule2PAndD(schedule):
	params = \
	{
		'A'     : schedule['A'],
		'Gamma' : schedule['Gamma'],
		'N'     : schedule['N'],
		'Q'     : schedule['Q'],
		'S'     : schedule['Q'],
		'T'     : schedule['T'],
		'a'     : schedule['a'],
		'alpha' : schedule['alpha'],
		'beta'  : schedule['beta'],       # [%]
		'e'     : schedule['e'],
		'gamma' : schedule['gamma'],
		'kappa' : schedule['kappa'],
		'l'     : schedule['l'],
		'm'     : schedule['m'],
		'nu'    : schedule['nu'],
		'r'     : schedule['r'],
		's'     : np.ones(schedule['N']*schedule['A'],dtype=int),
		't'     : schedule['t'],
	}

	d_var = \
	{
		'c'     : schedule['c'],
		'delta' : schedule['delta'],
		'eta'   : schedule['eta'],
		'g'     : schedule['g'],
		'p'     : schedule['p'],
		'sigma' : schedule['sigma'],
		'u'     : schedule['u'],
		'v'     : schedule['v'],
		'w'     : schedule['w'],
	}

	return params, d_var

##===============================================================================
#
def main():
	load_from_file = False

	# Create Gurobi model
	m = gp.Model()

	# Create schedule manager class
	s = Schedule(m)
	#  s = YAMLSchedule("./schedule/symmetric_route.yaml", m)
	#  s = YAMLSchedule("./schedule/test.yaml", m)
	#  s = YAMLSchedule("./schedule/route3.yaml", m)

	## Generate the schedule
	schedule = s.generate()
	#  schedule = b2c1()
	#  schedule = b3c2()

	# Separate decision variables from parameters
	params, d_var = schedule2PAndD(schedule)

	# Optimize
	o = Optimizer(m, params, d_var, load_from_file)

	## Set the number of buses
	o.setIterations(schedule['N']+schedule['A'])

	## List of constraints to optimize over
	constraints = \
	{
		### Packing
		ChargeDuration(),
		Delta(),
		Sigma(),
		SigmaDelta(),
		SpaceBigO(),
		TimeBigO(),
		ValidDepartureTime(),
		ValidEndTime(),
		ValidInitialTime(),

		### Dynamic
		BilinearLinearization(),
		ChargePropagation(),
		FinalCharge(),
		InitialCharge(),
		MaxChargePropagation(),
		MinChargePropagation(),
		ScalarToVectorQueue(),
		ValidQueueVector()
	}

	initialize(constraints, m, params, d_var)
	subscribe(constraints, o)

	results = o.optimize()

	# Plot Results
	#  p = Plotter(results)
	#  p.plotSchedule()
	#  p.plotCharges()
	#  p.plotChargerUsage()

	return

##===============================================================================
#
if __name__ == "__main__":
	main()
