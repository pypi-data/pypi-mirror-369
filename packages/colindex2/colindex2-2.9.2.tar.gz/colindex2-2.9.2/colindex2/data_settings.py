import numpy as np
import pandas as pd

# DATA SETTINGS ----------
input_data_type = ""  # nc or <f4 or >f4
output_dir = "./d01"
output_data_type = ""  # nc or <f4 or >f4
# nc: netcdf
# <f4: little endian, 4-byte float binary
# >f4: big endian, 4-byte float binary

if input_data_type == "nc":
    pass
    #var_name = "z"  # when input has multiple variables
    #lon_name = ""  # use if each differs from "longitude"
    #lat_name = ""  # "latitude""
    #lev_name = ""  # "level"
    #time_name = ""  # "time"
else:  # for binary input
    lons = np.arange(-180, 180, 1.25)  # degrees east
    lats = np.arange(90, -90, -1.25)  # degrees north
    levs = [1000,975,925,900,875,850,800,775,750,700,650,600,500,450,400,350,300,250,225,200,175,150,125,100,85,70,60,50,40,30,20,10,7,5,3,2,1,0.7,0.3,0.1,0.03,0.01]  # hPa
    times = pd.date_range("1700-01-01 00", "1700-01-01 00", freq="6h")
    # document of pandas.date_range() is below
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.date_range.html

selected_levs = [300]  # hPa, must be list

# DETECTION SETTINGS ----------
detection_type = "L"
r = np.arange(300, 2100, 100)  # km
SR_thres = 3.  # non-dim, slope ratio
So_thres = 3.  # m/(100km), intensity
Do_thres = 0.  # m, depth
xx_thres = .5   # m/(100km)^2, zonal concavity (to remove low-lat. highs)

# TRACKING SETTINGS ----------
tracking_data_dir = output_dir  # no need to changee except for special case
tracking_times = pd.date_range("1700-01-01 00", "1700-01-01 00", freq="6h")
tracking_levs = []
parallel_levs = True  # if True, parallel processes for each tracking_levs
tracking_types = "L"  # L or H or both
tlimit = 200  # km/h, maximum tracking speed (Lupo et al. 2023)
DU_thres = 36.  # h, duration threshold (Munoz et al. 2020)
MAXSo_thres = 0.  # m/(100km), maximum intensity threshold
ALLDIST_thres = 0.  # km, accumurated moving distance threshold

long_term = False  # if True, ID will be reset as 1 when every 00UTC 1st January and confine searching window to 5 months
operational = False  # if True, tracking process starts from already tracked data which stored in Vt directory
    
