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
    ##===========================================================================
    # PUBLIC
    ##===========================================================================

    ##---------------------------------------------------------------------------
    #
    def __init__(self):
        """
        Initialize the Quin-Modified algorithm

        Input:
          - None

        Output
           - None
        """
        self.dm     = DataManager()                                             # Get instance of data manager
        self.init   = self.__parseYAML()                                        # Get ignored routes
        self.__genDecisionVars()                                                # Generate decision variables
        self.BOD    = 0.0                                                       # Beginning of day
        self.EOD    = self.init['time']['time_horizon']                         # End of day
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

        # Unpack MILP Variables
        ## Input variables
        A   = self.dm['A']                                                      # Number of buses
        G   = self.dm['Gamma']                                                  # ID of current visit
        N   = self.dm['N']                                                      # Number of visits
        Q   = self.dm['Q']                                                      # Number of chargers
        a   = self.dm['a']                                                      # Initial charge percentage
        alp = self.dm['alpha']                                                  # Initial charge percentage
        f   = self.init['chargers']['fast']['num']                              # Number of fast chargers
        gam = self.dm['gamma']                                                  # Index of next visit for bus b
        l   = self.dm['l']                                                      # Discharge over route i
        k   = self.dm['kappa']                                                  # Battery capacity
        s   = self.init['chargers']['slow']['num']                              # Number of slow chargers
        t   = self.dm['t']                                                      # Departure time from station
        z   = self.dm['zeta']                                                   # Discharge rate for bus b

        ## Decision variables
        c   = self.c                                                            # Detatch time
        eta = self.eta                                                          # Charge at start of visit
        u   = self.u                                                            # Initial charge times
        v   = self.v                                                            # Active charger

        # Helper Variables
        first_visit = [True]*self.dm['A']                                       # List of first visit to initialize
        self.cu     = [[[self.BOD, self.EOD]] for i in range(Q)]                # Keep track of charger usage

        # For each visit
        for i in range(N):
            id  = G[i]                                                          # ID
            dis = l[i]                                                          # Discharge

            ## Set initial charge for first visit
            if alp[i] > 0:
              eta[i] = k[G[i]]*alp[i]                                           # Initial charge
              eta[gam[i]] = eta[i] - dis                                        # Next visit charge
            ## Else its a normal visit
            else:
              priority = ''

              ### If the charge is below 60%, prioritize it to fast
              if eta[i]   < 0.6*k[G[i]]                           : priority = 'fast'
              ### Else if prioritize to slow, fast if no slow
              elif eta[i] >= 0.6*k[G[i]] and eta[i] < 0.75*k[G[i]]: priority = 'slow'
              ### Else if only use slow
              elif eta[i] <= 0.75*k[G[i]] and eta[i] < 0.9*k[G[i]]: priority = 'SLOW'
              ### Else if, don't charge
              elif eta[i] >= 0.9*k[G[i]]                          : priority = '' # Don't do anything

              ## Assign bus to charger
              if priority == '':
                  eta[gam[i]], v[i], u[i], c[i] = self.__assignCharger(i, eta[i], self.cu, a[i], a[i], 'slow')
              else:
                  eta[gam[i]], v[i], u[i], c[i] = self.__assignCharger(i, eta[i], self.cu, a[i], t[i], priority)

        # Format results
        results = self.__formatResults(eta, v, u, c)

        return results

    ##===========================================================================
    # PRIVATE
    ##===========================================================================

    ##---------------------------------------------------------------------------
    # NOTE: Make this a shared util
    def __parseYAML(self, path: str="./config/schedule.yaml"):
        """
        Input:
          - NONE

        Output:
          - self.init: Parsed schedule YAML file
        """
        # Variables
        self.f = open(path, "r")
        init   = yaml.load(self.f, Loader = yaml.FullLoader)
        return init

    ##---------------------------------------------------------------------------
    #
    def __genDecisionVars(self):
        """
        Input:
          - None

        Output:
          - u   : Starting charge time
          - v   : Selected charging queue
          - c   : Detatch time fro visit i
          - p   : Amount of time spent on charger for visit i
          - g   : Linearization term for bilinear term
          - eta : Initial charge for visit i
          - w   : Vector representation of v
        """
        # Local Variables
        N = self.dm['N']         # Number of visits
        Q = self.dm['Q']         # Number of chargers

        # Generate decision variables
        self.u   = np.zeros(N)                  # Initial charge time
        self.v   = np.zeros(N, dtype=int)       # Assigned queue
        self.c   = np.zeros(N)                  # Detach time
        self.p   = np.zeros(N)                  # Charge time
        self.g   = np.zeros((N,Q), dtype=float) # Linearization term
        self.eta = np.zeros(N)                  # Initial charge
        self.w   = np.zeros((N,Q), dtype=int)   # Vector representation of queue
        return

    ##---------------------------------------------------------------------------
    #
    def __assignCharger(self, i, eta, cu, start, stop, priority):
        """
        Charger assignment that prioritizes fast chargers

        Input
          - i     : Visit index
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
        if priority == 'slow': queue = range(Q)                                 # Prioritize slow
        if priority == 'fast': queue = range(s,Q,1)                             # Prioritize fast
        if priority == 'SLOW': queue = range(0, s)                              # Only slow

        # For each of the chargers going from slow to fast
        for q in queue:
          eta, u, c, v = self.__assignBusToCharge(i, q, eta, start, stop)       # Determine charge and time
          if v >= 0: break                                                      # If a charger has been selected

        return eta, v, u, c

    ##---------------------------------------------------------------------------
    #
    def __formatResults(self, eta, v, u, c):
        """
        Format the results so that they can be plotted

        Input:
          - eta : Current charge of visit i
          - v   : Charger of interest
          - u   : Start charge time
          - c   : End charge time

        Output:
          - Update data manager with decision variables
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
            self.w[i][v[i]] = 1                                                 # Active charger
            self.g[i][v[i]] = self.dm['p'][i]                                   # Linearization term

        self.dm['w'] = self.w
        self.dm['g'] = self.g

        # Save Results
        ## Extract all the decision variable results
        d_var_results = \
                dict((k, self.dm.m_decision_var[k])
                      for k in self.dm.m_decision_var.keys()
                      if k != 'model')

        results = merge_dicts(self.dm.m_params, d_var_results)                  # Update results

        return results

    ##---------------------------------------------------------------------------
    #
    def __assignBusToCharge(self, i, q, eta, a, t):
        """
        Assign bus to charger and determine charge time

        Input
          - i   : Visit index
          - q   : Charger of interest
          - eta : Current charge
          - a   : Arrival time to station
          - t   : Departure time

        Output
          - eta : Initial charge for next visit
          - u   :
          - c   :
          - v   :
        """
        f = self.init['chargers']['fast']['num']
        s = self.init['chargers']['slow']['num']
        k = self.init['buses']['bat_capacity']                                  # Battery capacity
        r = 0
        v = -1

        # Pick a charge rate
        if q < s: r = self.init['chargers']['slow']['rate']
        else    : r = self.init['chargers']['fast']['rate']

        # Reserve spot
        u, c, v = self.__findFreeTime(a, t, q)

        # Save reservation
        ## If there has been times allotted
        if v >= 0:
          for j in self.cu[v]:
              s = j[0]                                                          # Start of free time
              e = j[1]                                                          # End of free time

              # If the allocated time is in the selected free time
              if s <= u and c <= e:
                q = self.cu[v]
                q.remove(j)                                                     # Remove current free time
                q.append([s, u])                                                # Update charger times
                q.append([c, e])
                break

          ## Calculate new charge
          if eta + r*(c - u) >= 0.9*k:
              c = (0.9*k-eta)/r + u
              #print("Amount charged: {0}".format(t))
              eta  = 0.9*k - self.dm['l'][i]
          else:
              eta = eta + r*(c - u) - self.dm['l'][i]

        return eta, u, c, v

    ##---------------------------------------------------------------------------
    #
    def __findFreeTime(self, a, t, q):
      """
      Find a time for a bus to be charged

      Input:
        - a : Arrival time
        - t : Departure time
        - q : Charger of interest

      Output:
        - u : Start charge time
        - c : End charge time
        - v : Selected bus
      """
      # Variables
      u = a
      c = t
      v = -1

      # For every assigned charge time
      for i in self.cu[q]:
          b = i[0]                                                              # Begin slot
          e = i[1]                                                              # End slot

          ## Try to find an open slot
          if (all(a < x for x in i) and all(t < x for x in i))  or \
             (all(a > x for x in i) and all(t > x for x in i)): continue

          if   b <= a and t <= e        : v = q;               break
          elif a <= b and t >= a        : u = b; v = q;        break
          elif all(x >= b for x in i) and \
               all(t >= x for x in i)   : c = e; v = q;        break
          elif a <= b and t >= e        : u = b; c = e; v = q; break

          if v >= 0: break                                                # Charger found

      return u, c, v

    ##---------------------------------------------------------------------------
    #
    def __makeReservation():
      return
