#!/usr/bin/python

# Standard Lib
import gurobipy as gp
import sys
import yaml

from gurobipy import GRB

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Include in path
sys.path.append("optimize/")
sys.path.append("optimize/constraint/")
sys.path.append("optimize/constraint/dynamics/")
sys.path.append("optimize/constraint/packing/")
sys.path.append("optimize/constraint/power/")
sys.path.append("optimize/objective/")
sys.path.append("plot/")
sys.path.append("plot/plots/")
sys.path.append("schedule/generate/")
sys.path.append("schedule/load/")
sys.path.append("util/")

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Developed
from schedule_manager import Schedule
from optimizer        import Optimizer

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Objective
from min_time_objectives import MinTimeObjective
from min_power_objective import MinPowerObjective

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

## Dynamic
from discrete_power_usage    import DiscretePowerUsage
from bilinear_discrete_power import BilinearDiscretePower

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plots
from plot               import Plotter
from charge_plot        import ChargePlot
from charger_usage_plot import ChargerUsagePlot
from schedule_plot      import SchedulePlot
from power_usage_plot   import PowerUsagePlot

## Static schedules
from b2c1          import *
from b3c2          import *
from yaml_schedule import YAMLSchedule

##===============================================================================
#
def plot(results):
    plots = \
    [
        SchedulePlot(),
        ChargePlot(),
        ChargerUsagePlot(),
        PowerUsagePlot(),
    ]

    Plotter.initialize(results)

    for p in plots:
        p.plot()

    return

##===============================================================================
#
def setupObjective(o, m, params, d_var):
    objectives = \
    [
        MinTimeObjective("min_time_objective"),
        #  MinPowerObjective("min_power_objective"),
    ]

    objectives[0].initialize(m, params, d_var)
    o.subscribeObjective(objectives[0])

    return

##===============================================================================
#
def setupConstraints(o, m, params, d_var):
    # Local Variables
    A = params['A']
    N = params['N']
    Q = params['Q']

    # Set the number of visists
    o.setIterations(N+A)

    ## List of constraints to optimize over
    constraints = \
    [
        ### Packing
        ChargeDuration("charge_duration"),
        Delta("delta", N+A),
        Sigma("sigma", N+A),
        SigmaDelta("sigma_delta", N+A),
        SpaceBigO("space_big_o", N+A),
        TimeBigO("time_big_o", N+A),
        ValidDepartureTime("valid_departure_time"),
        ValidEndTime("valid_end_time"),
        ValidInitialTime("valid_initial_time"),

        ### Dynamic
        BilinearLinearization("bilinera_linearization"),
        ChargePropagation("charge_propagation"),
        FinalCharge("final_charge"),
        InitialCharge("initial_charge"),
        MaxChargePropagation("max_charge_propagation"),
        MinChargePropagation("min_charge_propagation"),
        ScalarToVectorQueue("scalar_to_vector_queue"),
        ValidQueueVector("valid_queue_vector"),

        ### Power
        #  DiscretePowerUsage("discrete_power_usage", Q),
        #  BilinearDiscretePower("biliner_discrete_power", Q),
    ]

    initializeConstr(constraints, m, params, d_var)
    subscribeConstr(constraints, o)
    return

##===============================================================================
#
def initializeConstr(constraints, model, params, d_var):
    for c in constraints:
        c.initialize(model, params, d_var)
    return

##===============================================================================
#
def subscribeConstr(constraints, optimizer_obj):
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
        'K'     : schedule['K'],
        'a'     : schedule['a'],
        'alpha' : schedule['alpha'],
        'beta'  : schedule['beta'],       # [%]
        'dt'    : schedule['dt'],
        'e'     : schedule['e'],
        'gamma' : schedule['gamma'],
        'kappa' : schedule['kappa'],
        'l'     : schedule['l'],
        'm'     : schedule['m'],
        'nu'    : schedule['nu'],
        'r'     : schedule['r'],
        's'     : np.ones(schedule['N']*schedule['A'],dtype=int),
        't'     : schedule['t'],
        'tk'    : schedule['tk'],
    }

    d_var = \
    {
        'c'     : schedule['c'],
        'delta' : schedule['delta'],
        'dt'    : schedule['dt'],
        'eta'   : schedule['eta'],
        'g'     : schedule['g'],
        'p'     : schedule['p'],
        'rho'   : schedule['rho'],
        'sigma' : schedule['sigma'],
        'u'     : schedule['u'],
        'v'     : schedule['v'],
        'w'     : schedule['w'],
        'xi'    : schedule['xi'],
    }

    return params, d_var

##===============================================================================
#
def main():
    load_from_file = False
    with open(r'./general.yaml') as f:
        lff = yaml.load(f, Loader=yaml.FullLoader)['load_from_file']
        if lff >= 1:
            load_from_file = True

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

    setupObjective(o, m, params, d_var)
    setupConstraints(o, m, params, d_var)

    results = o.optimize()

    # Plot Results
    plot(results)

    return

##===============================================================================
#
if __name__ == "__main__":
    main()
