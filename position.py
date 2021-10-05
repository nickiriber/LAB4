import numpy as np
import os
from datetime import datetime, timedelta

class Position:
    """A Class for handling Position Data"""
    
       

    def __init__(self):
       
    #list to hold time, lat, long, heights
        self.times = []
        self.latitudes = []
        self.longitudes = []
        self.heights = []
    
    #Data path to .RAW's
        self.data_path = "/home/jupyter-nirib/ESCI_872_Public/Data/"
    
    #Empty numpy array
        self.proj_pos = np.array([])
    
   
        self.metadata = dict([('geodetic_units', 'rad'), #
                   ('height_units', 'm'),
                   (' proj_units','m'),
                   ('geoid_name', None),
                   ('ellipsoid_name', None),
                   ('height_relative_to', None),
                   ('time_basis', 'UTC'),
                   ('proj_str', 'Unknown')])
        pass
    
    
    
    def __str__(self):
        return "%s" % str(self.metadata) # returns dict as str
    
    
        
    def ParseNMEA0183_GGA(self,
                          dt_str,
                          geoid_name,
                          ellipsoid_name,
                          height_relative_to): #missing date
    
        # Get the GGA string and tokenize it
        gga_data = dt_str.split(',')

        # verify that we have a GGA string
        if not gga_data[0][-3:] == "GGA":
            raise RuntimeError(
                'ParseNMEA0183_GGA: argument `dt_str` must be a GGA message')

        self.metadata["geoid_name"] = geoid_name
        self.metadata["ellipsoid_name"] = ellipsoid_name
        self.metadata["height_relative_to"] = height_relative_to
    

    
    def read_hypack_raw_file(self, fullpath):

        # This function will currently only function provided that there are GGA sentences 
        # in the records.
        # You may update the function to include other positioning messages as well, but 
        # this is outside the scope of the class

        # Check the File's existence
        if os.path.exists(fullpath):
            self.data_path = fullpath
            print('Opening GNSS data file:' + fullpath)
        else:  # Raise a meaningful error
            raise RuntimeError('Unable to locate the input file' + fullpath)

        # Open, read and close the file
        hypack_file = open(fullpath)
        hypack_content = hypack_file.read()
        hypack_file.close    

        # Split the file in lines
        hypack_records = hypack_content.splitlines()

        # Go through the header lines to find the date of the survey 
        # (not contained in the GGA records)

        lines_parsed=0
        for hypack_record in hypack_records:

            # Check for the time and date

            if hypack_record[:3].lower() == "tnd":
                hypack_datetime=datetime.strptime(hypack_record[4:23],
                                                  "%H:%M:%S %m/%d/%Y")

                print("HYPACK RAW Header start time and date: " +
                      hypack_datetime.ctime())

            # Keep track of the lines parsed
            lines_parsed+=1

            # Stop going through the records if the record starts with the string eoh 
            # (End Of Header)
            if hypack_record[:3].lower() == "eoh":
                break         

        # Keep track of the number of GGA records found

        num_gga_recs=0

        for hypack_record in hypack_records[lines_parsed:]:

            if hypack_record[19:22] == "GGA":
                gga_data=hypack_record.split()[3]
                
                return self.ParseNMEA0183_GGA(gga_data, self.metadata["geoid_name"], self.metadata["ellipsoid_name"], self.metadata["height_relative_to"])

           
#4.1 
