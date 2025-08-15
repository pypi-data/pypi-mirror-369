import sys, os
import multiprocessing as mp
import argparse
import importlib.util
import numpy as np
import pandas as pd
import xarray as xr
from .colindex2 import Detect
from .tracking_overlap2 import Track
from .get_IDfile import Finder

def gen_data_settings():
    text = """\
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
    #lon_name = ""  # when input longitude short name differs from "longitude"
    #lat_name = ""  # ... "latitude"
    #lev_name = ""  # ... "level"
    #time_name = ""  # ... "time"
else:  # for binary input
    lons = np.arange(-180, 180, 1.25)  # degrees east
    lats = np.arange(90, -90.1, -1.25)  # degrees north
    levs = [1000,975,925,900,875,850,825,800,775,750,700,650,600,550,500,450,400,350,300,250,225,200,175,150,125,100,85,70,60,50,40,30,20,10,7,5,3,2,1,0.7,0.3,0.1,0.03,0.01]  # hPa

selected_levs = [300]  # hPa, must be list

# DETECTION SETTINGS ----------
detection_type = "L"
r = np.arange(200, 2100, 100)  # km
SR_thres = 3.  # non-dim, slope ratio
So_thres = 3.  # m/(100km), intensity
Do_thres = 0.  # m, depth
xx_thres = .5   # m/(100km)^2, zonal concavity (to remove low-lat. highs)

# TRACKING SETTINGS ----------
tracking_data_dir = output_dir  # no need to changee except for special case
tracking_levs = selected_levs  # no need to changee except for special case
tracking_times = pd.date_range("1700-01-01 00", "1700-01-01 00", freq="6h")
tracking_types = "L"  # L or H or both
parallel_levs = True  # if True, parallel processes for each tracking_levs

tlimit = 150.  # km/h, maximum tracking speed (Lupo et al. 2023)
DU_thres = 36.  # h, duration threshold (Munoz et al. 2020)
MAXSo_thres = 0.  # m/(100km), maximum intensity threshold
ALLDIST_thres = 0.  # km, accumurated moving distance threshold

long_term = False  # if True, ID will be reset to 1 when every 00UTC 1st January and confine searching window to 5 months
    """
    with open("./data_settings.py", "w") as a:
        a.write(text)

def divide_chunks(ar,n):          
    d,m = np.divmod(len(ar),n)
    ar2 = []
    for i in range(n):
        if i != n-1:
            ar2.append(ar[d*i:d*(i+1)])
        else:
            ar2.append(ar[d*i:])
    return ar2


def _detect_wrapper(args):
    Detect(*args)

def _track_wrapper(args):
    Track(*args)

