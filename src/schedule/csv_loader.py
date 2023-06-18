"""
`csv_loader`  loads a CSV file of routing data and produces the input parameters.

This file is primarily accessed via `scheduler.py`
"""

# Standard Library
import csv

# Developed
from schedule_util import *

##===============================================================================
# PUBLIC

##-------------------------------------------------------------------------------
#
def genCSVRoutes(self, d_path):
    """
    Given the schedule object and a CSV file of routes, load the parameters and
    return a formatted set of routes to optimize over.

    Input:
      - self   : schedule scheduler object
      - d_path : base path to the data directory

    Output:
      - But routes loaded from CSV
    """

    # Variables
    r_path = d_path+"/routes.csv"

    routes = __loadCSV(self, r_path)                                            # Load the route data from CSV

    __bufferAttributes(self, routes)                                            # Load the route attributes into
                                                                                # scheduler object

    visits    = __convertRouteToVisit(self.init, routes)                        # Convert start/end route to
                                                                                # arrival/departure
    discharge = __calcDischarge(self, routes)                                   # Calculate the discharge
    __generateScheduleParams(self, d_path, visits, discharge)                   # Generate schedule parameters

    return

##===============================================================================
# PRIVATE

##-------------------------------------------------------------------------------
#
def __loadCSV(self, path: str):
    """
    Load a CSV of bus route data and format data into an easily accessible
    format

    Input:
      - self: Scheduler object
      - path: file path to the CSV file with bus data

    Output:
      - routes: bus route data object
    """
    # Lambda
    SEC2HR = lambda x : x/3600.0

    # Variables
    first_row = True                                                            # Indicate the first row is being
                                                                                # processed

    with open(path, newline='') as csvfile:                                     # Open the CSV file
        routes_raw = csv.reader(csvfile, delimiter=',')
        routes     = []
        id         = 0

        for row in routes_raw:                                                  # For each row in the csv file
            if first_row:                                                       # Ignore the first row
                first_row = False
                continue

            ### If the route is not being ignored
            if int(row[0]) not in self.init['ignore']:
                routes.append({'id': id, 'route': [SEC2HR(float(x)) for x in row[1:]]}) # Append the id and routes
                id += 1                                                                   # Update ID

    return routes

##-------------------------------------------------------------------------------
#
def __bufferAttributes(self, routes):
    """
    Takes the start,stop set of routes and generates routes that the scheduler
    object can understand.

    Input:
      - None

    Output:
      - set of route data to scheduler object
    """
    # Variables
    init = self.init

    # Calculate input parameters
    self.dm['A']     = len(routes)                                              # Number of buses
    self.dm['N']     = __countVisits(init, routes)                              # Number of visits
    self.dm['a']     = np.zeros(self.dm['N'], dtype=float)                      # Arrival times
    self.dm['tau']   = np.zeros(self.dm['N'], dtype=float)                      # Departure times
    self.dm['l']     = np.zeros(self.dm['N'], dtype=float)                      # Discharge for route i
    self.dm['gamma'] = np.zeros(self.dm['N'], dtype=int)                        # ID of bus for each visit
    self.dm['Gamma'] = np.zeros(self.dm['N'], dtype=int)                        # Index of next bus visit

    # Get the rest of the parameters from YAML
    genInputParams(self)                                                        # Get params from YAML

    return

##-------------------------------------------------------------------------------
#
def __countVisits(init, routes):
    """
    Counts the number of bus visits from the routes matrix.

    Input:
      - init  : Initialization parameters from YAML
      - routes: Matrix of ID and start/stop times of routes for each bus

    Output:
      - N: Number of visits
    """
    # Variables
    N = 0                                                                       # Number of visits
    BOD = init['time']['BOD']                                                   # Beginning of day
    EOD = init['time']['EOD']                                                   # End of day


    for r in routes:
        N += int((len(r['route'])) / 2)                                         # For every start/stop pair there is one
                                                                                # visit.
        # If the bus does not go on route immediately after the working day has
        # begun
        if r['route'][0] > BOD:
            N += 1                                                              # Increment the visit counter
        # If the bus arrives before the end of the working day
        if r['route'][-1] < EOD:
            N += 1                                                              # Increment the visit counter
    return N

