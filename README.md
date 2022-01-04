# uta-pap
To run, go into source code and type 'make setup' which will set up the virtual environment and install the dependencies and then 'make run'.

You will also need to have a gurobi licensed installed to solve a problem of this size.

# NOTE
The scenarios generated are random. There is a chance that the scenario generated is not feasible (although not very likely). There are two YAML files: 'src/schedule/generate/schedule.yaml' where you can enable the 'run_prev' variable which will use the previous generated scenario, but resolve the problem. This is to allow you to change the constraints but keep the same scenario such that you can see the affects of the constraints.
