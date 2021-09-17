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
    #  s = YAMLSchedule("./schedule/symmetric_route.yaml", m)
    s = YAMLSchedule("./schedule/test.yaml", m)
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
    mats = \
    {
        #  "Apeq" : gm.A_pack_eq,
        #  "xpeq" : gm.x_pack_eq,
        #  "bpeq" : gm.b_pack_eq,
        #  "Adeq" : gm.A_dyn_eq,
        #  "xdeq" : gm.x_dyn_eq,
        #  "bdeq" : gm.b_dyn_eq,
        #  "Apineq" : gm.A_pack_ineq,
        #  "xpineq" : gm.x_pack_ineq,
        #  "bpineq" : gm.b_pack_ineq,
        #  "Adineq" : gm.A_dyn_ineq,
        #  "xdineq" : gm.x_dyn_ineq,
        #  "bdineq" : gm.b_dyn_ineq,
    }

    o = Optimizer(schedule)

    o.optimize()

    return

##===============================================================================
#
if __name__ == "__main__":
    main()
