# System Modules
import numpy as np
import csv
from itertools import zip_longest


##===============================================================================
# STATIC
##===============================================================================
e_cell = 'nan'

##===============================================================================
# PUBLIC
##===============================================================================

##-------------------------------------------------------------------------------
#
def outputData(fn, dm, path: str='data/'):
    """
    Output data in a format for LaTeX to be able to plot

    Input:
      - fn : Base name of the file
      - dm : Data manager
      - str: Path to output directory

    Output:
      - Data files
    """
    __chargeOut(fn,dm,path)
    __usageOut(fn,dm,path)
    __powerOut(fn,dm,path)
    __scheduleOut(fn,dm,path)
    return

##===============================================================================
# PRIVATE
##===============================================================================

##-------------------------------------------------------------------------------
#
def __chargeOut(fn,dm,path):
    """
    Output charge plot data
Input:
    - fn : Base name of the file
    - dm : Data manager
    - str: Path to output directory

Output:
    - Data files
    """
    # Variables
    name     = fn+'-charge'
    N      = dm['N']
    A      = dm['A']
    G      = dm['Gamma']
    eta    = dm['eta']
    u      = dm['u']
    c      = dm['c']
    v      = dm['v']
    r      = dm['r']
    g      = dm['g']
    data   = -1*np.ones((2*N,2*A))
    fields = [['time'+str(i), 'eta'+str(i)] for i in range(A)]
    fields = [j for k in fields for j in k]

    # For every bus
    for j in range(A):
        t_i = 0

        ## For every visit
        for i in range(N):
            ### If the visit is for the bus of interest
            if G[i] == j:
                #### Append the charge on arrival
                data[t_i][j*2 + 0] = u[i]
                data[t_i][j*2 + 1] = eta[i]

                #### Append the charge on departure
                data[t_i+1][j*2 + 0] = c[i]
                data[t_i+1][j*2 + 1] = eta[i] + g[i][int(v[i])]*r[int(v[i])]

                #### Update index
                t_i += 2

    # Write data to disk
    __saveToFile(path, name, fields, data)

    return

##-------------------------------------------------------------------------------
#
def __usageOut(fn,dm,path):
    """
    Output charger usage data

    Input:
        - fn : Base name of the file
        - dm : Data manager
        - str: Path to output directory

    Output:
        - Data files
    """
    # Variables
    name   = fn+'-charge-cnt'
    K      = dm['K']
    N      = dm['N']
    T      = dm['T']
    u      = dm['u']
    c      = dm['c']
    v      = dm['v']
    slow   = dm['slow']
    data   = np.zeros((K,3), dtype=float)
    fields = ['visit', 'slow', 'fast']

    # For each visit
    idx = 0
    for k in np.linspace(0,T,K):
        data[idx,0] = k
        for i in range(N):
            if u[i] <= k and c[i] >= k:
                if v[i] < slow: data[idx,1] += 1
                else          : data[idx,2] += 1
        idx += 1

    # Write data to disk
    __saveToFile(path, name, fields, data)
    return

##-------------------------------------------------------------------------------
#
def __powerOut(fn,dm,path):
    """
    Output power usage data

    Input:
        - fn : Base name of the file
        - dm : Data manager
        - str: Path to output directory

    Output:
        - Data files
    """
    # Variables
    name   = fn+'-power-usage'
    K      = dm['K']
    N      = dm['N']
    T      = dm['T']
    c      = dm['c']
    r      = dm['r']
    u      = dm['u']
    v      = dm['v']
    data   = np.zeros((K,1), dtype=float)
    fields = ['power']

    # For each visit
    idx = 0
    for k in np.linspace(0,T,K):
        for i in range(N):
            if u[i] <= k and c[i] >= k: data[idx] += r[v[i]]
        idx += 1

    # Write data to disk
    __saveToFile(path, name, fields, data)
    return

##-------------------------------------------------------------------------------
#
def __scheduleOut(fn,dm,path):
    """
    Output schedule data

    Input:
        - fn : Base name of the file
        - dm : Data manager
        - str: Path to output directory

    Output:
        - Data files
    """
     # Variables
    name   = fn+'-schedule'
    A      = dm['A']
    N      = dm['N']
    G      = dm['Gamma']
    c      = dm['c']
    r      = dm['r']
    u      = dm['u']
    v      = dm['v']
    data   = -1*np.ones((2*N,3*A), dtype=float)
    fields = [['charger'+str(i), 'u'+str(i), 'c'+str(i)] for i in range(A)]
    fields = [j for k in fields for j in k]

    # For each visit
    for i in range(N):
        data[i][G[i]*3+0]   = v[i]
        data[i][G[i]*3+1]   = u[i]
        data[i+1][G[i]*3+2] = c[i]

    # Write data to disk
    __saveToFile(path, name, fields, data)
    return

##-------------------------------------------------------------------------------
#
def __saveToFile(path, name, fields, data):
    """
    Write data to CSV file

    Input:
        - path   : Path to output directory
        - name   : Name of the file
        - fields : Title each column
        - data   : Matrix of data

    Output:
        - CSV file located at 'PATH/NAME' with DATA as content
    """
    # Variables
    fn = path + name + ".csv"

    # Convert data to strings
    data = [[str(e) for e in row] for row in data]

    # For each row
    for row in data:
        ## For each item in the row
        for i in range(len(row)):
            ### if the row item is a '-1.0', replace it
            if row[i] == "-1.0": row[i] = e_cell

        ## If the row is only commas, clear it
        if row[1:] == row[:-1] and e_cell in row[:]: row.clear()

    # Save data to disk
    with open(fn, 'w') as csvfile:
        writer = csv.writer(csvfile)                                            # Create writer object
        writer.writerow(fields)                                                 # Write fields
        writer.writerows(data)

    return
