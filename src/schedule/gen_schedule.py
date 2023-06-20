################################################################################
# Description:
# Populates the scheduler with a randomly generated bus route schedule.
################################################################################

# Standard Library
import numpy as np
import random
import yaml

# Developed
from array_util    import *
from bus_data      import *
from schedule_util import *

##==============================================================================
# PUBLIC

##------------------------------------------------------------------------------
#
def genNewSchedule(self):
    """
    Input:
      - self: schedule object

    Output:
      - Random set of bus routes

    """
    __bufferAttributes(self)                                                    # Initialize all the attributes of the
                                                                                # random bus schedule
    __generateScheduleParams(self)                                              # Generate route times and gammas
    return

##==============================================================================
# PRIVATE

##------------------------------------------------------------------------------
#
def __generateScheduleParams(self):
    """
     Input:
       - self: scheduler object

     Output:
       - Randomly generated schedule
     """
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
        ## Initialize the previous arrival/departure
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
            departure_t = __selectDeptTime(self, arrival_t_o, final_visit)

            ### Select a duration (<= to the max route time allowed)
            arrival_t_n = __selectNextArrivalTime(self, i, n)

            ## Calculate discharge
            discharge = __calcDischarge(self, id, arrival_t_n, departure_t)

            ## Append to bus_data
            bd = self.fillBusData(id, arrival_t_o, departure_t, discharge)
            bus_data.append(bd)

        ## Update id
        id += 1

    # Sort and apply final elements to the schedule
    ## Sort bus_data by arrival times
    bus_data = sorted(bus_data, key=lambda d: d['arrival_time'])

    ## Determine gamma array
    self.dm['Gamma'] = genNextVisit(self, bus_data)

    ## Determine Gamma array
    self.dm['gamma'] = determineNextVisit(self, self.dm['Gamma'])

    ## Randomly assign initial charges
    self.dm['alpha'] = determineInitCharge(self, self.dm['Gamma'],
                                           self.init['initial_charge'])

    ## Assign final charges
    self.dm['beta'] =  determineFinalCharge(self, self.dm['gamma'],
                                            self.init['final_charge'])

    ## Assign arrival times to arrival array
    self.dm['a'] = applyParam(self, bus_data, "arrival_time")

    ## Assign departure times to tau array
    self.dm['t'] = applyParam(self, bus_data, "departure_time")

    ## Assign discharges to lambda array
    self.dm['l'] = applyParam(self, bus_data, "route_discharge")

    ## Save parameters to disk
    saveParams(self)

    return

##------------------------------------------------------------------------------
#
def __bufferAttributes(self):
    """
    Input:
      - NONE

    Output:
      - Schedule attributes
    """
    ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Store Input Parameters

    genInputParams(self)

    ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

##------------------------------------------------------------------------------
#
def __selectDeptTime(self, prev_arrival: float, final_visit: bool) -> float:
    """
     Input:
       - NONE

     Output:
       - Next departure time
    """
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

##------------------------------------------------------------------------------
#
def __selectNextArrivalTime(self, i: float, n: float) -> float:
    """
    Input:
      - i: Current visit number for bus a
      - n: Total number of visits for bus a

    Output:
      - Next arrival time
    """
    # Local variables
    i    += 1
    chunk = self.dm['T']/n

    # Determine when the time next time interval is over
    arrival_time = i*chunk

    return arrival_time

##------------------------------------------------------------------------------
#
def __calcDischarge(self, b_id: int, arrival_t: float, departure_t: float) -> float:
    """
        Input:
          - b_id       : bus id (index)
          - arrival_t  : arrival time for bus a visit i
          - departure_t: departure time for bus a visit i

        Output:
          - Total amount of discharge [KWH]
        """
    return (self.dm['zeta'][b_id]*KWH2KJ)*(arrival_t - departure_t)
