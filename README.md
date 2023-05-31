# UTA-PAP
UTA PAP is a Mixed Integer Linear Program (MILP) designed to solve the Position Allocation Problem (PAP) for the a
general battery electric bus (BEB) system. The position allocation problem is a rectangle packing problem where the
x-axis is defined as time and the y-axis is the set of queues for each charger. Given a sequence of bus visits, initial
charges, and types of charger, the program will estimate BEB discharges and determine and optimal scheduling for the
given routes.

## Running the Program
To run, go into source code and type 'make setup' which will set up the virtual environment and install the dependencies
and then type `make run`.

TODO: Hyperlink Gurobi and GLPK (PyMathProg) to their web-sites

The program utilizes the GNU linear programming kit (GLPK) as well as Gurobi to solve the MILP. If you wish to use
Gurobi, you will need to have a valid license installed. Gurobi and GLPK will be installed as dependencies when `make
setup` is ran. *By default GLPK will be used as it is an open source project and more accessible*.

# NOTE
The scenarios generated are random. There is a chance that the scenario generated is not feasible (although not very
likely). There are two YAML files: 'src/schedule/generate/schedule.yaml' where you can enable the 'run_prev' variable
which will use the previous generated scenario, but resolve the problem. This is to allow you to change the constraints
but keep the same scenario such that you can see the affects of the constraints.