def _load_local_module(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} has not generated yet. Use gen_data_settings command")
    spec = importlib.util.spec_from_file_location("data_settings", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["data_settings"] = module
    spec.loader.exec_module(module)
    return module


def detect():
    description = """
Run detection of colindex.
Before run, generate data_settings.py with 'gen_data_settings' command and edit it.

 $ gen_data_settings

Then execute below for netcdf input.

 $ detect path/to/file.nc

For binary input, specify start/end times (st,et) and frequency of timesteps (freq).

 $ detect path/to/file.grd -st "yyyy-mm-dd hh" -et "yyyy-mm-dd hh" -freq 6h

Output point data and AS mesh data will be stored in output_dir/V and output_dir/AS.
Option -n can set number of multiprocess (default 4)

            """
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("input_data_path", type=str, help="input data path")
    parser.add_argument("-n", type=int, help="number of multiprocessing, default is 4.", default=4)
    parser.add_argument("-st", type=str, help="start timestep yyyy-mm-dd hh", default="1700-01-01 00")
    parser.add_argument("-et", type=str, help="end timestep yyyy-mm-dd hh", default="1700-01-01 00")
    parser.add_argument("-freq", type=str, help="frequency of timestep for pd.date_range, default is '6h'", default="6h")
    args = parser.parse_args()
    input_data_path = args.input_data_path
    cpu = args.n
    st = args.st
    et = args.et
    freq = args.freq

    data_settings_path = os.path.join(os.getcwd(), "data_settings.py")
    if not os.path.exists(data_settings_path):
        raise FileNotFoundError("there is no data_settings.pn in the current directory. generate it with 'gen_data_settings' command.")
    D = _load_local_module(data_settings_path)

    if D.input_data_type == "nc":
        if not hasattr(D, "var_name"):
            da = xr.open_dataarray(input_data_path)
        else:
            ds = xr.open_dataset(input_data_path)
            da = ds[D.var_name]

        if hasattr(D, "lon_name"):
            da = da.rename({D.lon_name:"longitude"})
        if hasattr(D, "lat_name"):
            da = da.rename({D.lat_name:"latitude"})
        if hasattr(D, "lev_name"):
            da = da.rename({D.lev_name:"level"})
        if hasattr(D, "time_name"):
            da = da.rename({D.time_name:"time"})

        lons = da.longitude.values
        lats = da.latitude.values
        levs = da.level.values
        times = pd.to_datetime(da.time.values)
        da = da.values
        fmt = None

    else:
        lons = D.lons
        lats = D.lats
        levs = D.levs
        #times = D.times
        times = pd.date_range(st,et,freq=freq)
        shape = (len(times),len(levs),len(lats),len(lons))
        fmt = D.input_data_type
        with open(input_data_path, "r") as a:
            da = np.fromfile(a, dtype=fmt).reshape(shape)

    stencil = "9g"
    distinct = True
    if D.output_data_type == "nc":
        nc = True
    else:
        nc = False
        fmt = D.output_data_type

    divided_times = divide_chunks(times, cpu)
    divided_time_slices = [slice(np.where(times==t[0])[0][0],np.where(times==t[-1])[0][0]+1) for t in divided_times]

    idx_levs = np.where(np.isin(levs, D.selected_levs))[0]

    for l in idx_levs:
        print("preparing ...", levs[l])
        das = [da[t,l,:,:] for t in divided_time_slices]
        lev = levs[l]
        args = [(das[i],D.output_dir,D.r,D.detection_type,stencil,distinct,
                 D.SR_thres,D.So_thres,D.Do_thres,D.xx_thres,
                 lev,times[divided_time_slices[i]],lons,lats,
                 True,nc,fmt) for i in range(cpu)]

        with mp.Pool(cpu) as p:
            p.map(_detect_wrapper, args)

def track():
    description = """
Run tracking of colindex. Before run, edit TRACKING SETTINGS section in data_settings.py

 $ track

Tracking point data will be stored in output_dir/Vtc.

            """
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    args = parser.parse_args()

    data_settings_path = os.path.join(os.getcwd(), "data_settings.py")
    if not os.path.exists(data_settings_path):
        raise FileNotFoundError("there is no data_settings.pn in the current directory. generate it with 'gen_data_settings' command.")
    D = _load_local_module(data_settings_path)

    if len(D.tracking_times) == 1:
        raise ValueError("'tracking_times' is not correct. set it in 'data_settings.py'")

    if D.tracking_types == "both":
        tys = ["L","H"]
    else:
        tys = [D.tracking_types]

    for ty in tys:

        args = [(D.tracking_times,lev,ty,
                D.tracking_data_dir,D.tlimit,
                #D.long_term,D.operational,
                D.long_term,False,
                D.DU_thres,D.MAXSo_thres,D.ALLDIST_thres) for lev in D.tracking_levs]

        if D.parallel_levs:
            with mp.Pool(len(D.tracking_levs)) as p:
                p.map(_track_wrapper, args)
        else:
            for i in range(len(tracking_levs)):
                _track_wrapper(args[i])

def find_track():
    description = """
Search tracking for specific IDs and save. Four arguments are required.
 $ find output_dir type lev freqH type2

The fourth argument 'type2' can be set 3 types:

c: only count number of all tracks
 $ find ./d01 L 300 6 c

A: find all tracks and save them as an all-included csv output_dir/all_{type}_{lev}.csv.
 $ find ./d01 L 300 6 A

a: find all tracks and save them separately in output_dir/ID/.
 $ find ./d01 L 300 6 a

(digit of ID): find one track labeled by ID. Add fifth argument of 'yyyymm' (year month) when the track observed, as following
 $ find ./d01 L 300 6 2222 202302

 This will produce a track obtained from 6-hour intarval data for 300-hPa level whose ID is 2222, appears in Feb 2023. 
 If add -a (-b) option at its tail, the tracks after merging (before splitting) are connected.
 $ find ./d01 L 300 6 2222 202302 -a
 $ find ./d01 L 300 6 2222 202302 -b
 $ find ./d01 L 300 6 2222 202302 -a -b

 """
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("odir", type=str, help="output data directory")
    parser.add_argument("ty", type=str, help="L or H")
    parser.add_argument("lev", type=str, help="level")
    parser.add_argument("freqH", type=int, help="frequency of timestep in hour")
    parser.add_argument("type2", nargs="+", type=str, help="A or a or c or 'ID yyyymm'")
    parser.add_argument('-a', '--option_a', action='store_true', default=False, help='follow track after merge')
    parser.add_argument('-b', '--option_b', action='store_true', default=False, help='follow track before split')
    args = parser.parse_args()
    odir = args.odir
    ty = args.ty
    lev = int(args.lev)
    type2 = args.type2

    #data_settings_path = os.path.join(os.getcwd(), "data_settings.py")
    #D = _load_local_module(data_settings_path)
    #freqH = int(D.tracking_times.inferred_freq[:-1])
    freqH = args.freqH

    f = Finder(odir, freqH)

    if type2[0] == "a":
        f.find_all(ty,lev)
    elif type2[0] == "c":
        f.count_all(ty,lev)
    elif type2[0] == "A":
        f.find_all(ty,lev,all_in_one=True)
    elif args.option_a:
        f.find_one(ty,lev,int(type2[1]), int(type2[0]),after_merge=True)
    elif args.option_b:
        f.find_one(ty,lev,int(type2[1]), int(type2[0]),before_split=True)
    else:
        f.find_one(ty,lev,int(type2[1]), int(type2[0]))
