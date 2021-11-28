# Standard Lib
import gurobipy as gp
import numpy as np
import random

from gurobipy import GRB

# Developed
from array_util import *
from pretty import *

##===============================================================================
#
class Schedule:
    ##===========================================================================
    # PUBLIC

    ##---------------------------------------------------------------------------
    # Input:
    #   A     : Amount of vehicles
    #   N     : Number of bus visits
    #   Q     : Amount of chargers
    #   T     : Time horizon
    #   beta  : Required final charge time for all buses
    #   model : Gurobi model
    #   nu    : Required minimum charge after each visit
    #
    def __init__(self,
                 model,
                 A              = 2,
                 nu             = 0.25,
                 N              = 9,
                 Q              = 9,
                 T              = 24,
                 max_rest_time  = 0.25):

        # Create list of discharge rates
        discharge_rate = np.repeat([5], A)

        # Evaluate charger parameters
        #  r              = np.random.randint(100,high=450,size=int(Q))
        r              = np.array([100, 100, 100, 100, 100, 450, 450, 450, 450])
        e              = r.copy()
        m              = r.copy()

        # Store Input Parameters
        self.A       = int(A)
        self.N       = int(N)
        self.Q       = int(Q)
        self.T       = int(T)         # [hr]
        self.dis_rat = discharge_rate # [kwh]
        self.e       = e
        self.m       = m
        self.mrt     = max_rest_time # [hr]
        self.nu      = nu             # [%]
        self.r       = r

        # Store Gurobi Model
        self.model   = model

        # Arrays to be generated
        ## Arrival time
        self.a     = np.zeros(N, dtype=float)

        ## Departure time
        self.t     = -1*np.ones(N, dtype=float)

        ## Discharge for route i
        self.l     = np.zeros(N, dtype=float)

        ## Initial charge for each visit
        self.alpha = np.zeros(N, dtype=float)

        ## ID of bus for each visit
        self.gamma = -1*np.ones(N+A, dtype=int)

        ## Index of next bus visit
        self.Gamma = -1*np.ones(N, dtype=int)

        ## Index of final bus visit
        self.beta = -1*np.ones(N, dtype=int)

        return

    ##---------------------------------------------------------------------------
    #
    def generate(self):
        # Generate Input Variables
        ## Generate arrival times
        self.__genArrival()

        ## Generate ID's for bus each bus visit
        self.__genID()

        ## Generate initial charges
        self.__genInitCharge()

        ## Generate bus capacities
        self.__genCapacities()

        ## Generate the final arrival index for each bus
        self.__genFinalCharge()

        # Decision Variables
        self.__genDecisionVars()

        # Add fake final state
        self.__genFinalStates()

        ## Generate the next bus visit array
        self.__genNextVisit()

        ## Generate time of departure
        self.__genDepart()

        ## Generate discharge amounts
        self.__genDischarge()

        # Compile schedule into dictionary
        schedule = \
        {
            ## Input Variables
            'A'     : self.A,
            'Gamma' : self.Gamma,
            'N'     : self.N,
            'Q'     : self.Q,
            'S'     : self.Q,
            'T'     : self.T,
            'a'     : self.a,
            'alpha' : self.alpha,
            'beta'  : self.beta,       # [%]
            'e'     : self.e,
            'gamma' : self.gamma,
            'kappa' : self.kappa,
            'l'     : self.l,
            'm'     : self.m,
            'nu'    : self.nu,
            'r'     : self.r,
            's'     : np.ones(self.N*self.A,dtype=int),
            't'     : self.t,

            ## Decision Variables
            'c'     : self.c,
            'delta' : self.delta,
            'eta'   : self.eta,
            'g'     : self.g,
            'p'     : self.p,
            'sigma' : self.sigma,
            'u'     : self.u,
            'v'     : self.v,
            'w'     : self.w,

            # Model
            'model' : self.model,
        }

        return schedule

    ##===========================================================================
    # PRIVATE

    ##---------------------------------------------------------------------------
    #
    def __genArrival(self):
        min = 0.1

        # Loop through all bus visits
        for i in range(self.N):
            if i < self.A:
                self.a[i] = min
            else:
                max       = \
                    (min + self.mrt) if (min+self.mrt) < self.T else self.T
                self.a[i] = min + (max - min)*random.random()
                min       = self.a[i]

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   N: Number of visits
    #   A: Amount of buses
    #
    # Output:
    #   Gamma: List of ID's for each visit
    #
    def __genID(self):
        prev_id = None
        skipped = np.zeros(self.A)

        # Generate random id's for each visit, but don't allow two of the same
        # id's in a row
        for i in range(self.N):
            if i < self.A:
                self.Gamma[i] = i
            else:
                while True:
                    self.Gamma[i] = random.randint(0, self.A-1)

                    if self.Gamma[i] != prev_id and skipped[self.Gamma[i]] > 2:
                            prev_id                = self.Gamma[i];
                            skipped[self.Gamma[i]] = 0
                    else:
                        skipped[self.Gamma[i]] += 1

                    break
        return

    ##---------------------------------------------------------------------------
    # Input:
    #   N     : Number of visits
    #   A     : Number of buses
    #   Gamma : List of ID's for each visit
    #   gamma : List of index for the next visit
    #   a     : List of arrival times
    #
    # Output:
    #   t: List of departure times for each bus visit
    #
    def __genDepart(self):
        for i in range(self.N):
            ## If the bus has another visit
            if self.gamma[i] > 0 and i != lastVisit(self.Gamma, self.Gamma[i]):
                #  max       = self.a[i+1]
                max       = self.a[self.gamma[i]]
                min       = (self.a[i] + self.a[i+1])/2
                #  min       = self.a[i]
                self.t[i] = min + (max - min)*random.random()
            else:
                self.t[i] = self.T
        return

    ##---------------------------------------------------------------------------
    # Input:
    #   N: Number of visits
    #   Gamma: List of ID's for each visit
    #
    # Output:
    #   gamma: List of index for the next visit
    #
    def __genNextVisit(self):
        # Local Variables
        ## Keep track of the previous index each bus arrived at
        next_idx  = np.array([final(self.Gamma, i) for i in range(self.A)], dtype=int)

        ## Keep track of the first instance each bus arrives
        last_idx = next_idx.copy()

        # Loop through each bus visit
        for i in range(self.N+self.A-1, -1, -1):
            ## Make sure that the index being checked is greater than the first
            ## visit. If it is, set the previous index value equal to the current.
            ## In other words, index i's value indicates the next index the bus
            ## will visit.
            if i < last_idx[self.Gamma[i]]:
                self.gamma[i]           = next_idx[self.Gamma[i]]
                next_idx[self.Gamma[i]] = i

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   A : Number of buses
    #
    # Output:
    #   alpha[N] : Initial charges for each bus
    #
    def __genInitCharge(self):
        min = 90
        max = 90

        self.alpha = -1*np.ones(self.N, dtype=float)

        for i in range(self.A):
                idx              = first(self.Gamma, i)
                self.alpha[idx]  = min + (max - min)*random.random()
                self.alpha[idx] /= 100.0

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   N     : Number of visits
    #   Gamma : List of ID's for each visit
    #   gamma : List of index for the next visist
    #   a     : List of arrival times
    #   t     : List of departure times for each bus visit
    #
    # Output:
    #   l: List of amount of discharge for each route
    #
    def __genDischarge(self):
        # Loop through each visit
        for i in range(self.N):
            ## If the route has another visit and it isnt the last one
            if self.gamma[i] > 0 and i != lastVisit(self.Gamma, self.Gamma[i]):
                if prevVisit(self.Gamma, self.Gamma[i], i) == -1:
                    self.l[i] = self.dis_rat[self.Gamma[i]] * self.a[i]
                else:
                    self.l[i] = self.dis_rat[self.Gamma[i]] * \
                            (self.a[i] - self.t[prevVisit(self.Gamma, self.Gamma[i], i)])
        return

    ##---------------------------------------------------------------------------
    # Input:
    #   A     : Number of buses
    #   Gamma : List of ID'ss for each visit
    #
    # Output:
    #   beta: List of charge values
    #
    def __genFinalCharge(self):
        final_percent = 0.95
        for i in range(self.A):
            self.beta = np.append(self.beta, final_percent)
        return

    ##---------------------------------------------------------------------------
    # Input:
    #
    # Output:
    #
    def __genCapacities(self):
        mj2kwh     = 0.277778
        #  self.kappa = np.random.randint(1396, high=1396, size=self.A)*mj2kwh # [kwh]
        self.kappa = np.repeat([1396], self.A)*mj2kwh # [kwh]

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   model: Gurobi model object
    #
    # Object:
    #   The following gurobi MVars:
    #   u     : Starting charge time
    #   v     : Selected charging queue
    #   c     : Detatch time fro visit i
    #   p     : Amount of time spent on charger for visit i
    #   g     : Linearization term for bilinear term
    #   eta   : Initial charge for visit i
    #   w     : Vector representation of v
    #   sigma : u_i < u_j
    #   delta : v_i < v_j
    #
    def __genDecisionVars(self):
        # Local Variables
        A = self.A
        N = self.N

        # Generate decision variables
        ## Initial charge time
        self.u = self.model.addMVar(shape=N+A, vtype=GRB.CONTINUOUS, name="u")

        ## Assigned queue
        self.v = self.model.addMVar(shape=N+A, vtype=GRB.CONTINUOUS, name="v")

        ## Detatch tiself.model.
        self.c = self.model.addMVar(shape=N+A, vtype=GRB.CONTINUOUS, name="c")

        ## Charge tiself.model.
        self.p = self.model.addMVar(shape=N+A, vtype=GRB.CONTINUOUS, name="p")

        ## Lineriztion term
        self.g = self.model.addMVar(shape=(N+A,self.Q), vtype=GRB.CONTINUOUS, name="g")

        ## Initial charge
        self.eta = self.model.addMVar(shape=N+self.A, vtype=GRB.CONTINUOUS, name="eta")

        ## Vector representation of queue
        self.w = self.model.addMVar(shape=(N+A,self.Q), vtype=GRB.BINARY, name="w")

        ## Sigma
        self.sigma = self.model.addMVar(shape=(N+A,N+A), vtype=GRB.BINARY, name="sigma")

        ## Delta
        self.delta = self.model.addMVar(shape=(N+A,N+A), vtype=GRB.BINARY, name="delta")

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   Gamma :
    #   a     :
    #   alpha :
    #   beta  :
    #   gamma :
    #   l     :
    #   t     :
    #
    # Output:
    #
    def __genFinalStates(self):
        # Loop through each bus
        for i in range(self.A):
            ## Add final Gamma ID's
            self.Gamma = np.append(self.Gamma, i)

            ## Add final arrival
            self.a = np.append(self.a, [self.T])

            ## Add final alpha values
            self.alpha = np.append(self.alpha, [-1])

            ## Add final l
            self.l = np.append(self.l, [0])

            ## Add final t
            self.t = np.append(self.t, [self.T])

        return