##-------------------------------------------------------------------------------
#
def  __convertRouteToVisit(init, routes):
    """
    Convert the start/stop representation to a arrival/departure representation
    of the route schedule.

    Input:
      - init  : Initialization parameters from YAML
      - routes: CSV route data in start/stop route form

    Output:
      - routes: CSV route data in arrival/departure form
    """
    # Variables
    routes_visit = []
    BOD = init['time']['BOD']                                                   # Beginning of day
    EOD = init['time']['EOD']                                                   # End of day

    # Generate set of visit/departures
    # For each bus/route
    for route in routes:
        ## Variables
        r         = route['route']                                              # Routes for bus b
        b         = route['id']                                                 # Bus id

        J         = len(r)                                                      # Number of routes for bus
        arrival_c = r[1]                                                        # Current arrival time
        arrival_n = 0                                                           # Next arrival time
        departure = 0                                                           # Departure time
        j         = 0                                                           # Current route for bus b
        tmp_route = []                                                          # Temporary [Arrival, Depart] pair

        ## For each start/stop route pair
        for j in range(0,J,2):
            ### Update times
            departure = r[j]                                                    # Assign departure time
            arrival_n = r[j+1]                                                  # Assign next arrival time

            ### If the first visit as at the BOD
            if j == 0 and r[j] > BOD:
                tmp_route.append([BOD, departure])                              # The first arrivial is at BOD
                continue
            ### Otherwise the first visit after BOD
            elif j == 0 and r[j] == BOD:
                tmp_route.append([BOD, BOD])                                    # Put in a dummy visit to propogate discharge
                continue                                                        # The first arrival is after next route
            # Else append the arrival/departure time normally
            else:
                tmp_route.append([arrival_c, departure])                        # Append next arrival/departure pair

            ### If the final visit is not at the EOD
            if j == J-2  and r[j+1] < EOD:
                tmp_route.append([arrival_n, EOD])                              # The last visit is after final route to
                                                                                # EOD

            arrival_c = arrival_n                                               # Update the current visit for next
                                                                                # iteration

        routes_visit.append({'id': b, 'visit': tmp_route})                      # Update the visits for bus b

    return routes_visit

##-------------------------------------------------------------------------------
#
def __calcDischarge(self, routes):
    """
    Calculate the discharge for each route

    Input:
      - self  : Scheduler object
      - route : Bus routes in start/stop form

    Output:
      - discharge : Battery discharge over each visit

    """
    # Variables
    discharge = []                                                              # Discharge for each visit
    BOD       = self.init['time']['BOD']                                             # Beginning of day
    EOD       = self.init['time']['EOD']                                             # End of day

    # For each set of routes for bus b
    for route in routes:
        J             = len(route['route'])                                     # Number of routes for bus b
        b             = route['id']                                             # Bus index
        discharge_tmp = []                                                      # Discharges for bus b

        ## For each route for bus b
        for j in range(0,J,2):
            r = route['route']
            discharge_tmp.append(self.dm['zeta'][b] * (r[j+1] - r[j]))          # Calculate discharge

            ### If the final visit is not at the end of the day
            if j == J-2 and r[j+1] < EOD:
                discharge_tmp.append(0)                                         # The final route does not have a discharge

        discharge.append(discharge_tmp)                                         # Update discharges
        b += 1                                                                  # Update the bus index

    return discharge

##-------------------------------------------------------------------------------
#
def __generateScheduleParams(self, d_path, visits, discharge):
    """
    Generate a schedule based on the CSV file.

    Input
      - self      : Scheduler object
      - d_path    : Relative path to the data directory
      - visits    : Routes in arrival/departure form
      - discharge : Discharge for each bus route

    Output
      - Schedule generated from CSV
    """
    ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Variables
    bus_data        = []                                                        # Bus data to be sorted

    ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Executable code

    # Generate bus data structure for each visit
    for visit,dis in zip(visits, discharge):
        id = visit['id']                                                        # ID

        for j in range(len(visit['visit'])):
            arrival  = visit['visit'][j][0]                                     # Visit
            depart   = visit['visit'][j][1]                                     # Departure
            bd       = self.fillBusData(id, arrival, depart, dis[j])            # Update bus data
            bus_data.append(bd)

    # Sort and apply final elements to the schedule
    ## Sort bus_data by arrival times
    bus_data = sorted(bus_data, key=lambda d: d['arrival_time'])                # Sort bus data using arrival time

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

    ## Assign discharges to lambus_dataa array
    self.dm['l'] = applyParam(self, bus_data, "route_discharge")

    ## Save parameters to disk
    saveParams(self, d_path)

    return
