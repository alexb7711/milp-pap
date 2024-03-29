#!/usr/bin/python

# ================================================================================
# INCLUDES

# Standard Lib
import gurobipy as gp
import os
import sys
import yaml

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Include in path
#
# Recursively include in path:
# https://www.tutorialspoint.com/python/os_walk.htm
for root, dirs, files in os.walk(".", topdown=False):
    for name in dirs:
        sys.path.append(root + "/" + name)

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Developed
from scheduler import Schedule
from optimizer import Optimizer
from quin_modified import QuinModified

from data_output import outputData

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Data managers
from data_manager import DataManager

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Objective
from min_time_objectives import MinTimeObjective

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Constraints
## Packing
from charge_duration import ChargeDuration
from delta import Delta
from sigma import Sigma
from sigma_delta import SigmaDelta
from space_big_o import SpaceBigO
from time_big_o import TimeBigO
from valid_departure_time import ValidDepartureTime
from valid_end_time import ValidEndTime
from valid_initial_time import ValidInitialTime

## Dynamic
from bilinear_linearization import BilinearLinearization
from charge_propagation import ChargePropagation
from final_charge import FinalCharge
from initial_charge import InitialCharge
from max_charge_propagation import MaxChargePropagation
from min_charge_propagation import MinChargePropagation
from scalar_to_vector_queue import ScalarToVectorQueue
from valid_queue_vector import ValidQueueVector

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plots
from plot import Plotter
from charge_plot import ChargePlot
from charger_usage_plot import ChargerUsagePlot
from schedule_plot import SchedulePlot
from power_usage_plot import PowerUsagePlot
from accumulated_energy_usage_plot import AccumulatedEnergyUsagePlot

##===============================================================================
# FUNCTIONS


##-------------------------------------------------------------------------------
#
def createModel(path: str = "./config/general.yaml"):
    """
    Input:
      - str : Path to the configuration file

    Output:
      - model : Model for the MILP to be created with
    """
    # Variables
    f = open(path, "r")  # Open file
    model = None  # MILP model

    # Parse 'config/general.yaml'
    with open(r"config/general.yaml") as f:
        file = yaml.load(f, Loader=yaml.FullLoader)
        solver = file["solver"]

    # Create the appropriate model
    # TODO: Create appropriate model for GLPK
    if solver == "GLPK":
        model = gp.Model()
    else:
        model = gp.Model()

    return model


##-------------------------------------------------------------------------------
#
def plot(results, dm):
    """
    Runs a list of plot functions

    Input
      - results : Output of GUROBI solution
      - dm      : Data Manager

    Output
      - NONE
    """
    plots = [
        SchedulePlot(),
        ChargePlot(),
        ChargerUsagePlot(),
        PowerUsagePlot(),
        AccumulatedEnergyUsagePlot(),
    ]

    Plotter.initialize(results, dm)

    with open(r"config/general.yaml") as f:
        file = yaml.load(f, Loader=yaml.FullLoader)
        if file["plot"] > 0:
            for p in plots:
                p.plot()

    return


##-------------------------------------------------------------------------------
#
def setupObjective(o, dm):
    # Local variables
    d_var = dm.m_decision_var
    m = dm["model"]
    params = dm.m_params

    objectives = [
        MinTimeObjective("min_time_objective"),
    ]

    objectives[0].initialize(m, params, d_var)
    o.subscribeObjective(objectives[0])

    return


##-------------------------------------------------------------------------------
#
def setupConstraints(o, dm):
    # Local Variables
    A = dm["A"]
    N = dm["N"]
    Q = dm["Q"]
    d_var = dm.m_decision_var
    m = dm["model"]
    params = dm.m_params

    # Set the number of visists
    o.setIterations(N)

    ## List of constraints to optimize over
    constraints = [
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
    ]

    initializeConstr(constraints, m, params, d_var)
    subscribeConstr(constraints, o)
    return


##-------------------------------------------------------------------------------
#
def initializeConstr(constraints, model, params, d_var):
    for c in constraints:
        c.initialize(model, params, d_var)
    return


##-------------------------------------------------------------------------------
#
def subscribeConstr(constraints, optimizer_obj):
    for c in constraints:
        optimizer_obj.subscribeConstraint(c)
    return


##===============================================================================
# MAIN
def main():
    # Create data manager object
    dm = DataManager()

    # Create MILP model
    dm["model"] = createModel()

    # Create schedule
    Schedule(dm["model"])

    # Optimize
    ## Initialize optimizer
    o = Optimizer()  # MILP solution
    qm = QuinModified()  # Quin Modified solution

    ## Initialize objectives and constraints
    setupObjective(o, dm)
    setupConstraints(o, dm)

    ### Optimize model with MILP
    results = o.optimize()
    outputData("milp", results)
    plot(results, dm)

    ### Optimize with Quin-Modified
    results = qm.optimize()
    outputData("qm", dm)
    plot(results, dm)

    return


##===============================================================================
#
if __name__ == "__main__":
    main()
