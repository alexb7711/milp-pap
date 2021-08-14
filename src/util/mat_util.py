#!/usr/bin/python

# Standard Lib
import numpy as np

##===============================================================================
# Input:
#   N    : Number of visits
#   Q    : Number of chargers
#   t    : Type of matrix (float, int, ...)
#   vals : Array of values to be placed. i.e. [1, 2] will be placed as follows :
#          [[ 1 2 0 0 ...]
#           [ 0 0 1 2 ...]...]
#          By default the values will increment, but you can specify the values
#          as well
#
# Output:
#   An NxNQ matrix with the appropriate values
#
def NQMat(N, Q, t, vals=[]):
    if not len(vals):
        vals = range(1,Q+1,1)

    inc  = len(vals)
    mat  = np.zeros((N, N*Q), dtype=t)

    for i in range(N):
        idx = 0
        for j in range(N*Q):
            if j >= i*inc and j <= i*inc + inc - 1:
                mat[i][j] = vals[idx]
                idx     += 1

    return mat

##===============================================================================
# Input:
#   Xi  : N*(N-1)
#   Q   : Number of chargers
#   t   : Type of matrix (float, int, ...)
#   vals : The values to be placed in the matrix
#
# Output:
#   An XixN matrix. The values will be placed as
#       [[ -1  1  0  0 0 0 ...]
#        [  1 -1  0  0 0 0 ...]
#        [  0  0 -1  1 0 0 ...]
#        [  0  0  1 -1 0 0 ...]
#   to loop through every combination
#
def XiNMat(Xi, N, t, vals=[1,-1]):

    # Initialize Matrix
    mat = np.zeros((Xi, N), dtype=t)

    # i indicates the bus visit in sigma[i][j]
    i = 0

    # Loop through each possible combination
    for k in range(0,Xi,N-1):
        for j in range(N-1):
            ## Create a column of 1's to represent i's in matrix
            mat[k+j,i] = vals[0]

            ## If j < i, j's indexing is simply incremented from 0
            if j < i:
                mat[k+j,j]   = vals[1]
            ## Otherwise the j's index must be added by 1 because the diagonal
            ## terms are being ignored
            else:
                mat[k+j,j+1] = vals[1]

        ## Increment i to iterate over next bus
        i += 1

    return mat

##===============================================================================
# Input:
#   N    : Number of visits
#   Q    : Number of chargers
#   t    : Type of matrix (float, int, ...)
#   vals : Array of values to be placed. i.e. [1, 2] will be placed as follows :
#          [[ 1 2 0 0 ...]
#           [ 0 0 1 2 ...]...]
#          By default the values will increment, but you can specify the values
#          as well
#
# Output:
#   An NxNQ matrix with the appropriate values
#
def NQNMat(N, Q, t, vals=[]):
    if not len(vals):
        vals = np.ones(Q, dtype=t)

    mat = NQMat(N, Q, t, vals)

    return mat

##===============================================================================
# Input:
#   N   : Number of visits
#   t   : Type of matrix (float, int, ...)
#   idx : Array of indices to place 1's. i.e. [0, 2] will be placed as follows :
#          [[ 1 0 0 ...]
#           [ 0 0 0 ...]
#           [ 0 0 2 ...]...]
#          By default the matrix will be the identity, but you can specify the
#          value as well
#
# Output:
#   An NxN matrix with 1's values placed on the appropriate diagonal
#
def NMat(N, t, idx=[]):
    invalid_val = -1

    if not len(idx):
        idx = np.ones(N, dtype=t)

    ones = np.zeros(N, dtype=t)

    for i in range(len(idx)):
        if idx[i] == invalid_val:
            continue

        ones[idx[i]] = 1

    mat = ones*np.eye(N, dtype=t)

    return mat
