# Standard Library
import csv

# Developed
from schedule_util import *

##===============================================================================
# STATIC
BOD = 0                                                                         # Beginning of working day
EOD = 86400                                                                     # End of working day

##===============================================================================
# PUBLIC

##-------------------------------------------------------------------------------
#
def genCSVRoutes(self, path: str="./data/routes.csv"):
    """
    Given the schedule object and a CSV file of routes, load the parameters and
    return a formatted set of routes to optimize over.

    Input:
      - self: schedule scheduler object
      - path: path to CSV file

    Output:
      - But routes loaded from CSV
    """

    routes = __loadCSV(path)                                                    # Load the route data from CSV
    __bufferAttributes(self, routes)                                            # Load the route attributes into
                                                                                # scheduler object
    routes = __convertRouteToVisit(routes)                                      # Convert start/end route to
                                                                                # arrival/departure
    __generateScheduleParams(self, routes)                                      # Generate route times and gammas
    return

##===============================================================================
# PRIVATE

##-------------------------------------------------------------------------------
#
def __loadCSV(path: str):
    """
    Load a CSV of bus route data and format data into an easily accessible
    format

    Input:
      - path: file path to the CSV file with bus data

    Output:
      - routes: bus route data object
    """
    # Variables
    first_row = True                                                            # Indicate the first row is being
                                                                                # processed

    with open(path, newline='') as csvfile:                                     # Open the CSV file
        routes_raw = csv.reader(csvfile, delimiter=',')
        routes     = []

        for row in routes_raw:                                                  # For each row in the csv file
            if first_row:                                                       # Ignore the first row
                first_row = False
                continue

            routes.append({'id': int(row[0]), 'route': [float(x) for x in row[1:]]}) # Append the id and routes

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
    self.dm['A'] = len(routes)                                                  # Number of buses
    self.dm['N'] = __countVisits(init, routes)                                  # Number of visits

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

    for r in routes:
        N += int((len(r['route'])) / 2)                                         # For every start/stop pair there is one
                                                                                # visit. The first column is the id, so
                                                                                # remove it
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
def  __convertRouteToVisit(routes):
    """
    Convert the start/stop representation to a arrival/departure representation
    of the route schedule.

    Input:
      - routes: CSV route data in start/stop route form

    Output:
      - routes: CSV route data in arrival/departure form
    """
    # Variables
    routes_visit = []

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
def  __generateScheduleParams(self, routes):
    """
        Generate a schedule based on the CSV file.

     Input:
       - self  : scheduler object
       - routes: CSV route data

     Output:
       - CSV generated schedule
    """

    # TODO: create gamma arrays, alpha/beta arrays, departure times, discharges (basically everything from gen_schedule:
    # __generateScheduleParams(self):)

    # Local variables
    A         : float = self.dm['A']
    N         : float = self.dm['N']
    discharge : float = 0
    id        : int   = 0
    bus_data          = []

    return
