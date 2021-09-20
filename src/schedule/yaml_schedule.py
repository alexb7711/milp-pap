# Standard Lib
import gurobipy as gp
import numpy as np
import yaml
import random

from gurobipy import GRB
from yaml import Loader

# Developed
from array_util import *

##===============================================================================
# NOTE!!!!
#   Currently, this module requires that all "starts" read from the YAML are > 0.
#   This is an assumption that will be dealt with at a later date.
#
class YAMLSchedule:

    ##===========================================================================
    # PUBLIC

    ##---------------------------------------------------------------------------
    # Input:
    #   file  : Path to the yaml file
    #   model : Gurobi model
    #
    def __init__(self, f, model):
        stream    = open(f, 'r')
        self.data = yaml.load(stream, Loader=Loader)

        self.model = model
        return

    ##---------------------------------------------------------------------------
    # Input:
    #   data : YAML bus route data
    #
    # Output:
    #   Schedule: The loaded schedule from yaml file
    #
    def generate(self):
        # A
        self.__countBuses()

        # Q
        self.__countChargers()

        # nu
        self.__getMinCharge()

        # r
        self.__getChargeRates()

        # m
        self.__getAssignCosts()

        # e
        self.__getUseCosts()

        # T
        self.__getTimeHorizon()

        # Group Data
        self.__groupData()

        # t
        self.__genDepartureTimes()

        # N
        self.__countVisits()

        # beta
        self.__getFinalCharge()

        # Gamma
        self.__genBusIdx()

        # gamma
        self.__genNextVisits()

        # s
        self.__genSizes()

        # lambda
        self.__calcPowerLoss()

        # alpha
        self.__getInitCharge()

        # Bus Capacities
        self.__getCapacities()

        # a
        self.__genArrivalTimes()

        # Add fake final state
        self.__genFinalStates()

        # final arrivals
        self.__genFinalArrival()

        # Decision Variables
        self.__genDecisionVars()

        schedule = \
        {
            ## Input Variables
            'A'     : self.A,
            'Gamma' : self.Gamma,
            'nu'    : self.nu,      # [%]
            'N'     : self.N,
            'Q'     : self.Q,
            'S'     : 3,
            'T'     : self.T,
            'a'     : self.a,
            'alpha' : self.alpha,
            'beta'  : self.beta,       # [%]
            'kappa' : self.capacity,   # [kwh]
            'e'     : self.e,
            'fa'    : self.final_arr,
            'gamma' : self.gamma,
            'l'     : self.l,
            'm'     : self.m,
            'r'     : self.r,
            's'     : self.s,
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
    # Input:
    #   data : YAML bus route data
    #
    # Output:
    #   A : Number of beses in system
    #
    def __countBuses(self):
        self.A = len([x for x in self.data["buses"]])
        return

    ##---------------------------------------------------------------------------
    # Input:
    #   group_data: pre-processed YAML data
    #
    # Output:
    #   N: NUmber of bus visits
    def __countVisits(self):
        self.N = len(self.gd)
        return

    ##---------------------------------------------------------------------------
    # Input:
    #   data: YAML bus route data
    #
    # Output:
    #   Q: Number of chargers in system
    #
    def __countChargers(self):
        chargers = self.data["chargers"]
        self.Q = chargers["osc"]["num"] + chargers["depot"]["num"]
        return

    ##---------------------------------------------------------------------------
    # Input:
    #
    # Output:
    #   nu: Minimum charge percentage allowed
    #
    def __getMinCharge(self):
        self.nu = 0.35
        return

    ##---------------------------------------------------------------------------
    # Input:
    #   data : YAML bus route data
    #
    # Output:
    #   List of bus capacities in [KJ]
    #
    def __getCapacities(self):
        capacities = []

        # Loop through each bus
        for i in self.data["buses"]:
            ## Store capacity in [MJ]
            capacities.append(i["battery"]["capacity"]*10)
            #  capacities.append(i["battery"]["capacity"]*1000)
            #  capacities.append(i["battery"]["capacity"]*1.5)

        self.capacity = np.array(capacities)

        #  self.capacity = np.array([capacities[x] for x in self.Gamma])

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   data: YAML bus route data
    #
    # Output:
    #   l: Discharge amount per route [KJ]
    #
    def __calcPowerLoss(self):
        l = []

        for i in range(self.N):
            if self.gd[i]["start"] < 0:
                l.append(0)
            else:
                motor_load = self.gd[i]["motor_load"]
                duration   = self.gd[i]["duration"]
                l.append(motor_load*duration)

        self.l = np.array(l)

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   data: YAML bus route data
    #
    # Output:
    #   r: Charge rate for each charger [kj]
    #
    def __getChargeRates(self):
        arr = [self.data["chargers"]["osc"]["rate"]]
        cnt = self.data["chargers"]["osc"]["num"]
        osc = np.repeat(arr, cnt)

        arr   = [self.data["chargers"]["depot"]["rate"]]
        cnt   = self.data["chargers"]["depot"]["num"]
        depot = np.repeat(arr, cnt)

        self.r = np.append(depot, osc)

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   r: Charge rate for each charger [kj]
    #
    # Output:
    #   m: Cost of assigning bus i to charger q
    #
    def __getAssignCosts(self):
        self.m = 2*self.r.copy()
        return

    ##---------------------------------------------------------------------------
    # Input:
    #   r: Charge rate for each charger [kj]
    #
    # Output:
    #   e: Cost of assigning bus i to charger q per unit time
    #
    def __getUseCosts(self):
        self.e = self.r.copy()
        return

    ##---------------------------------------------------------------------------
    # Input:
    #   group_data: pre-processed YAML data
    #
    # Output:
    #   Gamma: ID for each bus visit
    #
    def __genBusIdx(self):
        Gamma = []

        for i in self.gd:
            Gamma.append(i["id"])

        for i in range(self.A):
            ## Add final Gamma ID's
            Gamma = np.append(Gamma, i)

        self.Gamma = np.array(Gamma)

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   N: Number of visits
    #   Gamma: List of ID's for each visit
    #
    # Output:
    #   gamma: List of index for the next visit
    #
    def __genNextVisits(self):
        # Local Variables
        ## Keep track of the previous index each bus arrived at
        next_idx = np.array([final(self.Gamma, i) for i in range(self.A)], dtype=int)
        gamma    = -1*np.ones(self.N+self.A, dtype=int)

        ## Keep track of the first instance each bus arrives
        last_idx = next_idx.copy()

        # Loop through each bus visit
        for i in range(self.N+self.A-1, -1, -1):
            ## Make sure that the index being checked is greater than the first
            ## visit. If it is, set the previous index value equal to the current.
            ## In other words, index i's value indicates the next index the bus
            ## will visit.
            if i < last_idx[self.Gamma[i]]:
                gamma[i]                = next_idx[self.Gamma[i]]
                next_idx[self.Gamma[i]] = i

        self.gamma = np.array(gamma)

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   data: YAML bus route data
    #
    # Output:
    #   T: Time horizone of system
    #
    def __getTimeHorizon(self):
        self.T = self.data["sim_duration"]
        return

    ##---------------------------------------------------------------------------
    # Input:
    #   data: YAML bus route data
    #
    # Output:
    #   group_data: pre-processed data for easier generation of other required
    #               input parameters
    #
    def __groupData(self):
        group_data = []
        bus       = self.data["buses"]
        iden      = 0

        for i in bus:
            s                   = i["route"]["starts"]
            d                   = i["route"]["durations"]
            start, dur, arrival = self.__genData(s,d)

            for j in range(len(start)):
                group_data.append({"id"         : iden            , \
                                   "start"      : start[j]        , \
                                   "duration"   : dur[j]          , \
                                   "motor_load" : i["motor_load"] , \
                                   "arrival"    : arrival[j]})

            iden += 1

        self.gd = np.array(sorted(group_data, key=lambda k: k["arrival"]))

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
        self.final_arr = np.ones(self.N, dtype = int)
        final_arr      = np.ones(self.A, dtype = int)

        for i in range(self.A):
            self.final_arr[i] = final(self.Gamma, i)

        return
        # TODO: GENERATE FINAL ARR OF SIZE N
        #  for i in final_arr:


    ##---------------------------------------------------------------------------
    # Input:
    #   group_data: pre-processed YAML data
    #
    # Output:
    #   t: Required time of departure for each bus visit
    #
    def __genDepartureTimes(self):
        t = []

        for i in self.gd:
            t.append(i["start"])

        for i in range(len(t)):
            if t[i] == -1:
                t[i] = self.T

        self.t = np.array(t)

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   N: Number of bus visits
    #   Q: Number of chargers
    #
    # Output:
    #   c     : Detatch time from charger
    #   delta : Matrix representation of bus placement over space
    #   eta   : Initial charge for each bus visit
    #   g     : Linearization term for bilinear terms
    #   p     : Time spent on charger
    #   sigma : Matrix representation of bus placement over time
    #   u     : Initial time to be charged
    #   v     : Assigned queue
    #   w     : Vectorization of v
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
    #   data: YAML bus route data
    #
    # Output
    #   alpha: Initial charges for each bus
    #
    def __getInitCharge(self):
        init_charge = []

        for i in self.data["buses"]:
            init_charge.append(i["battery"]["charge"]/100.0)

        self.alpha = -1*np.ones(self.N)

        for i in range(self.A):
            self.alpha[first(self.Gamma, i)] = init_charge[i]

        return

    ##---------------------------------------------------------------------------
    # Input:
    #
    # Output:
    #   beta: Minimum final charge percentage for each bus
    def __getFinalCharge(self):
        final_percent = 0.95
        self.beta     = np.zeros(self.N)

        for i in range(self.A):
            self.beta = np.append(self.beta, final_percent)
        return

    ##---------------------------------------------------------------------------
    # Input:
    #   data: YAML bus route data
    #
    # Output:
    #   a: Arrival times for each bus visit
    #
    def __genArrivalTimes(self):
        a = []
        for i in self.gd:
            a.append(i["arrival"])

        self.a = np.array(a)

        return

    ##---------------------------------------------------------------------------
    # Input:
    #
    # Output:
    #   s: Sizes of each bus (1)
    #
    def __genSizes(self):
        self.s = np.ones(self.N+self.A)
        return

    ##---------------------------------------------------------------------------
    # Input:
    #   s: Start route times for bus i
    #   d: Duration route times for bus i
    #
    # Output:
    #   start   : Start route time for visit i
    #   dur     : Duration route time for visit i
    #   arrival : Arrival time for visit i
    #
    def __genData(self, s,d):
        start   = []
        dur     = []
        arrival = []

        for i in range(len(s)):
            if i == 0 and s[i] != 0:
                arrival.append(0)
                start.append(s[i])
                dur.append(d[i])
            elif i == len(s)-1:
                arrival.append(s[i]+d[i])
                start.append(-1)
                dur.append(-1)
            else:
                arrival.append(s[i-1]+d[i-1])
                start.append(s[i])
                dur.append(d[i])

        return start, dur, arrival

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
            ## Add final arrival
            self.a = np.append(self.a, [self.T])

            ## Add final alpha values
            self.alpha = np.append(self.alpha, [-1])

            ## Add final l
            self.l = np.append(self.l, [0])

            ## Add final t
            self.t = np.append(self.t, [self.T])

        return
