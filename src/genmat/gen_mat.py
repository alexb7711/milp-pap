#!/usr/bin/python

# Standard Lib
import numpy as np

# Developed
from mat_util   import NQMat
from array_util import *

##===============================================================================
#
class GenMat:
    ##===========================================================================
    # PUBLIC

    ##---------------------------------------------------------------------------
    # Input:
    #   schedule: Contains all the information needed to build the matrices
    #             A_eq and A_ineq.
    #               * Input Parameters:
    #                   * Gamma : List of bus ID's for each visit
    #                   * N     : Number of bus visits
    #                   * Q     : Number of chargers
    #                   * a     : List of arrival times
    #                   * e     : Cost of charger use
    #                   * eta_A : List of initial charges
    #                   * gamma : List of indexes for the next visit
    #                   * l     : List of amount of discharge for each route
    #                   * m     : Cost of assignment to charger
    #                   * t     : List of departure times
    #               * Decision Variables:
    #                   * u     : Initial charge time for each visit
    #                   * v     : Assigned queue for each bus visit
    #                   * c     : Detatch time for each visit
    #                   * p     : Time spent on charger for each bus visit
    #                   * g     : Linearization term for blinear values
    #                   * eta   : Initial charge for each bus visit
    #                   * w     : Vector representation of queue assignment
    #                   * sigma : Time representation of visits
    #                   * delta : Space representation of visits
    #
    def __init__(self, schedule):
        self.__initVars(schedule)

        # Create A_eq
        ## Create A_pack
        self.a_pack_eq, self.x_pack_eq, self.b_pack_eq = self.__APackEq()

        ## Create A_dyanmics
        self.a_dyn_eq, self.x_dyn_eq, self.b_dyn_eq = self.__ADynEq()

        # Create A_ineq
        ## Create A_pack
        #  self.a_dyn_eq, self.x_dyn_eq, self.b_dyn_eq = self.__AdynIneq()

        ## Create A_dyanmics
        #  self.a_dyn_ineq, self.x_dyn_ineq, self.b_dyn_ineq = self.__ADynIneq()

        return

    ##===========================================================================
    # PRIVATE

    ##---------------------------------------------------------------------------
    # Input:
    #   schedule: Dictionary of variables required to generate the matrices
    #
    # Output:
    #   Initialized member variables
    def __initVars(self, schedule):
        # Initialize member variables
        ## Input Variables
        self.A     = schedule['A']
        self.G_idx = schedule['Gamma']
        self.N     = schedule['N']
        self.Q     = schedule['Q']
        self.e     = schedule['e']
        self.eta   = schedule['eta']
        self.g_idx = schedule['gamma']
        self.kappa = schedule['kappa']
        self.l     = schedule['l']
        self.t     = schedule['t']
        self.xi    = schedule['xi']

        ## Decision Variables
        self.a     = schedule['a']
        self.c     = schedule['c']
        self.delta = schedule['delta']
        self.eta   = schedule['eta']
        self.g     = schedule['g']
        self.p     = schedule['p']
        self.sigma = schedule['sigma']
        self.u     = schedule['u']
        self.v     = schedule['v']
        self.w     = schedule['w']

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   p: Time spent charging
    #   u: Initial charge time
    #   c: Detatch time
    #
    # Output:
    #   A_pack_eq
    #
    def __APackEq(self):
        nq_0      = np.zeros((self.N, self.N*self.Q), dtype=float)

        # A_pack_eq
        ## A_detatch
        A_p       = np.eye(self.N, dtype=float)
        A_u       = A_p.copy()

        A_detatch = np.append(A_p, A_u, axis=1)
        A_detatch = np.append(A_detatch, nq_0, axis=1)

        ## A_w
        A_w = NQMat(self.N, self.Q, float, np.ones(self.Q, dtype=float))
        A_w = np.append(nq_0, A_w, axis=1)

        ## A_v
        A_v = NQMat(self.N, self.Q, float)
        A_v = np.append(nq_0, A_v, axis=1)

        ## A_eq
        A_pack_eq = np.append(A_detatch, A_w, axis=0)
        A_pack_eq = np.append(A_pack_eq, A_v, axis=0)

        # x_pack_eq
        x_pack_eq = np.append(toArr(self.p), toArr(self.u))
        x_pack_eq = np.append(x_pack_eq, toArr(self.w))

        # b_pack_eq
        b_pack_eq = np.append(toArr(self.c), np.ones(self.N))
        b_pack_eq = np.append(b_pack_eq, toArr(self.v))

        return A_pack_eq, x_pack_eq, b_pack_eq

    ##---------------------------------------------------------------------------
    # Input:
    #   eta: Initial charge of each bus visit
    #   g  : Linearization term for p[i]*w[i][q]
    #   r  : Charge rate for each charger [kwh]
    #   l  : Discharge amount per bus route
    #
    # Output:
    #   A_dyn_eq
    #
    def __ADynEq(self):
        n_0 = np.eye(self.N, dtype=float)

        # A_dyn_eq
        A_dyn_eq = NQMat(self.N, self.Q, float, self.e)
        A_dyn_eq = np.append(n_0, A_dyn_eq, axis=1)
        A_dyn_eq = np.append(A_dyn_eq, n_0, axis=1)

        # x
        x_dyn_eq = np.append(self.kappa, toArr(self.eta))
        x_dyn_eq = np.append(x_dyn_eq, toArr(self.g))
        x_dyn_eq = np.append(x_dyn_eq, self.l)

        # b
        ## Because eta has size (N-A), the index values (0-A) need to be ignored
        ## and the values greater than A need to be normalized
        ## (i.e. start from 0)
        idx           = adjustArray(self.N, self.g_idx)
        b_dyn_eq = np.array([self.eta[i] for i in idx])

        return A_dyn_eq, x_dyn_eq, b_dyn_eq

    ##---------------------------------------------------------------------------
    # Input:
    def __APackIneq(self):
        return

    ##---------------------------------------------------------------------------
    # Input:
    def __ADynIneq(self):
        return

