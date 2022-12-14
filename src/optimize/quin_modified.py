# Standard Library
import csv
import numpy as np
import yaml

from operator import itemgetter

# Developed Modules
from data_manager import DataManager
from dict_util    import *

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
        # Variables
        results = []

        # MILP Variables
        N   = self.dm['N']
        Q   = self.dm['Q']
        a   = self.init['initial_charge']['max']                                # Initial charge percentage
        f   = self.init['chargers']['fast']['num']                              # Number of fast chargers
        i   = 0                                                                 # Index
        k   = self.init['buses']['bat_capacity']                                # Battery capacity
        s   = self.init['chargers']['slow']['num']                              # Number of slow chargers

        c   = self.dm['c']                                                      # Detatch time
        eta = self.dm['eta']                                                    # Charge at start of visit
        u   = self.dm['u']                                                      # Initial charge times
        v   = self.dm['v']                                                      # Active charger

        # Helper Variables
        first_visit  = [True]*self.dm['A']                                      # List of first visit to initialize
        charge       = [0]*self.dm['A']                                         # Track the charges of the buses
        self.charger_use  = [[[0.0, QuinModified.EOD]]]*Q                         # Keep track of charger usage

        #input(self.charger_use)

        # For each route
        for r in self.routes:
            id  = r['id']                                                       # ID
            dis = r['dis']                                                      # Discharge

            ## Set initial charge for first visit
            if first_visit[id]:
                first_visit[id] = False                                         # Remove flag
                eta[i]          = k*a - dis                                     # Initial charge
                charge[id]      = eta[i]
            else:
              priority = ''

              # Discharge after route
              charge[id] -= dis

              # If the charge is below 60%, prioritize it to fast
              if charge[id] < 0.6*k                           : priority = 'fast'
              # Else if prioritize to slow, fast if no slow
              elif charge[id] >= 0.6*k and charge[id] < 0.75*k: priority = 'slow'
              # Else if only use slow
              elif charge[id] <= 0.75*k and charge[id] < 0.9*k: priority = 'SLOW'
              # Else if, don't charge
              elif charge[id] >= 0.9*k                        : continue        # Don't do anything

              ## Assign bus to charger
              eta[i], v[i], u[i], c[i] = self.__assignCharger(charge[id], self.charger_use, r['pstop'], r['start'], priority)

            ## Update
            charge[id] = eta[i]                                                 # Update charge
            i         += 1                                                      # Update index

        # Format results
        results = self.__formatResults(eta, v, u, c)

        return results

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

            ## For each row in the csv file
            for row in routes_raw:
                if first_row:                                                   # Ignore the first row
                    first_row = False
                    continue

                ### If the route is not being ignored
                if int(row[0]) not in self.init['ignore']:
                    routes.append({'id': id, 'route': [sec2Hr(float(x)) for x in row[1:]]}) # Append the id and routes
                    id += 1                                                     # Update ID

        self.dm['A'] = id+1                                                     # Save number of buses
        self.dm['N'] = self.__countVisits(self.init, routes)                    # Number of visits

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
        N = 0                                                                   # Number of visits

        for r in routes:
            N += int((len(r['route'])) / 2)                                     # For every start/stop pair there is one
                                                                                # visit.

            if r['route'][0] > QuinModified.BOD:
                N += 1                                                          # Increment the visit counter
                # If the bus arrives before the end of the working day
                if r['route'][-1] < QuinModified.EOD:
                    N += 1                                                      # Increment the visit counter
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
            J = len(route['route'])                                             # Number of routes for bus b
            p_stop = QuinModified.BOD                                           # Keep track of the previos arrival time
            start  = 0

            ## If the first route is at the beginning of the day
            if route['route'][0] == QuinModified.BOD:
                p_stop = route['route'][1]                                      # The first visit is after first route
                start  = 2

            ## For each start/stop pair
            for r in range(start,J,2):
                ### If the final visit is before the EOD
                if r == J-2 and route['route'][r+1] < QuinModified.EOD:
                    route_sorted.append({'id'    : route['id']               ,
                                         'start' : QuinModified.EOD          ,
                                         'stop'  : QuinModified.EOD          ,
                                         'pstop' : p_stop                    ,
                                         'rest'  : QuinModified.EOD - p_stop ,
                                         'dis'   : 0.0})
                ### Otherwise
                else:
                    route_sorted.append({'id'    : route['id']                ,
                                         'start' : route['route'][r]          ,
                                         'stop'  : route['route'][r+1]        ,
                                         'pstop' : p_stop                     ,
                                         'rest'  : route['route'][r]-p_stop   ,
                                         'dis'   : zeta*(route['route'][r+1] - route['route'][r])})


                p_stop = route['route'][r+1]                                    # Update previous route

        #input(route_sorted)

        route_sorted = sorted(route_sorted, key=lambda d: d['start'])           # Sort bus data using arrival time

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
        self.dm['v'] = np.zeros(N, dtype=int)

        ## Detatch time
        self.dm['c'] = np.zeros(N)

        ## Charge time
        self.dm['p'] = np.zeros(N)

        ## Linearization term
        self.dm['g'] = np.zeros((N,Q), dtype=float)

        ## Initial charge
        self.dm['eta'] = np.zeros(N)

        ## Vector representation of queue
        self.dm['w'] = np.zeros((N,Q), dtype=int)

        return

    ##---------------------------------------------------------------------------
    #
    def __assignCharger(self, eta, cu, start, stop, priority):
        """
        Charger assignment that prioritizes fast chargers

        Input
          - eta   : Current charge
          - cu    : Charger usage
          - start : Start rest time
          - stop  : Stop rest time

        Output
          - eta : Current charge
          - v   : Set of available chargers
          - u   : Start charge time
          - c   : Stop charge time
        """
        # Variables
        f     = self.init['chargers']['fast']['num']
        s     = self.init['chargers']['slow']['num']
        Q     = self.dm['Q']
        queue = []
        v     = -1
        u = c = 0

        # Set up search priority
        if priority == 'slow': queue = range(Q)                                  # Prioritize slow
        if priority == 'fast': queue = range(Q-1, -1,-1)                            # Prioritize fast
        if priority == 'SLOW': queue = range(0, s)                               # Only slow

        # For each of the chargers going from slow to fast
        for i in queue:
          eta, u, c, v = self.__assignBusToCharge(i, eta, start, stop)           # Determine charge and time
          if v >=0: break                                                        # If a charger has been selected

        return eta, v, u, c

    ##---------------------------------------------------------------------------
    #
    def __formatResults(self, eta, v, u, c):
        """
        Format the results so that they can be plotted
        """
        # Variables
        N   = self.dm['N']
        Q   = self.dm['Q']

        # Update data manager
        self.dm['c']   = c                                                      # Detatch time
        self.dm['eta'] = eta                                                    # Charge at start of visit
        self.dm['u']   = u                                                      # Initial charge times
        self.dm['v']   = [int(x) for x in v]                                    # Active charger

        self.dm['p'] =  [self.dm['c'][i] - self.dm['u'][i] for i in range(N)]   # c_i - u_i

        for i in range(N):
          if v[i] > 0:
            print("Value of v: {0}".format(v[i]))
            self.dm['w'][i][v[i]] = 1                                           # Active charger
            self.dm['g'][i][v[i]] = self.dm['p'][i]                             # Linearization term

        # Save Results
        ## Extract all the decision variable results
        d_var_results = \
                dict((k, self.dm.m_decision_var[k])
                      for k in self.dm.m_decision_var.keys()
                      if k != 'model')

        results = merge_dicts(self.dm.m_params, d_var_results)                  # Update results

        # input(results)

        return results

    ##---------------------------------------------------------------------------
    #
    def __assignBusToCharge(self, q, eta, start, stop):
        """
        Assign bus to charger and determine charge time

        Input

        Output
          - eta :
          - u   :
          - c   :
          - v   :
        """
        f = self.init['chargers']['fast']['num']
        s = self.init['chargers']['slow']['num']
        k = self.init['buses']['bat_capacity']                                  # Battery capacity
        r = -1
        v = -1

        # Pick a charge rate
        if q < s: r = self.init['chargers']['slow']['rate']
        else    : r = self.init['chargers']['fast']['rate']

        # Reserve spot
        # For each charger, try to find a spot to reserve
        for queue in self.charger_use:
            ## For every assigned charge time
            for i in queue:
                b = i[0]                                                        # Begin slot
                e = i[1]                                                        # End slot

                ### Try to find an open slot
                if   start < b and stop < e: start = b; v = q; break
                elif start > b and stop > e: stop  = e; v = q; break
                elif start < b and stop > e: start = b; stop = e; v = q; break

            if v >= 0: break                                                    # Charger found

        # Save reservation
        ## If there has been times allotted
        for q in self.charger_use:
          for i in q:
              s = i[0]                                                          # Start of free time
              e = i[1]                                                          # End of free time

              # If the allocated time is in the selected free time
              if s <= start and stop <= e:
                q.remove(i)                                                     # Remove current free time
                print("remove {0} - {1}".format(i,q))
                q.append([s, start])                                            # Update charger times
                print("append {0} - {1}".format([s, start], q))
                q.append([stop, e])
                print("append {0} - {1}".format([stop, e], q))
                q.sort(key = lambda q: q[0])
                print("free times are: {0}".format(q))
                break

        ## If this is the first time slot being allotted
        if not self.charger_use:
          self.charger_use.append([0,start])                                    # Free from BOD to start
          self.charger_use.append([stop, QuinModified.EOD])                     # Free from end to EOD

        # Calculate new charge
        if eta + r*(stop - start) >= 0.9*k:
            stop = (k-eta)/r + start
            eta  = 0.9*k
        else:
            eta = eta + r*(stop - start)

        input("(eto, u, c, v): {0},{1},{2},{3}".format(eta, start, stop, v))

        return eta, start, stop, v
