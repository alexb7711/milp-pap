# Standard Lib
import gurobipy as gp
import numpy as np
import random
import yaml

from gurobipy import GRB

# Developed
from data_manager import DataManager
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

        # Create data manager object
        self.dm = DataManager()

        # Store gurobi model
        self.model       = model
        self.dm['model'] = model

        # If a new schedule is to be generated
        if self.init['run_prev'] <= 0:
            self.__loadAttributes()
            self.__generateScheduleParams()
        else:
            self.__loadPreviousParams()

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   NONE
    #
    # Output:
    #   NONE
    #
    def __del__(self):
        # Close the opened YAML file
        self.f.close()
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
        self.f = open(r'./config/schedule.yaml')
        init   = yaml.load(self.f, Loader=yaml.FullLoader)
        return init

    ##---------------------------------------------------------------------------
    # Input:
    #   NONE
    #
    # Output:
    #   Schedule attributes
    #
    def __loadAttributes(self):
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Local Variables
        init = self.init

        ## Evaluate charger parameters
        slow_chargers = np.array(np.repeat([init['chargers']['slow']['rate']],
                                 int(init['chargers']['slow']['num'])),
                                 dtype=int)
        fast_chargers = np.array(np.repeat([init['chargers']['fast']['rate']],
                                 int(init['chargers']['fast']['num'])),
                                 dtype=int)

        ### Concatenate charge rates
        r = np.concatenate((slow_chargers, fast_chargers))

        ### Assign cost of assignment and use for each charger
        epsilon = r.copy()
        m       = r.copy()

        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Store Input Parameters

        ## Number of buses
        self.dm['A'] = init['buses']['num_bus']

        ## Number of bus visits
        self.dm['N'] = init['buses']['num_visit']

        ## Number of chargers
        self.dm['Q'] = init['chargers']['slow']['num'] + \
                       init['chargers']['fast']['num']

        ## Time horizon
        self.dm['T'] = init['time']['time_horizon']

        ## Total number of discrete steps
        self.dm['K'] = init['time']['K']

        ## Initial charge percentages
        self.dm['alpha'] = np.zeros(self.dm['A'], dtype=float)

        ## Final charge percentages
        self.dm['beta'] = np.zeros(self.dm['A'], dtype=float)

        ## Calculate discrete time step
        self.dm['dt'] = self.dm['T']/self.dm['K']

        ## Cost of use for charger q
        self.dm['epsilon'] = epsilon

        ## Cost of assignment for charger q
        self.dm['m'] = m

        ## Maximum/Minimum rest time between bus routes
        self.dm['maxrst'] = init['buses']['max_rest']
        self.dm['minrst'] = init['buses']['min_rest']

        ## Maximum/Minimum rout time between bus routes
        self.dm['maxrt'] = init['buses']['max_route']
        self.dm['minrt'] = init['buses']['min_route']

        ## Minimum charge allowed on next visit
        self.dm['nu'] = init['buses']['min_charge']

        ## Charge rate for bus q
        self.dm['r'] = r

        ## Discrete time steps
        self.dm['tk'] = np.array([i*self.dm['dt'] for i in range(0,self.dm['K'])]);

        ## Discharge rate
        self.dm['zeta'] = np.repeat([init['buses']['dis_rate']], init['buses']['num_bus'])


        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Arrays to be generated

        ## Arrival time
        self.dm['a'] = np.zeros(self.dm['N'], dtype=float)

        ## Departure time
        self.dm['tau'] = np.zeros(self.dm['N'], dtype=float)

        ## Discharge for route i
        self.dm['lambda'] = np.zeros(self.dm['N'], dtype=float)

        ## ID of bus for each visit
        self.dm['gamma'] = np.zeros(self.dm['N'], dtype=int)

        ## Index of next bus visit
        self.dm['Gamma'] = np.zeros(self.dm['N'], dtype=int)

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   NONE
    #
    # Output:
    #   Randomly generated schedule
    #
    def __generateScheduleParams(self):
        # Local variables
        A = self.dm['A']
        N = self.dm['N']

        # Determine amount of visits for each bus
        # http://sunny.today/generate-random-integers-with-fixed-sum/
        num_visits = np.random.multinomial(N, np.ones(A)/A, size=1)[0]

        # For each bus
        for a,n in zip(range(A),num_visits):
            ## Initialize the previous arribval/departure
            ## to hour 0 (beginning of day)
            prev_departure = 0.
            next_arrival   = 0.

            ## For each bus, determine all the parameters for each visit
            for i in range(n):
                ### Determine if this visit is the final visit
                final_visit = True if i == n else False

                ### Select a start time (<= to the max rest time)
                prev_departure = self.__selectDeptTime(next_arrival, final_visit)

                ### Select a duration (<= to the max route time allowed)
                next_arrival = self.__selectDuration(i, n)

                print("arr: ", next_arrival)
                print("dep: ", prev_departure)
                input()

                ## Calculate departure time
                #  self.__calcDepartureTime(self)

                ### Calculate discharge
                #  self.__calcDischarge(self)

        # Determine gamma array

        # Determine Gamma array

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   NONE
    #
    # Output:
    #   Previously generated schedule
    #
    def __loadPreviousParams():
        data = np.load('data/input_vars.npy', allow_pickle='TRUE').item()
        self.__saveKVParams(data)
        self.__genDecisionVars()
        return

    ##---------------------------------------------------------------------------
    # Input:
    #   kv: Key/value pair for input parameters
    #
    # Output:
    #   Save input parameters in shared memory
    #
    def __saveKVParams(self, kv):
        # Local variables
        keys   = list(kv.keys())
        values = list(kv.values())

        # Save values to shared memory
        self.dm.setList(keys, values)

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   model: Gurobi model object
    #
    # Output:
    #   The following gurobi MVars:
    #   u     : Starting charge time
    #   v     : Selected charging queue
    #   c     : Detatch time fro visit i
    #   p     : Amount of time spent on charger for visit i
    #   g     : Linearization term for bilinear term
    #   eta   : Initial charge for visit i
    #   w     : Vector representation of v
    #   sigma : if u_i < u_j ? true : false
    #   delta : if v_i < v_j ? true : false
    #
    def __genDecisionVars(self):
        # Local Variables
        A = self.A
        N = self.N
        K = self.K
        Q = self.Q

        # Generate decision variables
        ## Initial charge time
        self.dm['u'] = self.model.addMVar(shape=N, vtype=GRB.CONTINUOUS, name="u")

        ## Assigned queue
        self.dm['v'] = self.model.addMVar(shape=N, vtype=GRB.CONTINUOUS, name="v")

        ## Detatch tiself.dm['model.
        self.dm['c'] = self.model.addMVar(shape=N, vtype=GRB.CONTINUOUS, name="c")

        ## Charge tiself.dm['model.
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

        ## Xi
        self.dm['xi'] = self.model.addMVar(shape=(N, Q, K), vtype=GRB.BINARY, name="xi")

        ## Psi
        self.dm['psi'] = self.model.addMVar(shape=(N, Q, K), vtype=GRB.BINARY, name="psi")

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   NONE
    #
    # Output:
    #   Next departure time
    #
    def __selectDeptTime(self, prev_arrival: float, final_visit: bool) -> float:
        # Local Variables
        maxrst = self.dm['maxrst']
        minrst = self.dm['minrst']

        if not final_visit:
            # If the next departure time is less than the time horizon use that,
            # otherwise set the departure time as the time horizon
            dept_time = \
                    prev_arrival + random.uniform(minrst, maxrst)                if   \
                    prev_arrival + random.uniform(minrst, maxrst) < self.dm['T'] else \
                    self.dm['T']
        else:
            dept_time = self.dm['T']

        return dept_time

    ##---------------------------------------------------------------------------
    # Input:
    #   i: Current visit number for bus a
    #   n: Total number of visits for bus a
    #
    # Output:
    #   Next arrival time
    #
    def __selectDuration(self, i: float, n: float) -> float:
        # Local variables
        i    += 1
        chunk = self.dm['T']/n

        #  maxrt = self.dm['maxrt']
        #  minrt = self.dm['minrt']

        # Determine how much time is left over until current "time chunk" is over
        arrival_time = i*chunk

        return arrival_time
