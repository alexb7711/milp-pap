#!/usr/bin/python

# Standard Lib
import numpy as np
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
sys.path.append("schedule/")
sys.path.append("util/")

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Developed
#  from schedule_manager import Schedule
from scheduler import Schedule
from optimizer import Optimizer
from pretty    import *

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Data managers
from data_manager import DataManager

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

## Power
from discrete_power_usage    import DiscretePowerUsage

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plots
from plot               import Plotter
from charge_plot        import ChargePlot
from charger_usage_plot import ChargerUsagePlot
from schedule_plot      import SchedulePlot
from power_usage_plot   import PowerUsagePlot

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
def setupObjective(o, dm):
    # Local variables
    d_var  = dm.m_decision_var
    m      = dm['model']
    params = dm.m_params

    objectives = \
    [
        MinTimeObjective("min_time_objective"),
        MinPowerObjective("min_power_objective"),
    ]

    objectives[0].initialize(m, params, d_var)
    o.subscribeObjective(objectives[0])

    return

##===============================================================================
#
def setupConstraints(o, dm):
    # Local Variables
    A = dm['A']
    N = dm['N']
    Q = dm['Q']
    d_var  = dm.m_decision_var
    m = dm['model']
    params = dm.m_params

    # Set the number of visists
    o.setIterations(N)

    ## List of constraints to optimize over
    constraints = \
    [
        ### Packing
        ChargeDuration("charge_duration"),
        Delta("delta", N),
        Sigma("sigma", N),
        SigmaDelta("sigma_delta", N),
        SpaceBigO("space_big_o", N),
        TimeBigO("time_big_o", N),
        ValidDepartureTime("valid_departure_time"),
        ValidEndTime("valid_end_time"),
        ValidInitialTime("valid_initial_time"),

        ### Dynamic
        BilinearLinearization("bilinear_linearization"),
        ChargePropagation("charge_propagation"),
        FinalCharge("final_charge"),
        InitialCharge("initial_charge"),
        MaxChargePropagation("max_charge_propagation"),
        MinChargePropagation("min_charge_propagation"),
        ScalarToVectorQueue("scalar_to_vector_queue"),
        ValidQueueVector("valid_queue_vector"),

        ### Power
        DiscretePowerUsage("discrete_power_usage", Q),
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
def main():
    load_from_file = False
    with open(r'config/general.yaml') as f:
        lff = yaml.load(f, Loader=yaml.FullLoader)['load_from_file']
        if lff >= 1:
            load_from_file = True

    # Create data manager object
    dm = DataManager()

    # Create gurobi model
    m = dm['model'] = gp.Model()

    # Create schedule manager class
    Schedule(m)

    # Optimize
    ## Initialize optimizer
    o = Optimizer(load_from_file)

    ## Initialize objectives and constraints
    setupObjective(o, dm)
    setupConstraints(o, dm)

    ## Optimize model
    results = o.optimize()

    # Plot Results
    plot(results)

    return

##===============================================================================
#
if __name__ == "__main__":
    main()
