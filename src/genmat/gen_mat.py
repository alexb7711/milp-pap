#!/usr/bin/python

# Standard Lib
import numpy        as np
import scipy.sparse as sp

# Developed
from mat_util   import *
from array_util import *

# Printing Parameters
large_width = 200
np.set_printoptions(linewidth=large_width)


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
    #                   * alpha : List of initial charges
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
        ## A
        self.A_eq   = self.__genAEQ()
        self.A_ineq = self.__genAINEQ()

        # x
        self.x_eq   = self.__genXEQ()
        self.x_ineq = self.__genXINEQ()

        # b
        self.b_eq   = self.__genBEQ()
        self.b_ineq = self.__genBINEQ()

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
        self.H_min = schedule['H_min']
        self.N     = schedule['N']
        self.Q     = schedule['Q']
        self.S     = schedule['S']
        self.T     = schedule['T']
        self.Xi    = self.N*(self.N-1)
        self.alpha = schedule['alpha']
        self.beta  = schedule['beta']
        self.cap   = schedule['cap']
        self.e     = schedule['e']
        self.fa    = schedule['fa']
        self.g_idx = schedule['gamma']
        self.l     = schedule['l']
        self.r     = schedule['r']
        self.t     = schedule['t']

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
        # A_pack_eq
        ## A_detatch
        print("Generating A_detatch...")

        A_p       = sp.csr_matrix(np.eye(self.N, dtype=float))
        A_u       = sp.csr_matrix(A_p.copy())
        nq_0      = sp.csr_matrix(np.zeros((self.N, self.N*self.Q), dtype=float))

        A_detatch = sp.hstack([A_p       , A_u ])
        A_detatch = sp.hstack([A_detatch , nq_0])

        del A_p, A_u, nq_0

        ## A_w
        print("Generating A_w...")

        ## Create array [1 2 .. Q 1 2 ... Q ...]
        inc_arr = range(1,self.Q+1,1)

        n2_0 = np.zeros((self.N, 2*self.N), dtype = float)

        A_w = NQMat(self.N, self.Q, float, inc_arr)
        A_w = np.append(n2_0, A_w, axis = 1)
        A_w = sp.csr_matrix(A_w)

        del inc_arr, n2_0

        ## A_eq
        print("Generating A_pack_eq...")
        A_pack_eq = sp.vstack([A_detatch, A_w])

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
        # A_init_charge
        print("Generating A_init_charge...")

        zeros         = sp.csr_matrix(np.zeros((self.N, self.N+self.N*self.Q), dtype=float))
        init_visit    = np.array([first(self.G_idx,i) for i in range(self.A)])

        A_init_charge = sp.hstack([sp.csr_matrix(alphaMat(self.N, float, self.alpha, init_visit)), zeros])

        del zeros, init_visit

        # A_next_charge
        print("Generating A_next_charge...")

        A_r  = sp.csr_matrix(NQMat(self.N, self.Q, float, self.r))
        iden = sp.csr_matrix(np.eye(self.N, dtype=float))

        for i in range(len(self.g_idx)):
            if self.g_idx[i] <= 0:
                iden[i] = iden[i] * 0
                A_r[i]  = A_r[i] * 0

        A_next_charge = sp.hstack([iden          , A_r   ])
        A_next_charge = sp.hstack([A_next_charge , -iden ])

        del A_r, iden

        ## Combine submatrices
        print("Generating A_dyn_eq...")
        A_dyn_eq = sp.vstack([A_init_charge, A_next_charge])

        return A_dyn_eq

    ##---------------------------------------------------------------------------
    # Input:
    #   u     : Initial charge time for each bus visit
    #   p     : Time on charger for each bus visit
    #   v     : Selected queue for each bus visit
    #   s     : Bus size of each bus visit
    #   sigma : Matrix representation of time relative to other bus visits
    #   delta : Matrix representation of physical space relative to other bus
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
        N   = self.N
        Q   = self.Q
        Xi  = self.Xi
        Psi = int(self.Xi/2)
        M   = self.T

        # A_time
        print("Generating A_time...")
        ## A_u
        A_u = XiNMat(Xi, N, int)
        A_u = sp.csr_matrix(A_u)

        ## A_p
        A_p = sp.csr_matrix(XiNMat(Xi, N, int, [0,-1]))

        ## A_sigma
        A_sigma = sp.csr_matrix(sdMat(N))

        ## A_ones
        A_ones = sp.csr_matrix(-1*-self.T*A_sigma.copy())

        ## A_zeros_aft
        A_zeros_aft = sp.csr_matrix(np.zeros((Xi, 2*Xi + 4*N + 3*N*Q)))

        ## Combine sub-matrices
        A_time = sp.hstack([A_u    , A_p             ])
        A_time = sp.hstack([A_time , -self.T*A_sigma ])
        A_time = sp.hstack([A_time , A_ones          ])
        A_time = sp.hstack([A_time , A_zeros_aft     ])

        del A_u, A_p, A_sigma, A_ones, A_zeros_aft

        # A_queue
        print("Generating A_queue...")
        ## A_zeros_bef
        A_zeros_bef = sp.csr_matrix(np.zeros((Xi, 2*Xi + 2*N)))

        ## A_v
        A_v = sp.csr_matrix(XiNMat(Xi, N, int))

        ## A_s
        A_s = sp.csr_matrix(XiNMat(Xi, N, int, [0,-1]))

        ## A_delta
        A_delta = sp.csr_matrix(sdMat(N))

        ## A_ones
        A_ones = sp.csr_matrix(-1*-self.S*A_delta.copy())

        ## A_zeros_aft
        A_zeros_aft = sp.csr_matrix(np.zeros((Xi, 2*N + 3*N*Q), dtype=float))

        ## Combine sub-matrices
        A_queue = sp.hstack([A_zeros_bef , A_v             ])
        A_queue = sp.hstack([A_queue     , A_s             ])
        A_queue = sp.hstack([A_queue     , -self.S*A_delta ])
        A_queue = sp.hstack([A_queue     , A_ones          ])
        A_queue = sp.hstack([A_queue     , A_zeros_aft     ])

        del A_v, A_s, A_delta, A_ones, A_zeros_aft

        # A_sd
        print("Generating A_sd...")
        ## A_delta
        A_delta = sp.csr_matrix(sd2Mat(N))

        ## A_sigma
        A_sigma = sp.csr_matrix(sd2Mat(N))

        ## A_zeros_bef
        A_zeros_bef = sp.csr_matrix(np.zeros((Psi,2*N), dtype=float))

        ## A_zeros_int
        A_zeros_int = sp.csr_matrix(np.zeros((Psi,Xi+2*N), dtype=float))

        ## A_zeros_aft
        A_zeros_aft = sp.csr_matrix(np.zeros((Psi, Xi + 2*N + 3*N*Q), dtype=float))

        ## Combine sub-matrices
        A_sd = sp.hstack([A_zeros_bef , A_sigma     ])
        A_sd = sp.hstack([A_sd        , A_zeros_int ])
        A_sd = sp.hstack([A_sd        , A_delta     ])
        A_sd = sp.hstack([A_sd        , A_zeros_aft ])

        del A_zeros_bef, A_zeros_int, A_zeros_aft

        # A_s
        print("Generating A_s...")
        ## A_zeros_bef
        A_zeros_bef = sp.csr_matrix(np.zeros((Psi,2*N), dtype=float))

        ## A_zeros_aft
        A_zeros_aft = sp.csr_matrix(np.zeros((Psi, 3*Xi + 4*N + 3*N*Q), dtype=float))

        ## Combine sub-matrices
        A_s = sp.hstack([A_zeros_bef , -1*A_sigma  ])
        A_s = sp.hstack([A_s         , A_zeros_aft ])

        del A_zeros_bef, A_zeros_aft, A_sigma

        # A_d
        print("Generating A_d...")
        ## A_zeros_bef
        A_zeros_bef = sp.csr_matrix(np.zeros((Psi,2*Xi+4*N), dtype=float))

        ## A_zeros_aft
        A_zeros_aft = sp.csr_matrix(np.zeros((Psi, Xi + 2*N + 3*N*Q), dtype=float))

        ## Combine sub-matrices
        A_d = sp.hstack([A_zeros_bef , -1*A_delta ])
        A_d = sp.hstack([A_d         , A_zeros_aft])

        del A_zeros_bef, A_zeros_aft, A_delta

        # A_a
        print("Generating A_a...")
        ## A_zeros_bef
        A_zeros_bef = sp.csr_matrix(np.zeros((N,4*Xi+4*N), dtype=float))

        ## A_zeros_aft
        A_zeros_aft = sp.csr_matrix(np.zeros((N, N+3*N*Q), dtype=float))

        ## Combine sub-matrices
        A_a = sp.hstack([A_zeros_bef , -1*np.eye(N,dtype=float)])
        A_a = sp.hstack([A_a         , A_zeros_aft             ])

        del A_zeros_bef, A_zeros_aft

        # A_c
        print("Generating A_c...")
        ## A_zeros_bef
        A_zeros_bef = sp.csr_matrix(np.zeros((N,4*Xi+5*N), dtype=float))

        ## A_zeros_aft
        A_zeros_aft = sp.csr_matrix(np.zeros((N, 3*N*Q), dtype=float))

        ## Combine sub-matrices
        A_c = sp.hstack([A_zeros_bef , -1*np.eye(N,dtype=float)])
        A_c = sp.hstack([A_c         , A_zeros_aft             ])

        del A_zeros_bef, A_zeros_aft

        # A_g
        print("Generating A_g...")
        ## A_zeros_bef
        A_zeros_bef = sp.csr_matrix(np.zeros((4*N,4*Xi + 6*N), dtype=float))

        ## A_nqzero
        A_nqzero = sp.csr_matrix(NQNMat(N, Q, int, np.zeros(Q, dtype=float)))

        ## A_gp
        ### A_gp_t
        A_gp_t = sp.hstack([sp.csr_matrix(-1*NQNMat(N, Q, int)), A_nqzero])
        A_gp_t = sp.hstack([A_gp_t                             , A_nqzero])

        ### A_gp_b
        A_gp_b = sp.hstack([sp.csr_matrix(1*NQNMat(N, Q, int)), -M*NQNMat(N, Q, int)])
        A_gp_b = sp.hstack([A_gp_b                            ,  M*NQNMat(N, Q, int)])

        ## A_gw
        ### A_gw_t
        A_gw_t = sp.hstack([sp.csr_matrix(-1*NQNMat(N, Q, int)), A_nqzero])
        A_gw_t = sp.hstack([A_gw_t, sp.csr_matrix(M*NQNMat(N, Q, int))])

        ### A_gw_b
        A_gw_b = sp.hstack([sp.csr_matrix(NQNMat(N, Q, int)), A_nqzero])
        A_gw_b = sp.hstack([A_gw_b                          , A_nqzero])


        ## Combine sub-matrices
        A_g = sp.vstack([A_gp_t      , A_gp_b])
        A_g = sp.vstack([A_g         , A_gw_t])
        A_g = sp.vstack([A_g         , A_gw_b])
        A_g = sp.hstack([A_zeros_bef , A_g])

        # A_pack_ineq
        print("Generating A_pack_ineq...")
        A_pack_ineq = sp.vstack([A_time      , A_queue])
        A_pack_ineq = sp.vstack([A_pack_ineq , A_sd   ])
        A_pack_ineq = sp.vstack([A_pack_ineq , A_s    ])
        A_pack_ineq = sp.vstack([A_pack_ineq , A_d    ])
        A_pack_ineq = sp.vstack([A_pack_ineq , A_a    ])
        A_pack_ineq = sp.vstack([A_pack_ineq , A_c    ])
        A_pack_ineq = sp.vstack([A_pack_ineq , A_c    ])
        A_pack_ineq = sp.vstack([A_pack_ineq , A_g    ])

        return A_pack_ineq

    ##---------------------------------------------------------------------------
    # Input:
    #   N     : Number of bus visits
    #   Q     : Number of chargers
    #   Xi    : N(N-1)
    #   c     : Detatch time for each visit
    #   eta   : Initial charge for each bus visit
    #   g     : Linearization term for blinear values
    #   alpha : List of initial charges
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
        A_ones = np.eye(N, dtype=float)
        ## TODO: Passing in self.r does not seem right, but it works for the
        ##       single charger case. Invstigate later.
        A_r    = NQNMat(N, Q, int, self.r)
        A_z    = 0*np.eye(N, dtype=float)

        ## Combine submatrices
        A_max_charge = np.append(-A_ones      , -A_r , axis=1)
        A_max_charge = np.append(A_max_charge , A_z , axis=1)

        # A_min_charge
        A_l = -1*np.eye(N, dtype=float)*self.l

        ## Combine submatrices
        A_min_charge = np.append(A_ones       , A_r , axis=1)
        A_min_charge = np.append(A_min_charge , A_l , axis=1)

        # A_last_charge
        A_last_charge = np.append(NMat(N, int, self.fa), np.zeros((N,N+N*Q), dtype=float), axis=1)

        # A_dyn_ineq
        A_dyn_ineq = np.append(A_max_charge , A_min_charge        , axis=0)
        A_dyn_ineq = np.append(A_dyn_ineq   , A_last_charge       , axis=0)

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
        print("Generating x_pack_eq...")
        x_pack_eq = np.append(toArr(self.p), toArr(self.u))
        x_pack_eq = np.append(x_pack_eq, toArr(self.w))
        return x_pack_eq

    ##---------------------------------------------------------------------------
    # Input:
    #   eta   : Initial charge of each bus visit
    #   g     : Linearization term for p[i]*w[i][q]
    #   alpha : Initial charge for first bus visit for each bus
    #   l     : Discharge amount per bus route
    #
    # Output:
    #   x_dyn_eq
    #
    def __xDynEq(self):
        print("Generating x_dyn_eq...")
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
        print("Generating x_pack_ineq...")
        x_pack_ineq = np.append(toArr(self.u) , toArr(self.p))
        x_pack_ineq = np.append(x_pack_ineq   , toArr(self.sigma))
        x_pack_ineq = np.append(x_pack_ineq   , np.ones(self.Xi , dtype=float ))
        x_pack_ineq = np.append(x_pack_ineq   , toArr(self.v))
        x_pack_ineq = np.append(x_pack_ineq   , self.S*np.ones(self.N , dtype=float ))
        x_pack_ineq = np.append(x_pack_ineq   , toArr(self.delta))
        x_pack_ineq = np.append(x_pack_ineq   , np.ones(self.Xi, dtype=float ))
        x_pack_ineq = np.append(x_pack_ineq   , self.a)
        x_pack_ineq = np.append(x_pack_ineq   , toArr(self.c))
        x_pack_ineq = np.append(x_pack_ineq   , toArr(self.g))
        x_pack_ineq = np.append(x_pack_ineq   , np.ones(self.N*self.Q, dtype=float ))
        x_pack_ineq = np.append(x_pack_ineq   , toArr(self.w))
        return x_pack_ineq

    ##---------------------------------------------------------------------------
    # Input:
    #   N : Number of bus visits
    #   eta   : Initial charge of each bus visit
    #   g     : Linearization term for p[i]*w[i][q]
    #
    # Output:
    #   x_dyn_ineq
    #
    def __xDynIneq(self):
        print("Generating x_dyn_ineq...")
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
        print("Generating b_pack_eq...")
        b_pack_eq = np.append(self.c.tolist(), self.v.tolist())
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
        print("Generating b_init_charge...")
        ## Find indices for initial visits
        init_visit_idx = [first(self.G_idx, i) for i in range(self.A)]

        ## Generate array to indicate first visit or not
        eta = self.eta.tolist()

        for i in range(self.N):
            if first(init_visit_idx,i) != -1:
                eta[i] = 1.0*eta[i]
            else:
                eta[i] = 0.0*eta[i]

        b_init_charge = eta

        # b_next_charge
        print("Generating b_next_charge...")
        idx           = adjustArray(self.A, self.g_idx)
        b_next_charge = []

        for i in self.g_idx:
            if i >= 0:
                b_next_charge.append(self.eta.tolist()[i])
            else:
                b_next_charge.append(0)

        # Combine submatrices
        print("Generating b_dyn_eq...")
        b_dyn_eq = np.append(b_init_charge, b_next_charge)

        return b_dyn_eq

    ##---------------------------------------------------------------------------
    # Input:
    #   N : Number of bus visits
    #   T : Time horizon
    #   c : Detatch time from charger for each bus visit
    #   p : Time spent on charger for each bus visit
    #
    # Output:
    #   b_pack_ineq
    #
    def __bPackIneq(self):
        # Local variables
        print("Generating b_pack_ineq...")
        N   = self.N
        T   = self.T
        Xi  = self.Xi
        Psi = int(self.Xi/2)

        xi_zeros = np.zeros(Xi, dtype=float)
        n_ones   = np.ones(N, dtype=float)
        psi_ones = np.ones(Psi, dtype=float)

        b_pack_ineq = np.append(xi_zeros    , xi_zeros)
        b_pack_ineq = np.append(b_pack_ineq , psi_ones)
        b_pack_ineq = np.append(b_pack_ineq , -psi_ones)
        b_pack_ineq = np.append(b_pack_ineq , -psi_ones)
        b_pack_ineq = np.append(b_pack_ineq , -1.0*np.array(toArr(self.c)))
        b_pack_ineq = np.append(b_pack_ineq , -1*(T*n_ones - toArr(self.p)))
        b_pack_ineq = np.append(b_pack_ineq , -self.t)
        b_pack_ineq = np.append(b_pack_ineq , -1.0*np.array(toArr(self.p)))
        b_pack_ineq = np.append(b_pack_ineq , toArr(self.p))
        b_pack_ineq = np.append(b_pack_ineq , np.zeros(2*N, dtype=float))

        return b_pack_ineq

    ##---------------------------------------------------------------------------
    # Input:
    #   N : Number of bus visits
    #   H : Final charge percentage for each bus
    #
    # Output:
    #   b_dyn_ineq
    #
    def __bDynIneq(self):
        # Local variables
        N               = self.N
        final_charge    = np.zeros(N)

        ## Set final charge value in correct index
        for i in self.fa:
            final_charge[i] = self.cap[i]

        print("Generating b_dyn_ineq...")
        b_dyn_ineq = np.append(-1*self.beta*self.cap, np.zeros(self.N, dtype=float))
        b_dyn_ineq = np.append(b_dyn_ineq, self.H_min*final_charge)

        return b_dyn_ineq

    ##---------------------------------------------------------------------------
    # Input:
    #   A_pack_eq
    #   A_dynamics_eq
    #
    # Output
    #   A_eq
    #
    def __genAEQ(self):
        Ap  = self.A_pack_eq
        Ad  = self.A_dyn_eq
        ztr = sp.csr_matrix(np.zeros((2*self.N, 2*self.N+self.N*self.Q), dtype   = float))
        zbl = sp.csr_matrix(np.zeros((2*self.N, 2*self.N+self.N*self.Q), dtype   = float))

        # Combine matrces
        print("Generating A_eq...")
        A_eq_top = sp.hstack([Ap, ztr])
        A_eq_bot = sp.hstack([zbl, Ad])
        A_eq     = sp.vstack([A_eq_top, A_eq_bot])

        return A_eq

    ##---------------------------------------------------------------------------
    # Input:
    #   A_pack_ineq
    #   A_dynamics_ineq
    #
    # Output
    #   A_ineq
    #
    def __genAINEQ(self):
        # Local Variables
        N   = self.N
        Xi  = self.Xi
        Psi = int(self.Xi/2)
        Q   = self.Q

        Ap  = self.A_pack_ineq
        Ad  = self.A_dyn_ineq
        ztr = sp.csr_matrix(np.zeros((2*Xi + 7*N + 3*Psi, 2*N + N*Q), dtype = float))
        zbl = sp.csr_matrix(np.zeros((3*N, 4*Xi + 6*N + 3*N*Q), dtype = float))

        # Combine Matrices
        print("Generating A_ineq...")
        A_ineq_top = sp.hstack([Ap         , ztr])
        A_ineq_bot = sp.hstack([zbl        , Ad ])
        A_ineq     = sp.vstack([A_ineq_top , A_ineq_bot])

        return A_ineq

    ##---------------------------------------------------------------------------
    # Input:
    #   x_pack_eq
    #   x_dynamics_eq
    #
    # Output
    #   x_eq
    #
    def __genXEQ(self):
        xp = self.x_pack_eq
        xd = self.x_dyn_eq
        return np.append(xp, xd)

    ##---------------------------------------------------------------------------
    # Input:
    #   x_pack_ineq
    #   x_dynamics_ineq
    #
    # Output
    #   x_ineq
    #
    def __genXINEQ(self):
        xp = self.x_pack_ineq
        xd = self.x_dyn_ineq
        return np.append(xp, xd)

    ##---------------------------------------------------------------------------
    # Input:
    #   b_pack_eq
    #   b_dynamics_eq
    #
    # Output
    #   b_eq
    #
    def __genBEQ(self):
        bp = self.b_pack_eq
        bd = self.b_dyn_eq
        return np.append(bp, bd)

    ##---------------------------------------------------------------------------
    # Input:
    #   b_pack_ineq
    #   b_dynamics_ineq
    #
    # Output
    #   b_ineq
    #
    def __genBINEQ(self):
        bp = self.b_pack_ineq
        bd = self.b_dyn_ineq
        return np.append(bp, bd)
