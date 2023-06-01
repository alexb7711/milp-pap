#!/usr/bin/python

#================================================================================
# INCLUDES

# Standard Lib
import numpy as np
import gurobipy as gp
import sys
import yaml

from gurobipy import GRB

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Include in path

# Optimizer
sys.path.append("optimize/")
sys.path.append("optimize/constraint/glpk")
sys.path.append("optimize/constraint/dynamics/")
sys.path.append("optimize/constraint/packing/")
sys.path.append("optimize/objective/")

# Plot
sys.path.append("plot/")
sys.path.append("plot/plots/")
sys.path.append("schedule/")
sys.path.append("util/")

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Developed
from scheduler     import Schedule
from optimizer     import Optimizer
from quin_modified import QuinModified
from pretty        import *
from data_output   import outputData

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Data managers
from data_manager import DataManager

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Objective
from gurobi_min_time_objectives import GBMinTimeObjective

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Constraints
## Packing
from gurobi_charge_duration      import GBChargeDuration
from gurobi_delta                import GBDelta
from gurobi_sigma                import GBSigma
from gurobi_sigma_delta          import GBSigmaDelta
from gurobi_space_big_o          import GBSpaceBigO
from gurobi_time_big_o           import GBTimeBigO
from gurobi_valid_departure_time import GBValidDepartureTime
from gurobi_valid_end_time       import GBValidEndTime
from gurobi_valid_initial_time   import GBValidInitialTime

## Dynamic
from gurobi_bilinear_linearization import GBBilinearLinearization
from gurobi_charge_propagation     import GBChargePropagation
from gurobi_final_charge           import GBFinalCharge
from gurobi_initial_charge         import GBInitialCharge
from gurobi_max_charge_propagation import GBMaxChargePropagation
from gurobi_min_charge_propagation import GBMinChargePropagation
from gurobi_scalar_to_vector_queue import GBScalarToVectorQueue
from gurobi_valid_queue_vector     import GBValidQueueVector

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plots
from plot                          import Plotter
from charge_plot                   import ChargePlot
from charger_usage_plot            import ChargerUsagePlot
from schedule_plot                 import SchedulePlot
from power_usage_plot              import PowerUsagePlot
from accumulated_energy_usage_plot import AccumulatedEnergyUsagePlot

##===============================================================================
# FUNCTIONS

##-------------------------------------------------------------------------------
#
def createModel(self, dm: DataManager, path: str="./config/general.yaml"):
    """
        Input:
          - dm  : Data manager instance
          - str : Path to the configuration file

        Output:
          - model : Model for the MILP to be created with
        """
    # Variables
    f     = open(path, "r")                                                     # Open file
    init  = yaml.load(self.f, Loader = yaml.FullLoader)                         # Parse YAML
    model = None                                                                # MILP model

    # Parse 'config/general.yaml'
    with open(r'config/general.yaml') as f:
        file   = yaml.load(f, Loader=yaml.FullLoader)
        solver = file['solver']

    # Create the appropriate model
    # TODO: Create appropriate model for GLPK
    if solver == "GLPK":
        model = gp.Model()
    else:
        model = gp.Model()

    # Assign and return model
    dm['model'] = model

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
    plots = \
    [
        SchedulePlot(),
        ChargePlot(),
        ChargerUsagePlot(),
        PowerUsagePlot(),
        AccumulatedEnergyUsagePlot(),
    ]

    Plotter.initialize(results, dm)


    with open(r'config/general.yaml') as f:
        file = yaml.load(f, Loader=yaml.FullLoader)
        if file['plot'] > 0:
            for p in plots: p.plot()

    return

##-------------------------------------------------------------------------------
#
def setupObjective(o, dm):
    # Local variables
    d_var  = dm.m_decision_var
    m      = dm['model']
    params = dm.m_params

    objectives = \
    [
        MinTimeObjective("min_time_objective"),
    ]

    objectives[0].initialize(m, params, d_var)
    o.subscribeObjective(objectives[0])

    return

##-------------------------------------------------------------------------------
#
def setupConstraints(o, dm):
    # Local Variables
    A      = dm['A']
    N      = dm['N']
    Q      = dm['Q']
    d_var  = dm.m_decision_var
    m      = dm['model']
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
    createModel(dm['model'])

    # Create schedule
    Schedule(dm['model'])

    # Optimize
    ## Initialize optimizer
    o  = Optimizer()                                                            # MILP solution
    qm = QuinModified()                                                         # Quin Modified solution

    ## Initialize objectives and constraints
    setupObjective(o, dm)
    setupConstraints(o, dm)

    ### Optimize model with MILP
    results = o.optimize()
    outputData("milp", results)

    ### Plot Results
    plot(results, dm)

    ### Optimize with Quin-Modified
    results = qm.optimize()
    outputData("qm", dm)

    ### Plot/Output Results
    plot(results, dm)

    return

##===============================================================================
#
if __name__ == "__main__":
    main()
