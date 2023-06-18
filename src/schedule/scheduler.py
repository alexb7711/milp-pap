"""
This file is abstracts the schedule generating routines. Currently, depending how
the `general.yaml` is configured, this file generates routes via

- route data from a csv file
- randomly generated routes

This file also interacts with the data manager by saving all the input parameters
and the generated decision variables.

Most, if not all interaction for schedule generation shoud be done through this file.
"""

# Standard Library
import gurobipy as gp
import numpy as np
import yaml

from gurobipy import GRB

# Developed
from array_util   import *
from bus_data     import *
from csv_loader   import genCSVRoutes
from data_manager import DataManager
from gen_schedule import genNewSchedule
from pretty       import *

##===============================================================================
#
class Schedule:
    ##===========================================================================
    # PUBLIC

    ##---------------------------------------------------------------------------
    #
    def __init__(self, model, c_path: str="./config/", d_path: str= "./data"):
        """
        Input:
          - model  : MILP model
          - c_path : Relative path to the base of the configuration files
          - d_path : Relative path to the base of the data files

        Output:
          - NONE
        """

        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Executable code

        # Parse YAML file
        self.init, self.run_prev, self.schedule_type = self.__parseYAML(c_path)

        # Get an instance of data manager
        self.dm = DataManager()

        # Store gurobi model
        self.model = model

        # If a new schedule is to be generated
        if self.run_prev <= 0:
            # Generate random schedule
            if self.schedule_type == "random": genNewSchedule(self)
            # Load schedule from CSV
            else                             : genCSVRoutes(self, d_path)
            # Generate decision variables
            self.__genDecisionVars()
        else:
            self.__loadPreviousParams()

        return

    ##---------------------------------------------------------------------------
    #
    def __del__(self):
        """
        Input:
          - NONE

        Output:
          - NONE
        """
        # Close the opened YAML file
        self.f.close()
        return

    ##---------------------------------------------------------------------------
    #
    def fillBusData(self, id: int, arrival_t: float, departure_t: float, discharge: float) -> dict:
        """
        Input:
          arrival_t   : Arrival time of bus a visit i
          departure_t : Departure time of bus a visit i
          discharge   : Total discharge from route

        Output:
          b: filled bus_info dictionary
        """
        # Local variables
        keys = bus_info.keys()
        data = [id, arrival_t, departure_t, discharge]

        return dict(zip(keys, data))

    ##===========================================================================
    # PRIVATE

    ##---------------------------------------------------------------------------
    #
    def __parseYAML(self, path):
        """
        Input:
          - NONE

        Output:
          - self.init: Parsed schedule YAML file
        """
        # Variables
        self.f   = open(path+'/schedule.yaml', "r")
        init     = yaml.load(self.f, Loader = yaml.FullLoader)

        # Parse 'config/general.yaml'
        with open(path+"/general.yaml", "r") as f:
                file          = yaml.load(f, Loader=yaml.FullLoader)
                run_prev      = file['run_prev']
                schedule_type = file['schedule_type']

        return init, run_prev, schedule_type

    ##---------------------------------------------------------------------------
    #
    def __loadPreviousParams(self):
        """
        Save the generated parameters

        Input:
            NONE

        Output:
            Previously generated schedule
        """

        # Load previous run input params from disk
        data = np.load('data/input_vars.npy', allow_pickle='TRUE').item()

        self.__saveKVParams(data)
        self.__genDecisionVars()
        return

    ##---------------------------------------------------------------------------
    #
    def __saveKVParams(self, kv):
        """
        Input:
          - kv: Key/value pair for input parameters

        Output:
          - Save input parameters in shared memory
        """
        # Local variables
        keys   = list(kv.keys())
        values = list(kv.values())

        # Save values to shared memory
        self.dm.setList(keys, values)
        return

    ##---------------------------------------------------------------------------
    #
    def __genDecisionVars(self):
        """
        Input:
          model: Gurobi model object

        Output:
          The following gurobi MVars:
          u     : Starting charge time
          v     : Selected charging queue
          c     : Detatch time fro visit i
          p     : Amount of time spent on charger for visit i
          g     : Linearization term for bilinear term
          eta   : Initial charge for visit i
          w     : Vector representation of v
          sigma : if u_i < u_j ? true : false
          delta : if v_i < v_j ? true : false
        """
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Variables
        N = self.dm['N']
        Q = self.dm['Q']

        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Executable code

        # If no model was loaded, return
        if not self.model:
            return

        # Generate decision variables
        ## Initial charge time
        self.dm['u'] = self.model.addMVar(shape=N, vtype=GRB.CONTINUOUS, name="u")

        ## Assigned queue
        self.dm['v'] = self.model.addMVar(shape=N, vtype=GRB.CONTINUOUS, name="v")

        ## Detatch time
        self.dm['c'] = self.model.addMVar(shape=N, vtype=GRB.CONTINUOUS, name="c")

        ## Charge time
        self.dm['p'] = self.model.addMVar(shape=N, vtype=GRB.CONTINUOUS, name="p")

        ## Lineriztion term
        self.dm['g'] = self.model.addMVar(shape=(N,Q), vtype=GRB.CONTINUOUS, name="g")

        ## Initial charge
        self.dm['eta'] = self.model.addMVar(shape=N, vtype=GRB.CONTINUOUS, name="eta")

        ## Vector representation of queue
        self.dm['w'] = self.model.addMVar(shape=(N,Q), vtype=GRB.BINARY, name="w")

        ## Sigma
        self.dm['sigma'] = self.model.addMVar(shape=(N,N), vtype=GRB.BINARY, name="sigma")

        ## Delta
        self.dm['delta'] = self.model.addMVar(shape=(N,N), vtype=GRB.BINARY, name="delta")

        return
