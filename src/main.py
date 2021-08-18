#!/usr/bin/python

# Standard Lib
import gurobipy as gp
import sys

from gurobipy import GRB

# Include in path
sys.path.append("util/")
sys.path.append("schedule/")
sys.path.append("genmat/")

# Developed
from schedule_manager import Schedule
from gen_mat  import GenMat

##===============================================================================
#
def main():
    # Create Gurobi model
    m = gp.Model("UTAPAP")

    # Create schedule manager class
    s = Schedule(m)

    ## Generate the schedule
    schedule = s.generate()

    # Create Matrix
    gm = GenMat(schedule)

    ## Generate matrices
    gm.genMats()

    # Optimize

    return

##===============================================================================
#
if __name__ == "__main__":
    main()
