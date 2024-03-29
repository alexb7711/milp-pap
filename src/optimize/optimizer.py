# System Modules
import yaml
import sys
import numpy as np

from progress.bar import Bar

np.set_printoptions(threshold=sys.maxsize)

# Developed Modules
from data_manager import DataManager
from dict_util import merge_dicts


##===============================================================================
#
class Optimizer:
    ##===========================================================================
    # PUBLIC
    ##===========================================================================

    ##---------------------------------------------------------------------------
    #
    def __init__(self, data_d: str = "../data"):
        # Parse 'config/general.yaml'
        with open(r"config/general.yaml") as f:
            file = yaml.load(f, Loader=yaml.FullLoader)
            self.jobs = file["jobs"]
            self.verbose = file["verbose"]
            self.lff = file["load_from_file"]
            self.time_lim = file["time_limit"]
            self.solver = file["solver"]

        # Initialize member variables
        self.dm = DataManager()
        self.model = self.dm["model"]
        self.params = self.dm.m_params
        self.d_var = self.dm.m_decision_var
        self.data_d = data_d
        self.constr = []
        self.objective = []

        return

    ##---------------------------------------------------------------------------
    #
    def optimize(self):
        """
            This method runs the uta-pap optimization based on the the data
            set in DataManager shared memory.

        Input:
            NONE

        Output:
            Gurobi MILP optimization results
        """
        if not self.lff:
            # gurobi model
            model = self.model

            # Set time limit
            model.setParam("TimeLimit", self.time_lim)

            # Objective
            print(
                "===================================================================="
            )
            print("Creating Objective...")
            print(
                "===================================================================="
            )
            self.__inputObjectives()

            # Add constraints
            print(
                "===================================================================="
            )
            print("Adding Constraints")
            print(
                "===================================================================="
            )
            with Bar("", max=self.iterations) as bar:
                for i in range(self.iterations):
                    self.__inputConstraints(i)
                    bar.next()

            # Uncomment to print model to disk
            #  model.write("model.lp")

            # Optimize
            print(
                "===================================================================="
            )
            print("Optimizing")
            print(
                "===================================================================="
            )
            model.optimize()

            # Save Results
            ## Extract all the decision variable results
            d_var_results = dict(
                (k, self.dm.m_decision_var[k].X)
                for k in self.dm.m_decision_var.keys()
                if k != "model"
            )

            ## Combine decision variable results with input parameters
            results = merge_dicts(self.dm.m_params, d_var_results)

            ## Save the results to disk
            np.save(self.data_d + "/results.npy", results)
        else:
            ## Load the results from disk
            results = np.load(self.data_d + "/results.npy", allow_pickle="TRUE").item()

        # Update data manager with results
        self.__updateDM(results)

        return results

    ##---------------------------------------------------------------------------
    # Input:
    #                       i: Number of iterations to apply constraints
    #
    # Output:
    #                       NONE
    #
    def setIterations(self, i):
        self.iterations = i
        return

    ##---------------------------------------------------------------------------
    # Input:
    #                       constr: Constraint object
    #
    # Output:
    #                       NONE
    #
    def subscribeConstraint(self, constr):
        self.constr.append(constr)
        return

    ##---------------------------------------------------------------------------
    # Input:
    #                       objective: Objective object
    #
    # Output:
    #                       NONE
    #
    def subscribeObjective(self, objective):
        self.objective.append(objective)
        return

    ##===========================================================================
    # PRIVATE
    ##===========================================================================

    ##---------------------------------------------------------------------------
    # Input:
    #                       NONE
    #
    # Output:
    #                       NONE
    #
    def __inputObjectives(self):
        for o in self.objective:
            if self.verbose > 0:
                print("Adding {0}...".format(o.name))
            o.addObjective()
        return

    ##---------------------------------------------------------------------------
    # Input:
    #                       NONE
    #
    # Output:
    #                       NONE
    #
    def __inputConstraints(self, i):
        for c in self.constr:
            if self.verbose > 0:
                print("Adding {0}...".format(c.name))

            c.addConstr(i)
        return

    ##---------------------------------------------------------------------------
    #
    def __updateDM(self, results):
        """
        Update the data manger with the result of the MILP

        Input:
          - results : Output of the MILP decision variables

        Output:
            - None
        """
        # Variables
        dm = self.dm
        r = results

        # Split dictionary into a list of keys and values
        k = r.keys()
        v = r.values()

        # Update data manager
        dm.setList(k, v)
        return
