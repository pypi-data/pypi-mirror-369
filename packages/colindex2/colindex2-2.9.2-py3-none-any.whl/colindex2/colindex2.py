import gc, os
from collections import OrderedDict
import warnings 
warnings.filterwarnings('ignore') 
import numpy as np
import numpy.linalg as LA
import pandas as pd
import xarray as xr

from .modules import invert_gcd1_array, invert_gcd2_array
from .modules import check_zonal_loop
from .modules import add_cyclic_point_hand2
from .modules import _calc_sole_numba, _opt_params_numba, _input_ex_numba
from .modules import _envelope_AS_numba_simple

class Detect():
    """
    Depression detector by searching each optimal location, intensity, and size from 2D fields.
    See puplication for details (Kasuga et al. 2021; K21).

    ----

    Parameters:
    -----------

    **da** : ``xarray.DataArray`` or ``numpy.ndarray`` 
        If ``xarray.DataArray``, dims must contain ``longitude``/``lon``/``lons``
        , ``latitude``/``lat``/``lats``, ``time``/``valid_time`` and ``level``/``lev``/``isobaricInhPa``.

        If ``numpy.ndarray``, options ``lon`` and ``lat`` must be set, see Examples.

        If array is 3D, detection will be automatically looped for axis=0, assuming time axis.


    **odir** : ``str``, default ``'./d01'``
        Output directory. By defaults, output data will be stored as follows

        .. code-block:: text

            current_dir/
            └── d01/
                ├── AS/
                |   └── AS-{ty}-{yyyymmddhhTT}-{llll}.nc
                ├── V/
                    └── V-{ty}-{yyyymmddhhTT}-{llll}.csv

        where, ``AS-...nc`` is AS file (AS positive for ``ty='L'``, AS negative for ``ty='H'``),
        ``V-...csv`` is point values for each detection, 
        ``yyyymm`` is year & month,
        ``ty`` is ``'L'`` or ``'H'``, ``yyyymmddhhTT`` is year-month-day-hour-minute, ``llll`` is level.


    **r** : ``np.array``, default ``np.arange(300, 2101, 200)``
        Radial variable for AS [km].
        ``r=np.arange(200, 2101, 100)`` (K21).


    **ty** : ``str``, {``'L'``, ``'H'``}, default ``'both'``
        Type of depression to be detected.

        - ``'L'`` for cutoff lows and troughs
        - ``'H'`` for cutoff highs and ridges


    **stencil** : ``str``, {``'9g'``, ``'5g'``, ``'5l'``} default ``'9g'`` 
        - ``'9g'`` for 9 point stencil using great circle to calc AS
        - ``'5g'`` for 5 point stencil using great circle to calc AS
        - ``'5l'`` for 5 point stencil using latitude circle to calc AS (K21)


    **distinct** : ``bool``, default ``True``
        If ``True``, search local minima (maxima) for the input field
        to distinct whether a detection is cutoff low (cutoff high) (``ex=1``) or trough (ridge) (``ex=0``). 


    **SR_thres** : ``float``, default ``3.``
        Threshold to remove noises with respect to the slope ratio.


    **So_thres** : ``float``, default ``3.``
        Threshold to remove noises with respect to the intensity [m/100km].

        In K21, ``10`` and ``5`` was used for cutoff lows and preexisting troughs.


    **Do_thres** : ``float``, default ``0.``
        Threshold to remove noises with respect to the depth [m].

        A large value (e.g., ``10``) reduces small-size noise, opted for surface low/high detection.


    **xx_thres** : ``float``, default ``0.5``
        Threshold to remove noises with respect to the zonal laplacan [m/(100 km)^2].

        This works for high detection
        by removeing large and weak ridges located south of the subtropical jet.


    **t** : ``pandas.Timestamp`` or ``pandas.DatetimeIndex``, default ``[pd.Timestamp('1000-01-01 00:00')]``
        Option for ``numpy.ndarray`` input. This will be used as a label in output files.


    **lev** : ``int``, default ``0``
        Option for ``numpy.ndarray`` input. This will be used as a label in output files.


    **lons** : ``list`` or ``numpy.ndarray``, default ``[-999.]``
        Option for ``numpy.ndarray`` input. Set like ``lon=np.arange(0, 360, 1.25)`` according to data.


    **lats** : ``list`` or ``numpy.ndarray``, default ``[-999.]``
        Option for ``numpy.ndarray`` input. Set like ``lon=np.arange(-90, 90, 1.25)`` according to data.

    
    **save** : ``bool``
        If you do not want automatic outputs, set ``False``.

    **nc** : ``bool``
        If ``True``, netcdf file will be created for AS. If you want binary outputs, set ``False``.

    **fmt** : ``str``
        if ``nc=False``, this format will be used as outputs. The format follows ``dtype`` notation of numpy.

    ----

    Examples:
    ---------

    Read netcdf geopotential height data using ``xarray`` and select level by ``.sel()`` to reduce the vertical dimension. ::

        >>> import xarray as xr
        >>> z = xr.open_dataarray('path/to/file.nc').sel(level=300)

    Import ``Detect`` function with the height data.
    Set ``odir`` to specify output data directory.
    By defaults, outputs will be stored in ``./d01``. ::

        >>> from colindex2 import Detect
        >>> Detect(z)

    That is the simplest usage for detection with the default settings.

    Some additional examples are following.

    Read output csv with parsing time columns. ::

        >>> df = pd.read_csv('./d01/AS/201504/AS-L-201504010000-0300.nc', parse_dates=['time'])

    When you want to use a binary of 4byte little-endian. You can save flat binary by setting ``nc=False``.::

        >>> import numpy as np
        >>> import pandas as pd
        ...
        >>> # make dimensional arrays
        >>> time = pd.date_range('2015-04-01 00', '2015-04-30 18', freq='6H')  # or pd.Timestamp() for a single timestep data
        >>> lev = np.array([1000, 975, ..., 150, 100])
        >>> lats = np.arange(-90, 91, 1.25)
        >>> lons = np.arange(0, 360, 1.25)
        >>> it, ip, iy, iz = len(time), len(lev), len(lats), len(lons)
        ...
        >>> # read binary
        >>> with open('bin/file.bin') as a:
        ...     z = np.fromfile(a, dtype='<f4').reshape(it, ip, iy, ix)
        ...
        >>> # execute with specifying dimansional arrays
        >>> Detect(z[0, 15], time=time[0], lev=lev[15], lats=lats, lons=lons,
        ...        nc=False, fmt='>f4')  # 4-byte big-endian

    Using multiprocessing.
    NOTE: DataArray must be loaded before multiprocessing.
    (use `z = z.load` to explicitly load data) ::

        >>> import mutiprocessing as mp
        >>> from colindex2 import Detect
        >>> z = xr.open_dataarray('path/to/file.nc')
        ...
        >>> def main(z):
        ...     Detect(z)
        ...
        >>> if __name__ == '__main__':
        ...
        ...     # partitioning levels for multiprocessing
        ...     levs = [200, 300, 400, 500]
        ...     z_list = [z.sel(level=l) for l in levs]
        ...
        ...     # mutiprocess using mp.Pool
        ...     with mp.Pool(len(z_list)) as p:
        ...         p.map(main, z_list)

    """

    def __init__(self, da, odir='./d01',
                 r=np.arange(200, 2101, 100),
                 ty='both', stencil='9g', distinct=True,
                 SR_thres=3., So_thres=3., Do_thres=0., xx_thres=.5,
                 lev=0, t=[pd.Timestamp('1700-01-01 00:00')], lons=[-999.], lats=[-999.],
                 save=True, nc=True, fmt='<f4'
                 ):

        print("loading...")

        # constants
        self.rr = 6371.  # earth radius [km]
        self.g = 9.8  # gravity [m/ss]
        self.factor = 100.  # unit conv m/km -> m/100km

        self.t = t
        self.lev = lev
        self.ty = ty
        self.stencil = stencil
        self.r = np.array(r)
        self.odir = odir
        self.SR_thres = SR_thres
        self.So_thres = So_thres
        self.Do_thres = Do_thres
        self.xx_thres = xx_thres
        self.distinct = distinct

        # read main array
        if isinstance(da, xr.DataArray):

            _dims = [k for k, v in da.coords.items()]  # this may include squeezed dims

            if 'valid_time' in _dims:
                tt = pd.to_datetime(da.valid_time.values)
            elif 'time' in _dims:
                tt = pd.to_datetime(da.time.values)
            else:
                tt = t

            if isinstance(tt, pd.Timestamp):
                self.t = [tt]  # must be iterable
                self.da = da.values[np.newaxis, ...]
            else:
                self.t = tt  # pd.DatetimeIndex or default list
                self.da = da.values

            if 'level' in _dims:
                self.lev = da.level.values
            elif 'lev' in _dims:
                self.lev = da.lev.values
            elif 'levs' in _dims:
                self.lev = da.levs.values
            elif 'isobaricInhPa' in _dims:
                self.lev = da.isobaricInhPa.values

            if 'longitude' in _dims:
                self.lon = da.longitude.values
            if 'lon' in _dims:
                self.lon = da.lon.values
            if 'lons' in _dims:
                self.lon = da.lons.values

            if 'latitude' in _dims:
                self.lat = da.latitude.values
            if 'lat' in _dims:
                self.lat = da.lat.values
            if 'lats' in _dims:
                self.lat = da.lats.values


        elif isinstance(da, np.ndarray):

            if len(lons) != da.shape[-1] or len(lats) != da.shape[-2]:
                raise ValueError('shape of lons or lats not fit input')
            else:
                self.lon = lons
                self.lat = lats
        else:
            raise ValueError('wrong input data type, must be xr.DataArray or np.ndarray')

        self.da = self._check64(self.da)
        self.lon = self._check64(self.lon)
        self.lat = self._check64(self.lat)
        self.lev = self._check64(self.lev)

        if isinstance(self.lev, np.ndarray):
            self.lev = self.lev.item()

        self._run(save=save, nc=nc, fmt=fmt)

    def _check64(self, ar):
        if ar.dtype == np.float32:
            return ar.astype(np.float64)
        elif ar.dtype == np.int32:
            return ar.astype(np.int64)
        else:
            return ar

    def _run(self, save=True, nc=True, fmt='<f4'):
        """
        Execute detection.
        """

        # prep data and get meta
        self._prep()

        # make interp mesh for AS
        self.mesh = self._make_interp_mesh()

        # start time loop
        for i0 in range(len(self.t)):

            t = self.t[i0]
            self.time = f'{t.year}{t.month:02}{t.day:02}{t.hour:02}{t.minute:02}'

            # make arrays for AS, ro, m, n (for positive/negative)
            self._envelope_AS(i0)

            # make V (point values)
            self._opt_params(i0)

            # make X (point values) and check ex
            if self.distinct:
                self._input_ex(i0)
                
            # save AS and V
            if save:
                self.save(nc=nc, fmt=fmt)

            print("done", self.lev, self.time)


    def _prep(self):
        
        # original grid for on grid analysis
        self.daSkp = self.da
        self.lonSkp = self.lon
        self.latSkp = self.lat

        # check zonal loop for interpolation
        self.zloop = check_zonal_loop(self.lon)

        # lonIntrp must be positive
        if self.zloop == 'loop0':
            self.daIntrp, self.lonIntrp = add_cyclic_point_hand2(self.da, self.lon)
        else:
            self.daIntrp = self.da
            self.lonIntrp = self.lon
        # simple copy
        self.latIntrp = self.lat


    def _mk_da(self):
        coords = self._get_coords()
        dims = ['time', 'level', 'latitude', 'longitude']
        names = ['AS', 'ro', 'm', 'n']
        arrays = [self.AS, self.ro, self.m, self.n]
        das = []
        for n, a in zip(names, arrays):
            _a = a[0]
            da = xr.DataArray(_a.astype("f4")[np.newaxis, np.newaxis, :, :],
                              coords=coords, dims=dims)
            das.append(da)
            _a = a[1]
            da = xr.DataArray(_a.astype("f4")[np.newaxis, np.newaxis, :, :],
                              coords=coords, dims=dims)
            das.append(da)
        self.subs = das[2:]

        '''import matplotlib.pyplot as plt
        self.ASp, self.ASn = das[:2]
        shade = plt.contourf(self.ASp.squeeze())
        plt.colorbar(shade, shrink=.7)
        plt.title('ASp')
        plt.savefig(f'/Users/kasuga/Desktop/Figs/colinidex2_test3_intermittent/ASp2.png')
        plt.close()
        shade = plt.contourf(self.ASn.squeeze())
        plt.colorbar(shade, shrink=.7)
        plt.title('ASn')
        plt.savefig(f'/Users/kasuga/Desktop/Figs/colinidex2_test3_intermittent/ASn2.png')
        plt.close()
        quit()'''

    def save(self, nc=True, fmt='<f4'):
        self.save_AS(nc=nc, fmt=fmt)
        self.save_V()
        #self.save_X()

    def _save_field_nc(self, n, da):
        coords = self._get_coords()
        dims = ['time', 'level', 'latitude', 'longitude']
        da = xr.DataArray(da.astype("f4")[np.newaxis, np.newaxis, :, :],
                          dims=dims, coords=coords)
        ds = xr.Dataset({n: da})
        path = self._mk_path_name(n)
        ds.to_netcdf(path+'.nc')

    def _save_field_grd(self, n, ar, fmt='<f4'):
        path = self._mk_path_name(n)
        ar.astype(fmt).tofile(path+'.grd')

    def save_AS(self, nc=True, fmt='<f4'):
        if self.ty == 'L' or self.ty == 'both':
            if nc:
                self._save_field_nc('AS-L', self.AS[0])
            else:
                self._save_field_grd('AS-L', self.AS[0], fmt)
        if self.ty == 'H' or self.ty == 'both':
            if nc:
                self._save_field_nc('AS-H', self.AS[1])
            else:
                self._save_field_grd('AS-H', self.AS[1], fmt)

    def save_subs(self):
        self._mk_da()
        names = ['r-L', 'r-H', 'm-L', 'm-H', 'n-L', 'n-H']
        if self.ty == 'L' or self.ty == 'both':
            subs_dir_L = {n: da for n, da in zip(names, self.subs) if 'L' in n}
            ds = xr.Dataset(subs_dir_L)
            path = self._mk_path_name('S-L')
            ds.to_netcdf(path+'.nc')
        if self.ty == 'H' or self.ty == 'both':
            subs_dir_H = {n: da for n, da in zip(names, self.subs) if 'H' in n}
            ds = xr.Dataset(subs_dir_H)
            path = self._mk_path_name('S-H')
            ds.to_netcdf(path+'.nc')

    def _save_points(self, n):
        path = self._mk_path_name(n)
        if n == 'V-L': df = self.V[self.V.ty==0]
        if n == 'V-H': df = self.V[self.V.ty==1]
        if n == 'X-L': df = self.X[self.X.ty==0]
        if n == 'X-H': df = self.X[self.X.ty==1]
        df.to_csv(path+'.csv', index=False)

    def save_V(self):
        if self.ty == 'L' or self.ty == 'both':
            self._save_points('V-L')
        if self.ty == 'H' or self.ty == 'both':
            self._save_points('V-H')

    def save_X(self):
        if self.ty == 'L' or self.ty == 'both':
            self._save_points('X-L')
        if self.ty == 'H' or self.ty == 'both':
            self._save_points('X-H')


    def _mk_path_name(self, f):
        ym = self.time[:6]
        dd = f'{self.odir}/{f[:-2]}/{ym}'
        os.makedirs(dd, exist_ok=True)
        return f'{dd}/{f}-{self.time}-{self.lev:04}'


    def _get_coords(self):
        t = self.time
        Y,M,D,H,T = t[:4],t[4:6],t[6:8],t[8:10],t[10:12]
        return {
            'time': [pd.Timestamp(f'{Y}-{M}-{D} {H}:{T}')],
            'level': ('level', [self.lev], {'units': 'millibars'}),
            'latitude': ('latitude', self.latSkp,
                         {'units': 'degrees_north'}),
            'longitude': ('longitude', self.lonSkp,
                          {'units': 'degrees_east'})
        }


    def _make_interp_mesh(self):
        stencil = self.stencil

        lons, lats = np.meshgrid(self.lonSkp, self.latSkp)  # skipped grids

        if stencil == '9g':
            ths = np.arange(0., 359., 45.)
        else:
            ths = np.arange(0., 359., 90.)

        ih = len(ths)
        ir = len(self.r)
        lons2 = np.empty((ir, ih, len(self.latSkp), len(self.lonSkp)))
        lats2 = np.empty((ir, ih, len(self.latSkp), len(self.lonSkp)))

        for i, _r in enumerate(self.r):
            for j, _h in enumerate(ths):
                if stencil == '9g' or stencil == '5g':
                    lons2[i, j, ...], lats2[i, j, ...] = invert_gcd2_array(lons, lats, _h, _r)
                elif stencil == '5l':
                    lons2[i, j, ...], lats2[i, j, ...] = invert_gcd1_array(lons, lats, _h, _r)

        lon = self.lonSkp
        if self.zloop == 'loop0' or self.zloop == 'loop1':
            if self.zloop == 'loop0':
                lon_max = lon[-1] + (lon[1] - lon[0])
            else: lon_max = lon[-1]
            lon_min = lon[0]
            lons2 = np.where(lons2>lon_max, lons2-360., lons2)
            lons2 = np.where(lons2<lon_min, lons2+360., lons2)

        return lons2, lats2, ths


    def _envelope_AS(self, i0):

        lons2, lats2, ths = self.mesh
        _ret = _envelope_AS_numba_simple(
                self.daSkp[i0], self.lonSkp, self.latSkp,
                np.array(self.r), lons2, lats2, ths,
                self.daIntrp[i0], self.lonIntrp, self.latIntrp,
                self.stencil, self.zloop in ["loop0","loop1"])
        AS_en, r_en, m_en, n_en, xx_en, yy_en, xy_en  = _ret

        self.AS = AS_en * self.factor
        self.ro = r_en
        self.m = m_en * self.factor
        self.n = n_en * self.factor
        self.xx = xx_en
        self.yy = yy_en
        self.xy = xy_en


    def calc_sole(self, lon, lat, rad, i0):
        """
        Calculate AS(x,y,r,t) for any point (x,y,r,t).

        Parameters
        ----------
        lon : int, float
            Longitude (x) of AS.

        lat : int, float
            Latitude (y) of AS.

        rad : int, float
            Raius (r) of AS.

        i0 : int
            Timestep (t) to be calculated as index.
        """

        da = self.daIntrp[i0]
        lons = self.lonIntrp
        lats = self.latIntrp
        stencil = self.stencil
        zloop = self.zloop
        factor = self.factor

        return _calc_sole_numba(da, lons, lats, lon, lat, rad,
                                zloop, stencil, factor)


    def _opt_params(self, i0):
        l = _opt_params_numba(
                self.zloop, self.ty,
                self.stencil, self.factor,
                self.AS, self.ro, self.m, self.n,# self.AS3,
                self.xx, self.yy, self.xy,
                self.da[i0], self.lon, self.lat,
                self.lonSkp, self.latSkp, self.r, self.rr,
                self.lev,
                self.So_thres, self.Do_thres,
                self.SR_thres, self.xx_thres)
        ls_t = np.full(l[0].shape, self.t[i0])

        dic = OrderedDict([('time',ls_t), ('ty', l[0]),
                           ('lev',l[1]), ('lat',l[2]), ('lon',l[3]),
                           ('valV',l[4]),
                           ('So',l[5]), ('ro',l[6]), ('Do',l[7]),
                           ('SBG',l[8]), ('SBGang',l[9]),
                           ('m',l[10]), ('n',l[11]), ('SR',l[12]),
                           ('EE',l[13]), ('XX',l[14])])
        # store as V
        self.V = pd.DataFrame.from_dict(dic)


    def _input_ex(self, i0):

        l = _input_ex_numba(
                self.zloop, self.daSkp[i0], self.lonSkp, self.latSkp,
                self.rr, self.daIntrp[i0],
                self.lonIntrp, self.latIntrp, self.ty, self.lev,
                self.V.ty.values, self.V.lon.values,
                self.V.lat.values, self.V.ro.values)

        ls_t = np.full(l[0].shape, self.t[i0])
        dic = OrderedDict([('time',ls_t), ('ty', l[0]),
                           ('lev',l[1]), ('lat',l[2]), ('lon',l[3]),
                           ('val',l[4])])
        self.X = pd.DataFrame.from_dict(dic)
        
        #update V
        self.V['ex'] = l[5] 
        self.V['valX'] = l[6]
        self.V['lonX'] = l[7]
        self.V['latX'] = l[8]

