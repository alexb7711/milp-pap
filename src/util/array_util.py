#!/usr/bin/python

# Standard Lib
import numpy as np

##===============================================================================
# Input:
#   array: An array of elements
#   element: The element being looked for
#
# Output:
#   The index of the first occurence of the specified element
def first(array, element):
    for i in range(len(array)):
        if array[i] == element:
            return i

    # Could not find the element
    return -1

##===============================================================================
# Input:
#   array: An array of elements
#   element: The element being looked for
#
# Output:
#   The index of the last occurence of the specified element
def final(array, element):
    for i in range(len(array)-1, 0, -1):
        if array[i] == element:
            return i

    # Could not find the element
    return -1

##===========================================================================
# Input:
#   lb: Lower bound to normalize off of
#   arr: Array to adjust values from
#
# Output:
#   Normalized array where values less than lb are zero and values greater than
#   lb are normalized from it
#
def adjustArray(lb, arr):
    norm_arr = arr.copy()

    for i in range(len(norm_arr)):
        if norm_arr[i] < lb:
            norm_arr[i] = -1
        else:
            norm_arr[i] = i

    return norm_arr

##===========================================================================
# Input:
#   garr: Gurobi array values to be placed in matrix
#   size: Size of array to be created
#
# Output:
#   Array of gurobi values
def toArr(garr):
    arr = garr.copy()
    return arr.tolist()

##===========================================================================
# Input:
#   N: Number of elements to be in the full size array
#   t: Type of variables in array (float, int, etc...)
#   idx: Indices of values to be set as 'value'
#   value: The number for each index to be set to (default = 1)
#
# Output:
#   Array of size N with 'value' placed in idx's locations
#
def toFullLen(N, t, idx, value=1):
    arr = np.zeros(N, dtype=t)

    for i in idx:
        arr[i] = value

    return arr

##===============================================================================
# Input:
#   mat: matrix
#
# Output:
#  vector representation of matrix
#
def mat2Vec(mat):
    mat = np.array(mat)
    m,n = mat.shape
    vec = np.zeros(m*n)
    i   = 0

    for m in mat:
        for n in m:
            vec[i] = n
            i     += 1

    return vec

##===============================================================================
# Input:
#   i: Row
#   j: Column
#
# Output:
#   Array of values corresponding to the matrix
def sdRow(m,i,j):
    # Generate NxN representation
    t_mat      = np.zeros((m,m))
    t_mat[i,j] = 1

    # Remove diagonal terms
    strided = np.lib.stride_tricks.as_strided
    s0,s1   = t_mat.strides
    mat     = strided(t_mat.ravel()[1:], shape = (m-1,m), strides = (s0+s1,s1)).reshape(m,-1)

    return mat2Vec(mat)

##===============================================================================
# Input:
#   i: Row
#   j: Column
#
# Output:
#   Array of values corresponding to the matrix
def sd2Row(m,i,j):
    # Generate NxN representation
    t_mat      = np.zeros((m,m))
    t_mat[i,j] = 1
    t_mat[j,i] = 1

    # Remove diagonal terms
    strided = np.lib.stride_tricks.as_strided
    s0,s1   = t_mat.strides
    mat     = strided(t_mat.ravel()[1:], shape = (m-1,m), strides = (s0+s1,s1)).reshape(m,-1)

    return mat2Vec(mat)
