# Standard Library
import csv
import numpy as np
import yaml

# Developed Modules
from data_manager import DataManager

##===============================================================================
#
class QuinModified:
    ##==========================================================================
    # STATIC
    BOD = 0.0                                                                   # Beginning of working day
    EOD = 24.0                                                                  # End of working day

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
        self.__genDecisionVars()                                                # Generate decision variables
        self.routes = self.__sortRoutes(routes)                                 # Sort routes by start time
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
        c   = self.dm['c']                                                      # Detatch time
        eta = self.dm['eta']                                                    # Charge at start of visit
        f   = self.init['chargers']['fast']['num']                              # Number of fast chargers
        g   = self.dm['g']                                                      # p_i * w_iq
        i   = 0                                                                 # Index
        k   = self.dm['kappa']                                                  # Battery capacity
        p   = self.dm['p']                                                      # c_i - u_i
        s   = self.init['chargers']['slow']['num']                              # Number of slow chargers
        u   = self.dm['u']                                                      # Initial charge times
        v   = self.dm['v']                                                      # Active charger
        w   = self.dm['w']                                                      # Active charger
        first_visit = [True]*self.dm['A']                                       # List of first visit to initialize
        charge = [True]*self.dm['A']                                            # Track the charges of the buses

        # For each route
        for r in self.route:
            id  = r['id']                                                       # ID
            dis = r['dis']                                                      # Discharge

            ## Set initial charge for first visit
            if first_visit[id]:
                first_visit[id] = False                                         # Remove flag
                eta[i]          = k*a - dis                                     # Initial charge
            # Else if the charge is below 60%, prioritize it to fast
            elif charge[id] < 0.6*k:
                self.__prioritizeFast(charge[id], v, u, c)
            # Else if prioritize to slow, fast if no slow
            elif charge[id] >= 0.6*k and charge[id] < 0.75*k:
                self.__prioritizeSlow(charge[id], v, u, c)
            # Else if only use slow
            elif charge[id] <= 0.75*k and charge[id] < 0.9*k:
                self.__onlySlow(charge[id], v, u, c)
            # Else if, don't charge
            elif charge[id] >= 0.9*k:
                continue                                                        # Don't do anything

            ## Update
            charge[id] = eta[i]                                                 # Update charge for bus b
            i         += 1                                                      # Update index

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

        self.dm['N']     = self.__countVisits(self.init, routes)                # Number of visits

        return routes

    ##--------------------------------------------------------------------------
    #
    def __countVisits(self, init, routes):
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
            if r['route'][0] > QuinModified.BOD:
                N += 1                                                              # Increment the visit counter
                # If the bus arrives before the end of the working day
                if r['route'][-1] < QuinModified.EOD:
                    N += 1                                                              # Increment the visit counter
        return N

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
        N = self.dm['N']
        Q = self.dm['Q'] = self.init['chargers']['fast']['num'] + self.init['chargers']['slow']['num']

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

    ##---------------------------------------------------------------------------
    #
    def __prioritizeFast(self, eta, v, u, c):
        """
        Charger assignment that prioritizes fast chargers

        Input
          - eta : current charge
          - v   :

        Output
        """
        return

    ##---------------------------------------------------------------------------
    #
    def __prioritizeSlow(self, eta, v, u, c):
        """
        Charger assignment that prioritizes slow chargers

        Input

        Output
        """
        return

    ##---------------------------------------------------------------------------
    #
    def __onlySlow(self, eta, v, u, c):
        """
        Charger assignment that only assigns to slow chargers

        Input

        Output
        """
        return
