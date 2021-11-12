#!/usr/bin/python

# Standard Lib
import gurobipy as gp
import sys

from gurobipy import GRB

# Include in path
sys.path.append("util/")
sys.path.append("schedule/")
sys.path.append("optimize/")

# Developed
from schedule_manager import Schedule
from optimizer        import Optimizer
from plot             import Plotter

## Static schedules
from b2c1          import *
from b3c2          import *
from yaml_schedule import YAMLSchedule

##===============================================================================
#
def main():
    load_from_file = False

    # Create Gurobi model
    m                  = gp.Model()
    m.Params.TimeLimit = 900

    # Create schedule manager class
    s = Schedule(m)
    #  s = YAMLSchedule("./schedule/symmetric_route.yaml", m)
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
    o = Optimizer(schedule, load_from_file)

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
