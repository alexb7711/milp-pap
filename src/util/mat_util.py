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
#   val : The value to be placed in the matrix
#
# Output:
#   An XixN matrix. The values will be placed as
#       [[ -1  1  0  0 0 0 ...]
#        [  1 -1  0  0 0 0 ...]
#        [  0  0 -1  1 0 0 ...]
#        [  0  0  1 -1 0 0 ...]
#
def QNMat(Xi, N, t, val=1):

    # Initialize Matrix
    mat = np.zeros((Xi, N), dtype=t)

    # Place value in appropriate locations
    ## Bus i
    i = 0

    ## Bus j
    j = 0

    ## Loop through each possible combination
    for k in range(Xi):
        for l in range(N):
            ### Check if i is out of bound
            if i >= Xi:
                break
            ### Ignore diagonals
            elif j == l:
                continue

            mat[i,j] = -1
            mat[i,l] = 1
            i       += 1

        j = j + 1 if j+1 < N else 0

    print(mat)

    return mat
