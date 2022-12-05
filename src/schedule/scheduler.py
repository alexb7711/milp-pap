# Standard Lib
import gurobipy as gp
import numpy as np
import random
import yaml

from gurobipy import GRB

# Developed
from array_util   import *
from bus_data     import *
from data_manager import DataManager
from pretty       import *

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
        self.init, self.run_prev = self.__parseYAML()

        # Get an instance of data manager
        self.dm = DataManager()

        # Store gurobi model
        self.model       = model

        # If a new schedule is to be generated
        if self.run_prev <= 0:
            self.__genNewSchedule()
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
        # Parse 'config/schedule.yaml'
        self.f   = open(r'./config/schedule.yaml')
        init     = yaml.load(self.f, Loader = yaml.FullLoader)

        # Parse 'config/general.yaml'
        # Parse 'config/general.yaml'
        with open(r'config/general.yaml') as f:
                file     = yaml.load(f, Loader=yaml.FullLoader)
                run_prev = file['run_prev']

        return init, run_prev

    ##---------------------------------------------------------------------------
    # Input:
    #   NONE
    #
    # Output:
    #   Schedule attributes
    #
    def __bufferAttributes(self):
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
        self.dm['Q'] = init['chargers']['slow']['num'] + init['chargers']['fast']['num']

        ## Singular charger size
        self.dm['S'] = self.dm['Q']

        ## Time horizon
        self.dm['T'] = init['time']['time_horizon']

        ## Total number of discrete steps
        self.dm['K'] = init['time']['K']

        ## Initial charge percentages
        self.dm['alpha'] = initArray(self.dm['A'], dtype=float)

        ## Final charge percentages
        self.dm['beta'] = initArray(self.dm['N'], dtype=float)

        ## Calculate discrete time step
        self.dm['dt'] = self.dm['T']/self.dm['K']

        ## Cost of use for charger q
        self.dm['e'] = epsilon

        ## Battery capacity of each bus
        self.dm['kappa'] = np.repeat(init['buses']['bat_capacity'], self.dm['A'])

        ## Cost of assignment for charger q
        self.dm['m'] = m

        ## Maximum/Minimum rest time between bus routes
        self.dm['maxr'] = init['buses']['max_rest']
        self.dm['minr'] = init['buses']['min_rest']

        ## Minimum charge allowed on next visit
        self.dm['nu'] = init['buses']['min_charge']

        ## Charge rate for bus q
        self.dm['r'] = r

        ## Length of a bus
        self.dm['s'] = np.repeat(init['buses']['bus_length'], self.dm['N'])

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
        self.dm['l'] = np.zeros(self.dm['N'], dtype=float)

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
        A         : float = self.dm['A']
        N         : float = self.dm['N']
        discharge : float = 0
        id        : int   = 0
        bus_data          = []

        # Determine amount of visits for each bus
        # http://sunny.today/generate-random-integers-with-fixed-sum/
        num_visits: np.array = np.random.multinomial(N, np.ones(A)/A, size=1)[0]

        # For each bus
        for a,n in zip(range(A),num_visits):
            ## Initialize the previous arribval/departure
            ## to hour 0 (beginning of day)
            departure_t: float = float(0)
            arrival_t_n: float = float(0)
            arrival_t_o: float = float(0)

            ## For each bus, determine all the parameters for each visit
            for i in range(n):
                ### Set the old arrival time equal to the new arrival time
                arrival_t_o = arrival_t_n

                ### Determine if this visit is the final visit
                final_visit = True if i == n-1 else False

                ### Select a start time (<= to the max rest time)
                departure_t = self.__selectDeptTime(arrival_t_o, final_visit)

                ### Select a duration (<= to the max route time allowed)
                arrival_t_n = self.__selectNextArrivalTime(i, n)

                ## Calculate discharge
                discharge = self.__calcDischarge(id, arrival_t_n, departure_t)

                ## Append to bus_data
                bd = self.__fillBusData(id, arrival_t_o, departure_t, discharge)
                bus_data.append(bd)

            ## Update id
            id += 1

        # Sort and apply final elements to the schedule
        ## Sort bus_data by arrival times
        bus_data = sorted(bus_data, key=lambda d: d['arrival_time'])

        ## Determine gamma array
        self.dm['Gamma'] = self.__genNextVisit(bus_data)

        ## Determine Gamma array
        self.dm['gamma'] = self.__determineNextVisit(self.dm['Gamma'])

        ## Randomly assign initial charges
        self.dm['alpha'] = \
                self.__determineInitCharge(self.dm['Gamma'],
                                           self.init['initial_charge'])

        ## Assign final charges
        self.dm['beta'] = \
                self.__determineFinalCharge(self.dm['gamma'],
                                            self.init['final_charge'])

        ## Assign arrival times to arrival array
        self.dm['a'] = self.__applyParam(bus_data, "arrival_time")

        ## Assign departure times to tau array
        self.dm['t'] = self.__applyParam(bus_data, "departure_time")

        ## Assign discharges to lambda array
        self.dm['l'] = self.__applyParam(bus_data, "route_discharge")

        ## Save parameters to disk
        self.__saveParams()

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   NONE
    #
    # Output:
    #   New bus schedule
    #
    def __genNewSchedule(self):
        self.__bufferAttributes()
        self.__generateScheduleParams()
        self.__genDecisionVars()
        return

    ##---------------------------------------------------------------------------
    #
    def __saveParams(self):
        """
        Save the generated schedule parameters to disk

        Input:
            NONE

        Output:
             Ouput parameters to 'data/input_vars.npy'
        """
        # Save data for furture runs
        np.save('data/input_vars.npy', self.dm.m_params)
        return

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
        A = self.dm['A']
        N = self.dm['N']
        K = self.dm['K']
        Q = self.dm['Q']

        # Generate decision variables
        ## Initial charge time
        self.dm['u'] = self.model.addMVar(shape=N, vtype=GRB.CONTINUOUS, name="u")

        ## Assigned queue
        self.dm['v'] = self.model.addMVar(shape=N, vtype=GRB.CONTINUOUS, name="v")

        ## Detatch time
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
        maxr = self.dm['maxr']
        minr = self.dm['minr']

        if not final_visit:
            # If the next departure time is less than the time horizon use that,
            # otherwise set the departure time as the time horizon
            dept_time = \
                    prev_arrival + random.uniform(minr, maxr)                if   \
                    prev_arrival + random.uniform(minr, maxr) < self.dm['T'] else \
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
    def __selectNextArrivalTime(self, i: float, n: float) -> float:
        # Local variables
        i    += 1
        chunk = self.dm['T']/n

        # Determine when the time next time interval is over
        arrival_time = i*chunk

        return arrival_time

    ##---------------------------------------------------------------------------
    # Input:
    #   b_id       : bus id (index)
    #   arrival_t  : arrival time for bus a visit i
    #   departure_t: departure time for bus a visit i
    #
    # Output:
    #   Total amount of discharge [KWH]
    #
    def __calcDischarge(self, b_id: int, arrival_t: float, departure_t: float) -> float:
        return self.dm['zeta'][b_id]*(arrival_t - departure_t)

    ##---------------------------------------------------------------------------
    # Input:
    #   arrival_t   : Arrival time of bus a visit i
    #   departure_t : Departure time of bus a visit i
    #   discharge   : Total discharge from route
    #
    # Output:
    #   b: filled bus_info dictionary
    #
    def __fillBusData(self, id: int, arrival_t: float, departure_t: float, discharge: float) -> dict:
        # Local variables
        keys = bus_info.keys()
        data = [id, arrival_t, departure_t, departure_t - arrival_t, discharge]

        return dict(zip(keys, data))

    ##---------------------------------------------------------------------------
    # Input:
    #   bus_data: List of bus information
    #
    # Output:
    #   Gamma: List of id's for each visit
    #
    def __genNextVisit(self, bus_data: np.ndarray) -> np.ndarray:
        Gamma         = [i['id'] for i in bus_data]
        return Gamma

    ##---------------------------------------------------------------------------
    #
    def __determineNextVisit(self, Gamma: np.ndarray) -> np.ndarray:
        """
        Input:
            Gamma: Array of bus arrivals id's

        Output:
            gamma: Array of index of next bus arrival for bus a
        """

        # Local Variables
        A = self.dm['A']
        N = self.dm['N']

        ## Create gamma buffer
        gamma = -1*np.ones(N, dtype=int)

        ## Keep track of the previous index each bus arrived at
        next_idx = np.array([final(Gamma, i) for i in range(A)], dtype=int)

        ## Keep track of the first instance each bus arrives
        last_idx = next_idx.copy()

        # Loop through each bus visit
        for i in range(N-1, -1, -1):
            ## Make sure that the index being checked is greater than the first
            ## visit. If it is, set the previous index value equal to the current.
            ## In other words, index i's value indicates the next index the bus
            ## will visit.
            if i < last_idx[Gamma[i]]:
                gamma[i]           = next_idx[Gamma[i]]
                next_idx[Gamma[i]] = i

        return gamma

    ##---------------------------------------------------------------------------
    #
    def __determineInitCharge(self, Gamma: np.ndarray,
                                    initial_charges: np.ndarray) -> np.ndarray:
        """
        Randomly assign inital charges that range from min to max

        Input:
            initial_charges: Contains min and max charge percentages
            bat_capacity   : Battery capacity for bus 'a'

        Output:
            alpha: Initial charge percentage for bus 'a'
        """
        # Local variables
        init_charge = lambda: np.random.uniform(initial_charges['min'], initial_charges['max'])
        alpha       = np.zeros(self.dm['N'], dtype=float)

        # Loop through bus
        for a in range(self.dm['A']):
            ## For each first visit, assign an inital charge percentage
            alpha[first(Gamma, a)] = init_charge()

        return alpha

    ##---------------------------------------------------------------------------
    #
    def __determineFinalCharge(self, gamma: np.ndarray,
                                     final_charge: float) -> np.ndarray:
        """
        Assign final charge percentage at the correct index in array of
        N arrivals

        Input:
            Gamma: Array of bus id's for each visit
            gamma: Array of indices for next bus arrival
            final_charge:

        Output:
            beta: Array of final charge percentages for bus 'a'
        """

        # Local variables
        beta = np.zeros(self.dm['N'], dtype=float)

        # Loop through each visit
        for i in range(self.dm['N']):
            ## If it is the last visit for bus 'a', update the final charge
            ## percentage
            if gamma[i] == -1:
                beta[i] = final_charge

        return beta

    ##---------------------------------------------------------------------------
    #
    def __applyParam(self, bus_data: np.ndarray, info: str) -> np.ndarray:
        """
        Apply the departure times for visit 'i' in the tau array

        Input:
            bus_data: List of information for each bus visit (See bus_data.py)
            info: String specifying the data to extract from bus_data

        Output:
            arr: Array of bus_data elements in Gamma order
        """
        return np.array([b[info] for b in bus_data])
