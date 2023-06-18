"""
`schedule_util` provides shared helper files between `csv_schedule` and
`gen_schedule`. The goal being to encourage reuseable code.
"""

# Standard Library
import numpy as np

# Developed
from array_util import *

##===============================================================================
# PUBLIC

##-------------------------------------------------------------------------------
#
def genInputParams(self):
    """
    This helper function gets the input parameters for both random and CSV
    route generation.

    Input:
      - self: schedule object

    Output:
      - NONE
    """
    ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Local Variables
    init = self.init

    ## Evaluate charger parameters
    slow_chargers = np.array(np.repeat([init['chargers']['slow']['rate']],
                                       int(init['chargers']['slow']['num'])),
                             dtype=int)
    fast_chargers = np.array(np.repeat([init['chargers']['fast']['rate']],
                                       int(init['chargers']['fast']['num'])),
                             dtype=int)
    ## Helper variables
    type    = self.schedule_type                                                # random or csv
    r       = np.concatenate((slow_chargers, fast_chargers))                    # Charge rates
    epsilon = r.copy()                                                          # Usage cost

    self.dm['T']     = init['time']['EOD'] - init['time']['BOD']                # Time horizon

    # If the routes are randomly generated
    if type == 'random':
        self.dm['A']     = init['buses']['num_bus']                             # Number of buses
        self.dm['N']     = init['buses']['num_visit']                           # Number of bus visits
        self.dm['maxr']  = init['buses']['max_rest']                            # Maximum rest time between bus routes
        self.dm['minr']  = init['buses']['min_rest']                            # Minimum rest time between bus routes
        self.dm['tk']    =  np.array([i*self.dm['dt'] for i in range(0,self.dm['K'])]) # Discrete time step size

    self.dm['K']     = init['time']['K']                                        # Total number of discrete steps
    self.dm['Q']     = init['chargers']['slow']['num'] + init['chargers']['fast']['num'] # Number of chargers
    self.dm['alpha'] = initArray(self.dm['A'], dtype=float)                     # Initial charge percentages
    self.dm['beta']  = initArray(self.dm['N'], dtype=float)                     # Final charge percentages
    self.dm['dt']    = self.dm['T']/self.dm['K']                                # Calculate discrete time step
    self.dm['e']     = epsilon                                                  # Cost of use for charger q
    self.dm['kappa'] = np.repeat(init['buses']['bat_capacity'], self.dm['A'])   # Battery capacity of each bus
    self.dm['m']     = [1000*x for x in range(int(self.dm['Q']))]               # Cost of assignment for charger q
    self.dm['nu']    = init['buses']['min_charge']                              # Minimum charge allowed on next visit
    self.dm['r']     = r                                                        # Charge rate for bus q
    self.dm['s']     = np.repeat(init['buses']['bus_length'], self.dm['N'])     # Length of a bus
    self.dm['zeta']  = np.repeat([init['buses']['dis_rate']], self.dm['A'])     # Discharge rate

    # Plotting info
    self.dm.set('fast', init['chargers']['fast']['num'])                        # Set number of fast chargers
    self.dm.set('slow', init['chargers']['slow']['num'])                        # Set number of slow chargers

    return

##------------------------------------------------------------------------------
#
def genNextVisit(self, bus_data: np.ndarray) -> np.ndarray:
    """
     Input:
       bus_data: List of bus information

     Output:
       Gamma: List of id's for each visit
        """
    Gamma         = [i['id'] for i in bus_data]
    return Gamma

##------------------------------------------------------------------------------
#
def determineNextVisit(self, Gamma: np.ndarray) -> np.ndarray:
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

##------------------------------------------------------------------------------
#
def determineInitCharge(self, Gamma: np.ndarray, initial_charges: np.ndarray) -> np.ndarray:
    """
     Randomly assign inital charges that range from min to max

     Input:
       - initial_charges: Contains min and max charge percentages
       - bat_capacity   : Battery capacity for bus 'a'

     Output:
       - alpha: Initial charge percentage for bus 'a'
    """
    # Local variables
    init_charge = lambda: np.random.uniform(initial_charges['min'], initial_charges['max'])
    alpha       = np.zeros(self.dm['N'], dtype=float)

    # Loop through bus
    for a in range(self.dm['A']):
        ## For each first visit, assign an inital charge percentage
        alpha[first(Gamma, a)] = init_charge()

    return alpha

##------------------------------------------------------------------------------
#
def determineFinalCharge(self, gamma: np.ndarray,
                           final_charge: float) -> np.ndarray:
    """
    Assign final charge percentage at the correct index in array of
    N arrivals

    Input:
      - Gamma: Array of bus id's for each visit
      - gamma: Array of indices for next bus arrival
      - final_charge:

    Output:
      - beta: Array of final charge percentages for bus 'a'
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

##------------------------------------------------------------------------------
#
def applyParam(self, bus_data: np.ndarray, info: str) -> np.ndarray:
    """
        Apply the departure times for visit 'i' in the tau array

        Input:
          -  bus_data: List of information for each bus visit (See bus_data.py)
                       info: String specifying the data to extract from bus_data

        Output:
           - arr: Array of bus_data elements in Gamma order
    """
    return np.array([b[info] for b in bus_data])

##------------------------------------------------------------------------------
#
def saveParams(self, d_path: str="data"):
    """
    Save the generated schedule parameters to disk

    Input:
      - NONE

    Output:
       - Ouput parameters to 'data/input_vars.npy'
    """
    # Save data for furture runs
    np.save(d_path+'/input_vars.npy', self.dm.m_params)
    return
