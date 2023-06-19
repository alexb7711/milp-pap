#!/usr/bin/python

# Standard Lib
import sys

# Include In Path
sys.path.append("./src/schedule/")
sys.path.append("./src/util/")

# Developed
from data_manager import DataManager
from scheduler import Schedule

##===============================================================================
#
def test_schedule_generation_csv():
    # Create a schedule
    s = Schedule(None, "./src/config", "./src/data")
    return
