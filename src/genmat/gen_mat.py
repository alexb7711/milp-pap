#!/usr/bin/python

# Standard Lib
import numpy as np

# Developed
from mat_util   import *
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
    #                   * kappa : List of initial charges
    #                   * gamma : List of indexes for the next visit
    #                   * l     : List of amount of discharge for each route
    #                   * m     : Cost of assignment to charger
    #                   * r     : List of charge rates
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
        return

    ##---------------------------------------------------------------------------
    # Input:
    #   Input from __initVars()
    #
    # Output:
    #   A_eq   , x_eq   , b_eq
    #   A_ineq , x_ineq , b_ineq
    #
    def genMats(self):
        # Generate matrices
        ## A's
        self.A_pack_eq   = self.__APackEq()
        self.A_dyn_eq    = self.__ADynEq()
        self.A_pack_ineq = self.__APackIneq()
        self.A_dyn_ineq  = self.__ADynIneq()

        ## x's
        self.x_pack_eq   = self.__xPackEq()
        self.x_dyn_eq    = self.__xDynEq()
        self.x_pack_ineq = self.__xPackIneq()
        self.x_dyn_ineq  = self.__xDynIneq()

        ## b's
        self.b_pack_eq   = self.__bPackEq()
        self.b_dyn_eq    = self.__bDynEq()
        self.b_pack_ineq = self.__bPackIneq()
        self.b_dyn_ineq  = self.__bDynIneq()

        # Combine Matrices

        # Create data structure
        mats = \
        {
        }

        return mats

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
        self.S     = schedule['S']
        self.T     = schedule['T']
        self.Xi    = self.N*(self.N-1)
        self.e     = schedule['e']
        self.fa    = schedule['fa']
        self.g_idx = schedule['gamma']
        self.kappa = schedule['kappa']
        self.l     = schedule['l']
        self.t     = schedule['t']
        self.r     = schedule['r']
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

        return A_pack_eq

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
        iden = np.eye(self.N, dtype=float)

        # A_init_charge
        zeros         = np.zeros((self.N, self.N+self.N*self.Q), dtype=float)
        A_init_charge = np.append(kappaMat(self.N, float, self.kappa), zeros, axis=1)

        # A_next_charge
        A_next_charge = NQMat(self.N, self.Q, float, self.r)
        A_next_charge = np.append(iden, A_next_charge, axis=1)
        A_next_charge = np.append(A_next_charge, iden, axis=1)

        ## Combine submatrices
        A_dyn_eq = np.append(A_init_charge, A_next_charge, axis=0)

        return A_dyn_eq

    ##---------------------------------------------------------------------------
    # Input:
    #   u     : Initial charge time for each bus visit
    #   p     : Time on charger for each bus visit
    #   v     : Selected queue for each bus visit
    #   s     : Bus size of each bus visit
    #   sigma : Matrix representation of time relative to other bus visits
    #   detla : Matrix representation of physical space relative to other bus
    #           visits
    #   a     : Arrival time for each bus visit
    #   c     : Detatch time from charger for each bus visit
    #   t     : Time of departure from station for each bus visit
    #   g     : Linearization term for p[i]*w[i][q]
    #   w     : Vector representation of v
    #
    # Output:
    #   A_pack_ineq, x_pack_ineq, b_pack_ineq
    #
    def __APackIneq(self):
        # Local variables
        N  = self.N
        Q  = self.Q
        Xi = self.Xi
        M  = self.T

        # A_time
        ## A_u
        A_u = XiNMat(Xi, N, int)

        ## A_p
        A_p = XiNMat(Xi, N, int, [0,-1])

        ## A_sigma
        A_sigma = -self.T*np.eye(Xi, dtype=int)

        ## A_ones
        A_ones = -1*A_sigma.copy()

        ## A_zeros_aft
        A_zeros_aft = np.zeros((Xi, 2*Xi + 4*N + 3*N*Q))

        ## Combine sub-matrices
        A_time = np.append(A_u    , A_p         , axis=1)
        A_time = np.append(A_time , A_sigma     , axis=1)
        A_time = np.append(A_time , A_ones      , axis=1)
        A_time = np.append(A_time , A_zeros_aft , axis=1)

        # A_queue
        ## A_zeros_bef
        A_zeros_bef = np.zeros((Xi, 2*Xi + 2*N))

        ## A_v
        A_v = XiNMat(Xi, N, int)

        ## A_s
        A_s = XiNMat(Xi, N, int, [0,-1])

        ## A_sigma
        A_delta = -self.T*np.eye(Xi, dtype=int)

        ## A_ones
        A_ones = -1*A_sigma.copy()

        ## A_zeros_aft
        A_zeros_aft = np.zeros((Xi, 2*N + 3*N*Q), dtype=int)

        ## Combine sub-matrices
        A_queue = np.append(A_zeros_bef , A_v         , axis=1)
        A_queue = np.append(A_queue     , A_s         , axis=1)
        A_queue = np.append(A_queue     , A_delta     , axis=1)
        A_queue = np.append(A_queue     , A_ones      , axis=1)
        A_queue = np.append(A_queue     , A_zeros_aft , axis=1)

        # A_sd
        ## A_zeros_bef
        A_zeros_bef = np.zeros((Xi,2*N), dtype=int)

        ## A_zeros_int
        A_zeros_int = np.zeros((Xi,Xi+2*N), dtype=int)

        ## A_zeros_aft
        A_zeros_aft = np.zeros((Xi, Xi + 2*N + 3*N*Q), dtype=int)

        ## Combine sub-matrices
        A_sd = np.append(A_zeros_bef , A_sigma     , axis=1)
        A_sd = np.append(A_sd        , A_zeros_int , axis=1)
        A_sd = np.append(A_sd        , A_delta     , axis=1)
        A_sd = np.append(A_sd        , A_zeros_aft , axis=1)

        # A_s
        ## A_zeros_bef
        A_zeros_bef = np.zeros((Xi,2*N), dtype=int)

        ## A_zeros_aft
        A_zeros_aft = np.zeros((Xi, 3*Xi + 4*N + 3*N*Q), dtype=int)

        ## Combine sub-matrices
        A_s = np.append(A_zeros_bef , -1*A_sigma  , axis=1)
        A_s = np.append(A_s         , A_zeros_aft , axis=1)

        # A_d
        ## A_zeros_bef
        A_zeros_bef = np.zeros((Xi,2*Xi+4*N), dtype=int)

        ## A_zeros_aft
        A_zeros_aft = np.zeros((Xi, Xi + 2*N + 3*N*Q), dtype=int)

        ## Combine sub-matrices
        A_d = np.append(A_zeros_bef , -1*A_delta  , axis=1)
        A_d = np.append(A_d         , A_zeros_aft , axis=1)

        # A_a
        ## A_zeros_bef
        A_zeros_bef = np.zeros((N,4*Xi+4*N), dtype=int)

        ## A_zeros_aft
        A_zeros_aft = np.zeros((N, N+3*N*Q), dtype=int)

        ## Combine sub-matrices
        A_a = np.append(A_zeros_bef , -1*np.eye(N , dtype=int) , axis=1)
        A_a = np.append(A_a         , A_zeros_aft              , axis=1)

        # A_c
        ## A_zeros_bef
        A_zeros_bef = np.zeros((N,4*Xi+5*N), dtype=int)

        ## A_zeros_aft
        A_zeros_aft = np.zeros((N, 3*N*Q), dtype=int)

        ## Combine sub-matrices
        A_c = np.append(A_zeros_bef , -1*np.eye(N,dtype=int) , axis=1)
        A_c = np.append(A_c         , A_zeros_aft                 , axis=1)

        # A_g
        ## A_zeros_bef
        A_zeros_bef = np.zeros((4*N,4*Xi + 6*N), dtype=int)

        ## A_nqzero
        A_nqzero = NQNMat(N, Q, int, np.zeros(Q, dtype=int))

        ## A_gg
        ## A_gp_t
        A_gp_t = np.append(-1*NQNMat(N, Q, int), A_nqzero, axis=1)
        A_gp_t = np.append(A_gp_t, A_nqzero, axis=1)

        ## A_gg_b
        A_gp_b = np.append(-1*NQNMat(N, Q, int), A_nqzero, axis=1)
        A_gp_b = np.append(A_gp_b, -M*NQNMat(N, Q, int), axis=1)

        ## A_gw_t
        A_gw_t = np.append(NQNMat(N, Q, int), A_nqzero, axis=1)
        A_gw_t = np.append(A_gw_t, A_nqzero, axis=1)

        ## A_gw_b
        A_gw_b = np.append(-1*NQNMat(N, Q, int), M*NQNMat(N, Q, int), axis=1)
        A_gw_b = np.append(A_gw_b, A_nqzero, axis=1)

        ## Combine sub-matrices
        A_g = np.append(A_gp_t      , A_gp_b , axis=0)
        A_g = np.append(A_g         , A_gw_t , axis=0)
        A_g = np.append(A_g         , A_gw_b , axis=0)
        A_g = np.append(A_zeros_bef , A_g    , axis=1)

        # A_pack_ineq
        A_pack_ineq = np.append(A_time      , A_queue , axis=0)
        A_pack_ineq = np.append(A_pack_ineq , A_sd    , axis=0)
        A_pack_ineq = np.append(A_pack_ineq , A_s     , axis=0)
        A_pack_ineq = np.append(A_pack_ineq , A_d     , axis=0)
        A_pack_ineq = np.append(A_pack_ineq , A_a     , axis=0)
        A_pack_ineq = np.append(A_pack_ineq , A_c     , axis=0)
        A_pack_ineq = np.append(A_pack_ineq , A_c     , axis=0)
        A_pack_ineq = np.append(A_pack_ineq , A_g     , axis=0)

        return A_pack_ineq

    ##---------------------------------------------------------------------------
    # Input:
    #   N     : Number of bus visits
    #   Q     : Number of chargers
    #   Xi    : N(N-1)
    #   c     : Detatch time for each visit
    #   eta   : Initial charge for each bus visit
    #   g     : Linearization term for blinear values
    #   kappa : List of initial charges
    #   l     : List of amount of discharge for each route
    #   p     : Time spent on charger for each bus visit
    #   r : Charge rate for each charger
    #   u     : Initial charge time for each visit
    #   v     : Assigned queue for each bus visit
    #
    # Output:
    #   A_dyn_ineq
    #
    def __ADynIneq(self):
        # Local variables
        N  = self.N
        Q  = self.Q
        Xi = self.Xi
        M  = self.T

        # A_max_charge
        A_ones = -1*np.eye(N, dtype=int)
        A_eta  = NQNMat(N, Q, int, -1*self.r)
        A_z    = 0*np.eye(N, dtype=int)

        ## Combine submatrices
        A_max_charge = np.append(A_ones       , A_eta , axis=1)
        A_max_charge = np.append(A_max_charge , A_z   , axis=1)

        # A_min_charge
        A_ones = -1*np.eye(N, dtype=int)
        A_r    = NQNMat(N, Q, int, -1*self.r)
        A_l    = np.eye(N, dtype=int)*self.l

        ## Combine submatrices
        A_min_charge = np.append(A_ones        , A_r , axis=1)
        A_min_charge = np.append(A_min_charge , A_l , axis=1)

        # A_last_charge
        A_last_charge = np.append(NMat(N, int, self.fa), np.zeros((N,N+N*Q), dtype=int), axis=1)

        # A_dyn_ineq
        A_dyn_ineq = np.append(A_max_charge , A_min_charge  , axis=0)
        A_dyn_ineq = np.append(A_dyn_ineq   , A_last_charge , axis=0)

        return A_dyn_ineq


    ##---------------------------------------------------------------------------
    # Input:
    #   p : Time on charger for each bus visit
    #   u : Initial charge time for each bus visit
    #   w : Vector representation of v
    #
    # Output:
    #   x_pack_eq
    #
    def __xPackEq(self):
        x_pack_eq = np.append(toArr(self.p), toArr(self.u))
        x_pack_eq = np.append(x_pack_eq, toArr(self.w))
        return x_pack_eq

    ##---------------------------------------------------------------------------
    # Input:
    #   eta   : Initial charge of each bus visit
    #   g     : Linearization term for p[i]*w[i][q]
    #   kappa : Initial charge for first bus visit for each bus
    #   l     : Discharge amount per bus route
    #
    # Output:
    #   x_dyn_eq
    #
    def __xDynEq(self):
        x_dyn_eq = np.append(toArr(self.eta), toArr(self.g))
        x_dyn_eq = np.append(x_dyn_eq, self.l)
        return x_dyn_eq

    ##---------------------------------------------------------------------------
    # Input:
    #   a     : List of arrival times
    #   gamma : List of indexes for the next visit
    #   t     : List of departure times
    #   u     : Initial charge time for each visit
    #   v     : Assigned queue for each bus visit
    #   c     : Detatch time for each visit
    #   p     : Time spent on charger for each bus visit
    #   w     : Vector representation of queue assignment
    #   sigma : Time representation of visits
    #   delta : Space representation of visits
    #
    # Output:
    #   a_pack_ineq
    #
    def __xPackIneq(self):
        print("u: ", np.array(toArr(self.u)).shape)
        print("p: ", np.array(toArr(self.p)).shape)
        print("sigma: ", np.array(toArr(self.sigma)).shape)
        print("v: ", np.array(toArr(self.v)).shape)
        print("delta: ", np.array(toArr(self.delta)).shape)
        print("a: ", self.a.shape)
        print("c: ", np.array(toArr(self.c)).shape)
        print("g: ", np.array(toArr(self.g)).shape)
        print("w: ", np.array(toArr(self.w)).shape)

        x_pack_ineq = np.append(toArr(self.u) , toArr(self.p))
        x_pack_ineq = np.append(x_pack_ineq   , toArr(self.sigma))
        x_pack_ineq = np.append(x_pack_ineq   , np.ones(self.Xi , dtype=int ))
        x_pack_ineq = np.append(x_pack_ineq   , toArr(self.v))
        x_pack_ineq = np.append(x_pack_ineq   , self.S*np.ones(self.N , dtype=int ))
        x_pack_ineq = np.append(x_pack_ineq   , toArr(self.delta))
        x_pack_ineq = np.append(x_pack_ineq   , np.ones(self.Xi, dtype=int ))
        x_pack_ineq = np.append(x_pack_ineq   , self.a)
        x_pack_ineq = np.append(x_pack_ineq   , toArr(self.c))
        x_pack_ineq = np.append(x_pack_ineq   , toArr(self.g))
        x_pack_ineq = np.append(x_pack_ineq   , toArr(self.w))
        x_pack_ineq = np.append(x_pack_ineq   , np.ones(self.N*self.Q, dtype=int ))
        return x_pack_ineq

    ##---------------------------------------------------------------------------
    # Input:
    def __xDynIneq(self):
        x_dyn_ineq = np.append(toArr(self.eta), toArr(self.g))
        x_dyn_ineq = np.append(x_dyn_ineq, np.ones(self.N, dtype=float))
        return x_dyn_ineq

    ##---------------------------------------------------------------------------
    # Input:
    #   N : Number of bus visits
    #   c : Detatch time from charger for each bus visit
    #   v : Selected queue for each bus visit
    #
    # Output:
    #   b_pack_eq
    #
    def __bPackEq(self):
        b_pack_eq = np.append(toArr(self.c), np.ones(self.N))
        b_pack_eq = np.append(b_pack_eq, toArr(self.v))
        return b_pack_eq

    ##---------------------------------------------------------------------------
    # Input:
    #   N   : Number of bus visits
    #   g   : Linearization term for p[i]*w[i][q]
    #   eta : Initial charge of each bus visit
    #
    # Output:
    #   b_dyn_eq
    #
    # Note:
    #   Because eta has size (N-A), the index values (0-A) need to be ignored
    #   and the values greater than A need to be normalized
    #   (i.e. start from 0)
    #
    def __bDynEq(self):
        # b_init_charge
        b_init_charge = np.array(toArr(self.eta))

        # b_next_charge
        idx           = adjustArray(self.N, self.g_idx)
        b_next_charge = np.array([self.eta[i] for i in idx])

        # Combine submatrices
        b_dyn_eq = np.append(b_init_charge, b_next_charge)

        return b_dyn_eq

    ##---------------------------------------------------------------------------
    # Input:
    def __bPackIneq(self):
        return

    ##---------------------------------------------------------------------------
    # Input:
    def __bDynIneq(self):
        return
