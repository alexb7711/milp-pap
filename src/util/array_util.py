#!/usr/bin/python

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
        if norm_arr[i] <= lb:
            norm_arr[i] = 0
        else:
            norm_arr[i] -= lb

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
    return [arr[i] for i in range(arr.shape[0])]
