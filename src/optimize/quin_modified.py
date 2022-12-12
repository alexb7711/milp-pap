# Standard Library
import csv
import numpy as np
import yaml

# Developed Modules
from data_manager import DataManager

##===============================================================================
#
class QuinModified:
    ##===========================================================================
    # PUBLIC
    ##===========================================================================

    ##---------------------------------------------------------------------------
    #
    def __init__(self, path: str="./data/routes.csv"):
        """
        Initialize the Quin-Modified algorithm

        Input:
          - path: path to CSV file

        Output
           - None
        """
        self.dm     = DataManager()                                             # Get instance of data manager
        self.init   = self.__parseYAML()                                        # Get ignored routes
        routes      = self.__loadCSV(path)                                      # Load the route data from CSV
        self.routes = self.__sortRoutes(routes)                                 # Sort routes by start time
        gon
        return

    ##---------------------------------------------------------------------------
    #
    def optimize(self):
        """
        Generate a charging schedule based on the quin-modified algorithm

        60% < bat: Prioritize fast chargers, put on slow if no fast available
        60% < bat < 75%: Prioritize slow, put on fast if no slow
        75% < bat < 90%: Only put on slow
        90% < bat: Do not assign to a charger

        Input
          - None

        Output
          - Charging schedule
        """
        # Local Variables
        a   = self.init['initial_charge']['max']                                # Initial charge percentage
        c   = self.init['c']                                                    # Detatch time
        eta = self.init['eta']                                                  # #Charge at start of visit
        f   = self.init['fast']                                                 # Number of fast chargers
        g   = self.init['g']                                                    # p_i * w_iq
        i   = 0                                                                 # Index
        k   = self.init['kappa']                                                # Battery capacity
        p   = self.init['p']                                                    # c_i - u_i
        s   = self.init['slow']                                                 # Number of slow chargers
        u   = self.init['u']                                                    # Initial charge times
        v   = self.init['v']                                                    # Active charger
        w   = self.init['w']                                                    # Active charger
        first_visit = [True]*self.dm['A']                                       # List of first visit to initialize

        # For each route
        for r in self.route:
            id  = r['id']                                                       # ID
            dis = r['dis']                                                      # Discharge

            ## Set initial charge for first visit
            if first_visit[id]:
                first_visit[id] = False                                         # Remove flag
                eta[i]          = k*a                                           # Initial charge

            i += 1                                                              # Update index

            continue
        return

    ##===========================================================================
    # PRIVATE
    ##===========================================================================

    ##---------------------------------------------------------------------------
    #
    def __parseYAML(self, path: str="./config/schedule.yaml"):
        """
        Input:
          - NONE

        Output:
          - self.init: Parsed schedule YAML file
        """
        # Variables
        self.f   = open(path, "r")
        init     = yaml.load(self.f, Loader = yaml.FullLoader)
        return init

    ##---------------------------------------------------------------------------
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
        sec2Hr = lambda x : x/3600.0

        # Variables
        first_row = True                                                        # Indicate the first row is being
                                                                                # processed

        with open(path, newline='') as csvfile:                                 # Open the CSV file
            routes_raw = csv.reader(csvfile, delimiter=',')
            routes     = []
            id         = 0

            for row in routes_raw:                                              # For each row in the csv file
                if first_row:                                                   # Ignore the first row
                    first_row = False
                    continue

                ### If the route is not being ignored
                if int(row[0]) not in self.init['ignore']:
                    routes.append({'id': id, 'route': [sec2Hr(float(x)) for x in row[1:]]}) # Append the id and routes
                    id += 1                                                                   # Update ID

        self.dm['A'] = id+1                                                     # Save number of buses

        return routes

    ##---------------------------------------------------------------------------
    #
    def __sortRoutes(self, routes):
        """
        Sort routes by start times

        Input
          - routes : CSV route data

        Output
          - routes : Sorted routes by start time
        """
        # Variables
        route_sorted = []
        zeta = self.dm['zeta'] = self.init['buses']['dis_rate']

        # For each route for bus b
        for route in routes:
            ## For each start/stop pair
            for r in range(0,len(route['route']),2):
                route_sorted.append({'id': route['id']    ,
                              'start': route['route'][r]  ,
                              'stop': route['route'][r+1] ,
                              'dis' : zeta*(route['route'][r+1] - route['route'][r])})

        route_sorted = sorted(route_sorted, key=lambda d: d['start'])           # Sort bus data using arrival time

        print(route_sorted)

        return route_sorted

    ##---------------------------------------------------------------------------
    #
    def __genDecisionVars(self):
        """
        Input:
          - None

        Output:
          u     : Starting charge time
          v     : Selected charging queue
          c     : Detatch time fro visit i
          p     : Amount of time spent on charger for visit i
          g     : Linearization term for bilinear term
          eta   : Initial charge for visit i
          w     : Vector representation of v
        """
        # Local Variables
        N = self.init['N']
        Q = self.init['Q']

        # Generate decision variables
        ## Initial charge time
        self.dm['u'] = np.zeros(N)

        ## Assigned queue
        self.dm['v'] = np.zeros(N)

        ## Detatch time
        self.dm['c'] = np.zeros(N)

        ## Charge time
        self.dm['p'] = np.zeros(N)

        ## Lineriztion term
        self.dm['g'] = np.zeros((N,Q))

        ## Initial charge
        self.dm['eta'] = np.zeros(N)

        ## Vector representation of queue
        self.dm['w'] = np.zeros((N,Q))

        return
