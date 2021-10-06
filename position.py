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
        self.qualities = []
        self.num_sats = []
        self.hdops = []
        self.undulations = [] 
        self.corr_ages = []
        self.corr_stations = []
    
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
    
    
    

    
    def ParseNMEA0183_GGA(self, dt_str,
                           geoid_name,
                           ellipsoid_name,
                           height_relative_to,
                           date=None):
            
        # Get the GGA string and tokenize it
        gga_data = dt_str.split(',')
        
        # Check the checksum given
        checksum = 0
        for c in dt_str[1:-3]:
            checksum ^= np.fromstring(c, dtype=np.uint8)
       
        if not hex(int(checksum))[2:] == gga_data[-1][-2:].lower():
            print('Checksum does not match, ignoring data')

        # verify that we have a GGA string
        if not gga_data[0][-3:] == "GGA":
            raise RuntimeError(
                'ParseNMEA0183_GGA: argument `dt_str` must be a GGA message')

        self.metadata["geoid_name"] = geoid_name
        self.metadata["ellipsoid_name"] = ellipsoid_name
        self.metadata["height_relative_to"] = height_relative_to
    
        # Determine the time of day from both the header and the GGA string

        gga_timedelta=timedelta(hours=int(gga_data[1][0:2]),\
                                minutes = int(gga_data[1][2:4]),\
                                seconds = int(gga_data[1][4:6]))

        # Set the time of the date to midnight
        
        date = datetime(date.year, date.month, date.day, 0, 0, 0)
        self.times.append(date + gga_timedelta)
        
        # Parse the latitude
        if gga_data[3].lower() == "n":
            lat = float(gga_data[2][0:2])+float(gga_data[2][2:])/60.
        else:
            lat = -float(gga_data[2][0:2])-float(gga_data[2][2:])/60.
        self.latitudes.append(lat)
        
        # Parse the longitude
        if gga_data[5].lower == "w":
            lon = float(gga_data[4][0:3])+float(gga_data[4][3:])/60.
        else:
            lon = -float(gga_data[4][0:3])-float(gga_data[4][3:])/60.
        self.longitudes.append(lon)
        
        # Parse the GNSS Quality indicator
        q = int(gga_data[6])
        self.qualities.append(q)
    
        # Parse the number of GNSS satellites used for the solution
        n_sats = int(gga_data[7])
        self.num_sats.append(n_sats)
        
        # Parse the HDOP Quality indicator
        hdop = float(gga_data[8])
        self.hdops.append(hdop)
        
        # Parse the orthometric height 
        height = float(gga_data[9])
        if not gga_data[10].lower() == 'm':
            raise RuntimeError('Orthomeric height units are not meters!')
        self.heights.append(height)
        
         # Parse the geoid ellipsoid undulation
        undulation = float(gga_data[11])
        if not gga_data[12].lower() == 'm':
            raise RuntimeError('Undulation units are not meters!')
        self.undulations.append(undulation)
                           
        # If there is more data then parse it
        corr_age = None
        corr_station = None
        if not gga_data[13] == "":
            corr_ages.append(float(gga_data[13]))
            corr_stations.append(float(gga_data[14][0:-3]))
            
            
            

    def read_hypack_raw_file(self, fullpath):

        # This function will currently only function provided that
        # there are GGA sentences in the records

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
                gga_data=hypack_record.split()[3] #index 3 starts with $GPGGA
                self.ParseNMEA0183_GGA(gga_data,
                                       "EGM08",
                                       "WGS84",
                                       "geoid",
                                       hypack_datetime)



    def write_hotlink(self, hotlink_path):

        fullpath, _ = os.path.splitext(self.data_path)

        fullpath = fullpath + "_pos.txt"

        # Check the File's existence

        if os.path.exists(fullpath):
            # Let the user now we are overwriting an existing file
            self.data_path = fullpath
            print('Overwriting file: ' + fullpath)
        else:  # Let the user know we are writing to a file
            print('Writing to file: ' + fullpath)

        output_file = open(fullpath, mode="w")  # mode="w" to open the file in writing mode

        # Write the header

        output_file.write('date time latitude longitude path\n')

        # Determine the duration associated to the positions in this object

        start_time = min(self.times)
        duration = max(self.times) - start_time
        

        # For each position write the date time longitude latitude path and fraction

        for i in range(0,len(self.times)):
            fraction = (self.times[i] - start_time) / duration
            line_content=str(self.times[i])+" %012.8f %013.8f %s?%f\n"%(self.latitudes[i],
                                                                        self.longitudes[i],
                                                                        hotlink_path,fraction)
            print(line_content)
            output_file.write(line_content)
            

            
            
    def __str__(self):
        
        txt = '\n'
        for key, value in self.metadata.items():
            txt += (key + ': ' + str(value) + '\n')
 
        txt +='\n'
        txt +='# of positions: %s \n'%(len(self.latitudes))    
        
        txt +='\n'
        txt +='Minimum latitude: %.8f \t| ' %(min(self.latitudes)) 
        txt +='Maximum latitude: %.8f\n' %(max(self.latitudes)) 
        txt +='Minimum longitude: %.8f | ' %(min(self.longitudes))
        txt +='Maximum longitude: %.8f \n' %(max(self.longitudes))
        txt +='Minimum height: %.2f \t\t| ' %(min(self.heights))
        txt +='Maximum height: %.2f \n' %(max(self.heights))
        
        txt +='\n'
        txt +='Start time: %s | ' %(min(self.times))
        txt +='End time: %s' %(max(self.times))

        
        return txt
