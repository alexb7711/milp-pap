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
    __generateScheduleParams(self)                                              # Generate route times and gammas
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

            routes.append({'id': row[0], 'route': [float(x) for x in row[1:]]}) # Append the id and routes

    return routes

##-------------------------------------------------------------------------------
#
def __attributesToScheduler(self, routes):
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

    genInputParams(self)                                                        # Get params from YAML
    self.dm['A'] = len(routes)                                                  # Number of buses
    self.dm['N'] = __countVisits(init, routes)                                  # Number of visits

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
def  __generateScheduleParams(self):
        """
        Generate a schedule based on the CSV file.

     Input:
       - self: scheduler object

     Output:
       - CSV generated schedule
        """

    # TODO: create gamma arrays, alpha/beta arrays, departure times, discharges (basically everything from gen_schedule:
    # __generateScheduleParams(self):)
    return
