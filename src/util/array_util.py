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

##===============================================================================
# Input:
#   array: An array of elements
#   element: The element being looked for
#
# Output:
#   The index of the last actual visit of the bus
#
def lastVisit(array, element):
    found = False
    for i in range(len(array)-1, 0, -1):
        if array[i] == element:
            if found:
                return i
            else:
                found = True

    # Could not find the element
    return -1

##===============================================================================
# Input:
#   array   : An array of elements
#   element : The element being looked for
#   idx     : Index to start looking from
#
# Output:
#   The index of the last actual visit of the bus
#
def prevVisit(array, element, idx):
    for i in range(idx-1, -1, -1):
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

##===============================================================================
# Input:
#   size: integer for array length
#   t   : type of array
#
# Output:
#   Array of values corresponding to the matrix
def initArray(size: int, t) -> np.ndarray:
    return initArray(size, t)

##===============================================================================
#
def initArray(size: tuple, dtype=float) -> np.ndarray:
    """
    Initialize a numpy array of dimension tuple of type t

    Input:
        size: tuple for array length
        t   : type of array

    Output:
        Array of values corresponding to the matrix
    """
    return -1*np.ones(size, dtype=dtype)
