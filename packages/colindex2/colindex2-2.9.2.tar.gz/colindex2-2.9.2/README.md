# colindex2

<div align="left">
  <img src="map.png" width="40%">
</div>

A python package for atmospheric depression detection and tracking. The main target is to capture upper tropospheric depressions such as cutoff lows and blockng highs from their earlier stages of troughs and ridges, respectively, with their seamless transitions of vortex-related variables.

### Reference

- Kasuga, S., M. Honda, J. Ukita, S. Yaname, H. Kawase, and A. Yamazaki, 2021: Seamless detection of cutoff lows and preexisting troughs. *Monthly Weather Review*, **149**, 3119–3134, [https://doi.org/10.1175/MWR-D-20-0255.1](https://doi.org/10.1175/MWR-D-20-0255.1)  

- Kasuga, S., and M. Honda, 2025: Climatology of Cutoff Lows Approaching Japan. *SOLA*, **21**, 329-333, [https://doi.org/10.2151/sola.2025-049](https://doi.org/10.2151/sola.2025-049)

<!--
:warning: The tracking scheme is underconstruction and its definition may be changed unnoticed. The relatively stabe versions are v2.7.6, and v2.8.1 See Tags and CHANGELOG. (edit: 2025.4.30)
-->

# Install

```
pip install colindex2
```
Dependecies are `numpy`, `pandas`, `numba`, `scipy`, `xarary`, `netCDF4`, and `h5netcdf`. 
<!--
> If you use anaconda environment, prepare the dependencies using `conda` in advance and then install `colindex2` using conda's `pip`, as recommended by [ANACONDA](https://www.anaconda.com/blog/using-pip-in-a-conda-environment).  
-->

# Tutorial
Try [colindex2_tutorial.ipynb](colindex2_tutorial.ipynb).

# Table of contents
[[_TOC_]]

# How to execute
## Import use for python users

Below examples excecute the detection and tracking with default settings.

```python
# importing
import xarray as xr
from colindex2 import Detect, Track

# make xr.DataArray of a latitude-longitude 2-dimensional field
# with a temporal axis (such as "time"/"valid_time")
z = xr.open_dataarray("z.nc")

# execute detection with default options
Detect(z)

# execute tracking with default options
# set date range (pd.date_range) and level of the field (e.g., 300 hPa) to be tracked
track_times = pd.date_range("yyyy-mm-dd hh", "yyyy-mm-dd hh", freq="6h")
Track(track_times, 300)
```

<details>

<summary> Important arguments and defaults </summary>

- For `Detect()`

| args| values | description |
| ---- | ----------- | ----- |
| odir | "./d01" | parent output directory name |
| r | np.arange(200,2101,100) | searching radius variable r [km]|
| SR_thres | 3.0 | SR threshold to remove tiny trough |
| So_thres | 3.0 | So threshold to remove weak vortices [m/100km]|

For more details, see [source code](colindex2/colindex2.py#L192)

- For `Track()`

| args| values | description |
| ---- | ----------- | ----- |
| odir | "./d01" | parent output directory name |
| tlimit | 150.0 | Traveling speed limit to prevent wrong connections by large depressions [km/h]. Default 150 km/h is 900 km in 6 hour. |
| long_term | False | If False, tracking ID will be continuously counted up during the analysis period, and massive memory usage may occur. If True, tracking ID will be labeled from 1 in every 00UTC 1st Jan. |
| DU_thres | 0 | Threshold for noise removal with respect to duration (life time) [hour]. Note this parameter is sensitive to short-time noise, thus to remove noises try 24 or 36. |

For more details, see [source code](colindex2/tracking_overlap2.py#L142)

</details>

## Command use for non-python users
But, python3 and requirements must be installed.  

If you add `-h` for the respective commands, their documets will be appear.

- 1. Generate data_settings.py

```
$ gen_data_settings
```

- 2. Edit [data_settings.py](data_settings.py)

- 3. Run detection

```
$ detect z.nc
```

- 4. Run tracking

```
$ track
```

- Draw maps to check tracking data and AS (netcdf output only)

```
$ draw_map z.nc ./d01 L 300 nps
```

- Find and make each tracking data

```
$ find_track ./d01 L 300 a
```

# How to use outputs
## Directory structure of outputs

```
current_dir/
|
└── d01/  # default name
    |
    ├── AS/  # 2D averaged slope function
    |   └── AS-{ty}-{yyyymmddhhTT}-{llll}.nc (or .grd)
    |
    ├── V/   # point values after detection
    |   └── V-{ty}-{yyyymmddhhTT}-{llll}.csv
    |
    ├── Vt/  # intermediate data
    |   └── V-{ty}-{yyyymmddhhTT}-{llll}.csv
    |
    ├── Vtc/ # final point values after tracking
    |    └── V-{ty}-{yyyymmddhhTT}-{llll}.csv
    |
    └── ID/  # continuous csv for a specific track whose id is `ID`
         └── {ty}-{l}-{yyyymm}-{ID}.csv
```
where, `ty` is `L` or `H`, `yyyymmddhhTT` is timestep, `llll` is level in 4 digits, and `l` is level.  

## How to load outputs in programs

- python3

 point data (`V` and `Vtc`, csv) 
```python
import pandas as pd
df = pd.read_csv(path_to_V, parse_dates=["time"])
```
 mesh data (`AS`, netcdf)
```python
import xarray
da = xr.open_dataarray(path_to_AS)
```
- julia

 point data (`V` and `Vtc`, csv) 
```julia
using CSV, DataFrames, Dates
df = CSV.read(path_to_V, DataFrame)
df.time = DateTime.(df.time, "yyyy-mm-dd HH:MM:SS")
```
 mesh data (`AS`, netcdf)
```julia
using Datasets
ds = Dataset(path_to_AS)
ar = ds["AS"][:,:]
```

## Variable parameters for point value csv (`Vct`)

<details>
<summary> Click here </summary>

| Names| Description |
| ---- | ----------- |
| time | Time. |
| ty | 0 for lows and troughs, 1 for highs and ridges |
| lev | Level. Usually in hPa. |
| lat, lon | Central coorditates in latitude and longitude. |
| valV | Value of input field on the center |
| valX | Value of the nearest local minimum (maximum) of input field for a low (high). |
| lonX,latX | Latitude and longitude of the nearest local extremum. If the deteciton depressino is trough or ridge, this value will be 999.9 |
| So | Optimal slope [m/100 km]. Intensity of depresion (as circular geostrophic winds). |
| ro | Optimal radius [r km]. Size of depression (as a radius of the circulation). |
| Do | Optimal depth [m]. Vertical depth of depression, generally proportional to ro. |
| SBG | Background slope [m/100 km]. |
| SBGang | Angle of Background slope vector [radian]. 0 for east. |
| m, n | Zonal, meridional components of SBG, respectivelly [m/100 km]. |
| SR | Slope ratio. For analytic characters of a Gaussian-shaped depression, 0.-1.34 for vortices, 1.34- for waves, and larger values (e.g., 3.) for ripples in a jet. |
| ex | Distinction between depressions and waves. <br>1 (there is a extremum within ro\*0.65) for lows/highs and 0 (otherwise) for troughs/ridges. |
| EE | Eccentricity (1 for pure isotropic, smaller values for Ellipses). |
| XX | Zonal discrete laplacian with a step of ro [m/(100 km)**2]. Small value means the feature has weak structure in zonal like sub-tropical ridges. |
| ID | Identification number. Tend to be larger than number of detection since it includes noises |
| MERGE | Merge lysis flag. <br>`-1` for soritary lysis, <br>`-2` for being merged from someone, <br>`-3` for lysis at the end of analysis, <br>`-4` for being involved in the secondary proces (see Fig. S2 in KH25), <br>other integers for the object ID of its merge lysis. |
| SPLIT | Split genesis flag. <br>`-1` for soritary genesis, <br>`-2` for being splitting and producing someone, <br>`-3` for genesis at the start of analysis, <br>`-4` for being involved in the secondary proces (see Fig. S2 in KH25), <br>other integers for the object ID of its split genesis. |
| DIST | Moving distance in a timestep [km]. Central difference. When merge/split/genesis/lysis, value will be missing, and the same applies to SPEED and DIR. |
| SPEED | Moving speed [m/s]. DIST/timestep. |
| DIR | Moving direction [radian]. 0 for east. |
| \_ DC | Accumulated duration [timestep] including before split. |
| DU | Duration [hour]. |
| XS | Sequential duration being ex=1 (lows/highs). |
| QS5 | 1 for Quasi-stational with 85% temporal overlapping of ro circles. |
| QS7 | As with QS5 but with 70%. |
| ALLDIST | Accumulated moving distance [km]. |
| MEDDIST | Median moving distance of all timesteps [km]. |
| MAX | 1 for the maximum development timestep (maximum So). |
| MAXSo | So when MAX. |
| MAXXS | Maximum duration of XS in a track (XS can be scored in multiple sequences). |
| MAXQS5 | Maximum duration of QS5 in a track. |
| MAXQS7 | Maximum duration of QS7 in a track. |
| exGEN | Genesis as vortex (`ex` changed from `0` to `1` for t-1 to t). |
| exLYS | Lysis as vortex (`ex` changed from `1` to `0` for t to t+1). |

</details>

## How to get csv for a specific track

Please obtain the ID for a specific depressin and its appeared year and month in advance.

Use `find_one` function by importing Finder.

```python
from colindex2 import Finder

# set output dir (default:"`./d01`") and timestep of output csv in `Vtc`
F = Finder(odir="./d01", timestep=6)

# set type (`"L"` or `"H"` for low or high detection, respectively), level (e.g., 300 hPa here), and year/month with 6 digits (e.g., 201504) when the feature appeared, and ID for the specific feature (e.g., 333)
# here, the result will be produced at "`./d01/ID/L-300-201504-333.csv`"
F.find_one("L", 300, 201504, 333)

# try below to concatenate the specific track with before splitting from and after merging to other features
F.find_one("L", 300, 201504, 333, before_split=True, after_merge=True)
```

You can use following functions (experimental, welcome bug reports!)

- `count_all(ty, lev)`: Print out count of all tracks on the specific level in the output directory.

- `find_all(ty, lev, all_in_one=False)`: Search all tracks on the specific level in a whole time range and save them as csvs. Recommended only for case studies.

