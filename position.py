import numpy as np
import os
from datetime import datetime, timedelta

class Position:
    """A Class for handling Position Data"""
    #list to hold time, lat, long, heights
    times = []
    latitudes = []
    longitudes = []
    heights = []
    
    data_path = ""
    
    #numpy array
    proj_pos = np.array([])
    
    #dict with metadata
    metadata = dict('geodetic_units': 'rad', #
               'height_units': 'm',
               ' proj_units':'m',
               'geoid_name': None,
               'ellipsoid_name': None,
               'height_relative_to': None,
               'time_basis': 'UTC',
               'proj_str': 'Unknown')
    

    def __init__(self):
        pass
    
    def __str__(self): 
        return self
    