#!/usr/bin/python

# Standard Lib
import numpy as np

##===============================================================================
# Input:
#   N: Number of visits
#   Q: Number of chargers
#   vals: Array of values to be placed. i.e. [1, 2] will be placed as follows:
#       [[ 1 2 0 0 ...]
#        [ 0 0 1 2 ...]...]
#         By default the values will increment, but you can specify the values
#         as well
#   t: Type of matrix (float, int, ...)
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
