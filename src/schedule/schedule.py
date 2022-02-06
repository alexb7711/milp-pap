# Standard Lib
import gurobipy as gp
import numpy as np
import random
import yaml

from gurobipy import GRB

# Developed
from Params import params
from array_util import *
from pretty import *

##===============================================================================
#
class Schedule:
    ##===========================================================================
    # PUBLIC

    ##---------------------------------------------------------------------------
    # Input:
    #   model : Gurobi model
    #
    # Output:
    #   NONE
    #
    def __init__(self, model):
        # Parse YAML file
        self.init = self.__parseYAML()

        # Store gurobi model
        self.model = model

        # If a new schedule is to be generated
        if self.init['run_prev'] <= 0:
            self.__generateAttributes()

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   NONE
    #
    # Output:
    #   Schedule parameters
    #
    def generate(self):
        if self.init['run_prev'] <= 0:
            self.__generateScheduleParams()
        else:
            self.__loadPreviousParams()

        schedule = createSchedule()
        return

    ##===========================================================================
    # PRIVATE

    ##---------------------------------------------------------------------------
    # Input:
    #   NONE
    #
    # Output:
    #   self.init: Parsed schedule YAML file
    #
    def __parseYAML(self):
        init = {}
        with open(r'./schedule/generate/schedule.yaml') as f:
                init = yaml.load(f, Loader=yaml.FullLoader)

        return init

    ##---------------------------------------------------------------------------
    # Input:
    #   NONE
    #
    # Output:
    #   Schedule attributes
    #
    def __generateAttributes(self):
            # Create list of discharge rates
            discharge_rate = np.repeat([self.init['buses']['dis_rate']],
                                        self.init['buses']['num_bus'])

            # Evaluate charger parameters
            slow_chargers = np.array(np.repeat([self.init['chargers']['slow']['rate']],
                                     int(self.init['chargers']['slow']['num'])),
                                     dtype=int)
            fast_chargers = np.array(np.repeat([self.init['chargers']['fast']['rate']],
                                     int(self.init['chargers']['fast']['num'])),
                                     dtype=int)
            r = np.concatenate((slow_chargers, fast_chargers))
            e = r.copy()
            m = r.copy()

            self.dt      = self.init['time']['dt']/60

            # Store Input Parameters
            self.A       = self.init['buses']['num_bus']
            self.N       = self.init['buses']['num_visit']
            self.Q       = self.init['chargers']['slow']['num'] + \
                           self.init['chargers']['fast']['num']
            self.T       = self.init['time']['time_horizon']
            self.K       = int(self.T/self.dt)
            self.dis_rat = discharge_rate # [kwh]
            self.e       = e
            self.m       = m
            self.mrt     = self.init['buses']['max_rest']   # [hr]
            self.nu      = self.init['buses']['min_charge'] # [%]
            self.r       = r

            # Arrays to be generated
            ## Arrival time
            self.a     = np.zeros(self.N, dtype=float)

            ## Departure time
            self.t     = -1*np.ones(self.N, dtype=float)

            ## Discharge for route i
            self.l     = np.zeros(self.N, dtype=float)

            ## Initial charge for each visit
            self.alpha = np.zeros(self.N, dtype=float)

            ## ID of bus for each visit
            self.gamma = -1*np.ones(self.N+self.A, dtype=int)

            ## Index of next bus visit
            self.Gamma = -1*np.ones(self.N, dtype=int)

            ## Index of final bus visit
            self.beta = -1*np.ones(self.N, dtype=int)

            ## Discrete time steps
            self.tk   = np.array([i*self.dt for i in range(0,T,self.K)]);

            return
