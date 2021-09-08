# Standard Lib
import gurobipy as gp
import numpy as np
import random

from gurobipy import GRB

# Developed
from array_util import *

##===============================================================================
#
class Schedule:
    ##===========================================================================
    # PUBLIC

    ##---------------------------------------------------------------------------
    # Input:
    #   T       : Time horizon
    #   N       : Number of bus visits
    #   A       : Amount of vehicles
    #   Q       : Amount of chargers
    #   H_final : Required final charge time for all buses
    #   H_min   : Required minimum charge after each visit
    #   model   : Gurobi model
    #
    def __init__(self,
                 model,
                 A              = 2,
                 H_final        = 0.95,
                 H_min          = 0.25,
                 N              = 6,
                 #  N              = 3,
                 Q              = 2,
                 T              = 16,
                 discharge_rate = np.array([2, 2, 2, 2, 2, 2], dtype=float),
                 e              = np.array([3, 6], dtype=int),
                 m              = np.array([5, 10], dtype=int),
                 max_route_time = 3,
                 r              = np.array([3, 6], dtype=int)):

        self.A       = A
        self.H_final = H_final        # [%]
        self.H_min   = H_min          # [%]
        self.N       = N
        self.Q       = Q
        self.T       = T              # [hr]
        self.dis_rat = discharge_rate # [kwh]
        self.e       = e
        self.m       = m
        self.mrt     = max_route_time # [hr]
        self.r       = r              # [kwh]

        self.model   = model

        # Arrays to be generated
        ## Arrival time
        self.a     = np.zeros(N, dtype=float)

        ## Departure time
        self.t     = -1*np.ones(N, dtype=float)

        ## Discharge for route i
        self.l     = np.zeros(N, dtype=float)

        ## Initial charge for each visit
        self.kappa = np.zeros(A, dtype=float)

        ## Minimum final charge for each visit
        self.xi    = np.zeros(A, dtype=float)

        ## ID of bus for each visit
        self.gamma = -1*np.ones(N, dtype=int)

        ## Index of next bus visit
        self.Gamma = -1*np.ones(N, dtype=int)

        ## Index of final bus visit
        self.final_arr = -1*np.ones(A, dtype=int)

        return

    ##---------------------------------------------------------------------------
    #
    def generate(self):
        # Generate Input Variables
        ## Generate arrival times
        self.__genArrival()

        ## Generate ID's for bus each bus visit
        self.__genID()

        ## Generate the next bus visit array
        self.__genNextVisit()

        ## Generate time of departure
        self.__genDepart()

        ## Generate initial charges
        self.__genInitCharge()

        ## Generate discharge amounts
        self.__genDischarge()

        ## Generate the final arrival index for each bus
        self.__genFinalArrival()

        # Generate decision variables
        # TODO: Put gurobi var generation in own function
        ## Initial charge time
        u = self.model.addMVar(shape=self.N, vtype=GRB.CONTINUOUS, name="u")

        ## Assigned queue
        v = self.model.addMVar(shape=self.N, vtype=GRB.CONTINUOUS, name="v")

        ## Detatch tiself.model.
        c = self.model.addMVar(shape=self.N, vtype=GRB.CONTINUOUS, name="c")

        ## Charge tiself.model.
        p = self.model.addMVar(shape=self.N, vtype=GRB.CONTINUOUS, name="p")

        ## Lineriztion term
        g = self.model.addMVar(shape=self.N*self.Q, vtype=GRB.CONTINUOUS, name="g")

        ## Initial charge
        eta = self.model.addMVar(shape=self.N, vtype=GRB.CONTINUOUS, name="eta")

        ## Vector representation of queue
        #  w = self.model.addMVar(shape=self.N*self.Q, vtype=GRB.BINARY, name="w")
        w = self.model.addMVar(shape=self.N*self.Q, vtype=GRB.CONTINUOUS, name="w")

        ## Sigma
        #  sigma = self.model.addMVar(shape=self.N*(self.N-1), vtype=GRB.BINARY, name="sigma")
        sigma = self.model.addMVar(shape=self.N*(self.N-1), vtype=GRB.CONTINUOUS, name="sigma")

        ## Delta
        #  delta = self.model.addMVar(shape=self.N*(self.N-1), vtype=GRB.BINARY, name="delta")
        delta = self.model.addMVar(shape=self.N*(self.N-1), vtype=GRB.CONTINUOUS, name="delta")

        # Compile schedule into dictionary
        schedule = \
        {
            ## Input Variables
            'A'     : self.A,
            'Gamma' : self.Gamma,
            'H_f'   : self.H_final,       # [%]
            'N'     : self.N,
            'Q'     : self.Q,
            'S'     : 1.0,
            'T'     : self.T,
            'a'     : self.a,
            'e'     : self.e,
            'fa'    : self.final_arr,
            'gamma' : self.gamma,
            'kappa' : self.kappa,
            'l'     : self.l,
            'm'     : self.m,
            'r'     : self.r,
            't'     : self.t,
            'xi'    : self.xi,

            ## Decision Variables
            'c'     : c,
            'delta' : delta,
            'eta'   : eta,
            'g'     : g,
            'p'     : p,
            'sigma' : sigma,
            'u'     : u,
            'v'     : v,
            'w'     : w,

            # Model
            'model' : self.model,
        }

        return schedule

    ##===========================================================================
    # PRIVATE

    ##---------------------------------------------------------------------------
    #
    def __genDecisionVars(self):

        return

    ##---------------------------------------------------------------------------
    #
    def __genArrival(self):
        min = 0

        for i in range(self.N):
            max       = \
                (min + self.mrt) if (min+self.mrt) < self.T else self.T
            self.a[i] = min + (max - min)*random.random()
            min       = self.a[i]

        print ("a: \n", self.a)
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

        # Generate random id's for each visit, but don't allow two of the same
        # id's in a row
        for i in range(self.N):
            while True:
                self.Gamma[i] = random.randint(0, self.A-1)

                if self.Gamma[i] != prev_id:
                    prev_id = self.Gamma[i];
                    break

        print("Gamma: \n", self.Gamma)

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
            if self.gamma[i] > 0:
                max       = abs(self.a[self.gamma[i]])
                min       = self.a[i]
                self.t[i] = min + (max - min)*random.random()
            else:
                self.t[i] = self.T

        print("tau:\n ", self.t)

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
        for i in range(self.N-1, -1, -1):
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
    #   kappa[A] : Initial charges for each bus
    #
    def __genInitCharge(self):
        min = 50
        max = 99

        self.kappa = np.zeros(self.N, dtype=int)

        for i in range(self.A):
                idx = first(self.Gamma, i)
                self.kappa[idx] = min + (max - min)*random.random()
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
        for i in range(self.N):
            if self.gamma[i] > 0:
                self.l[i] = self.dis_rat[self.Gamma[i]] * (self.t[i] - self.a[i])

        #  print("Discharge:\n ", self.l)
        return

    ##---------------------------------------------------------------------------
    # Input:
    #   N     : Number of visits
    #   Gamma : List of ID'ss for each visit
    #
    # Output:
    #   final_arr: List of indices for the final arrival for each bus
    #
    def __genFinalArrival(self):
        for i in range(self.A):
            self.final_arr[i] = final(self.Gamma, i)

        return
