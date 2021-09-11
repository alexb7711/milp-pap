#!/usr/bin/python

# Standard Lib
import numpy as np

# Developed
from array_util import *

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
#       [[ -1 1 0 0 0 0 ...]
#        [ -1 0 1 0 0 0 ...]
#        [ -1 0 1 0 0 0 ...]
#        [ -1 0 0 1 0 0 ...]...]
#   to loop through every combination
#
def XiNMat(Xi, N, t, vals=[1,-1]):
    # Local Variables
    history = np.zeros((N,N))
    mat     = []

    # Loop through each possibility
    for i in range(N):
        for j in range(N):
            ## Check if this permutation has been addressed before
            if history[i,j] != 1 and i != j:
                ### Update history
                history[i,j] = 1

                ### Create array
                temp = np.zeros(N)
                temp[i] = vals[1]
                temp[j] = vals[0]

                ### Append array to mat
                mat.append(temp)
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

##===============================================================================
# Input:
#   N     : Number of visits
#   t     : Type of matrix (float, int, ...)
#   init  : Array of initial charges
#   first : Array of initial visit indices
#
# Output:
#   An NxN matrix with 1's values placed on the appropriate diagonal
#
def alphaMat(N, t, init, first):
    ones = np.zeros(N, dtype=t)

    for i in first:
        ones[i] = 1

    mat = ones*np.eye(N, dtype=t)

    return mat

##===============================================================================
# Input:
#   N   : Number of visits
#   Q   : Number of chargers
#   t   : Type of matrix (float, int, ...)
#   arr : vector to be reshaped
#
# Output:
#   NxQ matrix made of vec values
#
def NQReshape(N, Q, arr):
    # Local Vars
    ## Matrix to be returned
    mat = []

    ## Index of array
    idx = 0

    for i in range(N):
        temp = []
        for j in range(Q):
            temp.append(arr[idx])
            idx      += 1

        mat.append(temp)

    return np.array(mat)

##===============================================================================
# Input:
#   N : Number of visits
#
# Output:
#   Assuming N = 3, the matrix would be of the form:
#
#   [[1 0 0 0 0 0],
#    [0 1 0 0 0 0],
#    [0 0 1 0 0 0]]
#
#   As to represent [i,j] and [j,i] being active at the same time
#
def sdMat(N):
    Xi      = N*(N-1)
    mat     = []
    history = np.zeros((N,N))

    # Loop through each permutation
    for i in range(N):
        for j in range(N):
            ## Check if this permutation has been addressed before
            if history[i,j] != 1 and i != j:
                ### Update history
                history[i,j] = 1

                ### Create array
                temp = sdRow(N,i,j)

                ### Append array to mat
                mat.append(temp)

    #  print(np.array(mat))
    #  input("Press Enter...")

    return np.array(mat)

##===============================================================================
# Input:
#   N : Number of visits
#
# Output:
#   Assuming N = 3, the matrix would be of the form:
#
#   [[1 0 0 1 0 0],
#    [0 1 0 0 1 0],
#    [0 0 1 0 0 1]]
#
#   As to represent [i,j] and [j,i] being active at the same time
#
def sd2Mat(N):
    Xi      = N*(N-1)
    mat     = []
    history = np.zeros((N,N))

    # Loop through each permutation
    for i in range(N):
        for j in range(N):
            ## Check if this permutation has been addressed before
            if history[i,j] != 1 and i != j:
                ### Update history
                history[i,j] = 1
                history[j,i] = 1

                ### Create array
                temp = sd2Row(N,i,j)

                ### Append array to mat
                mat.append(temp)

    #  print(np.array(mat))
    #  input("Press Enter...")

    return np.array(mat)
