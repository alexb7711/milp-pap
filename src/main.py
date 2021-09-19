#!/usr/bin/python

# Standard Lib
import gurobipy as gp
import sys

from gurobipy import GRB

# Include in path
sys.path.append("util/")
sys.path.append("schedule/")
sys.path.append("genmat/")
sys.path.append("optimize/")

# Developed
from schedule_manager import Schedule
from gen_mat          import GenMat
from optimizer        import Optimizer
from plot             import Plotter

## Static schedules
from b2c1          import *
from b3c2          import *
from yaml_schedule import YAMLSchedule

##===============================================================================
#
def main():
    #  save_scenario = True

    # Create Gurobi model
    m = gp.Model()

    # Create schedule manager class
    #  s = Schedule(m, save_scenario)
    s = YAMLSchedule("./schedule/symmetric_route.yaml", m)
    #  s = YAMLSchedule("./schedule/test.yaml", m)
    #  s = YAMLSchedule("./schedule/route3.yaml", m)

    ## Generate the schedule
    schedule = s.generate()
    #  schedule = b2c1()
    #  schedule = b3c2()

    # Create Matrix
    #  gm = GenMat(schedule)

    ## Generate matrices
    #  gm.genMats()

    # Optimize
    o = Optimizer(schedule, False)

    results = o.optimize()

    # Plot Results
    p = Plotter(results)
    p.plotSchedule()
    p.plotCharges()
    p.plotChargerUsage()

    return

##===============================================================================
#
if __name__ == "__main__":
    main()
