from numba import jit, njit
import numba
import numpy as np
import numpy.linalg as LA
import xarray as xr


def conv_second(dt):
    # 'H' and 'T' are deprecated since pandas-2.2.0
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases

    if 'H' in dt or 'h' in dt:
        if 'H' == dt:
            _h = 1
        else:
            _h = int(dt[:-1])
        return 60*60*_h

    elif 'D' in dt:
        if 'D' == dt:
            _d = 1
        else:
            _d = int(dt[:-1])
        return 60*60*24*_d

    elif 'T' in dt or 'min' in dt:
        if 'T' == dt:
            _T = 1
        else:
            _T = int(dt[:-1])
        return 60*_T


def great_circle_distance(_lon1, _lat1, _lon2, _lat2, r=6371.):
    """calculate great-circle distance [km]"""

    if type(_lon1) != type(np.array([0])) and type(_lon2) != type(np.array([0])):
        arrays = False
        if _lon1 == _lon2 and _lat1 == _lat2:
            return 0.
    else:
        arrays = True

    lon1 = _lon1*np.pi/180
    lon2 = _lon2*np.pi/180
    lat1 = _lat1*np.pi/180
    lat2 = _lat2*np.pi/180

    if not arrays:
        ds = np.arccos(np.sin(lat1)*np.sin(lat2)
                       +np.cos(lat1)*np.cos(lat2)*np.cos(abs(lon1-lon2)))
    else:
        lon_bool = np.where(lon1==lon2, True, False)
        lat_bool = np.where(lat1==lat2, True, False)
        ds = np.where((lon_bool)&(lat_bool), 0.,
                      np.arccos(np.sin(lat1)*np.sin(lat2)
                                +np.cos(lat1)*np.cos(lat2)*np.cos(abs(lon1-lon2))))

    return r*ds


@njit
def great_circle_distance_numba(_lon1, _lat1, _lon2, _lat2) :
    """calculate great-circle distance [km]"""

    rr = 6371.

    lon1 = _lon1*np.pi/180
    lon2 = _lon2*np.pi/180
    lat1 = _lat1*np.pi/180
    lat2 = _lat2*np.pi/180

    ds = np.arccos(np.sin(lat1)*np.sin(lat2)
                   +np.cos(lat1)*np.cos(lat2)*np.cos(np.abs(lon1-lon2)))
    return ds*rr


@njit
def moving_direction(lon_B, lat_B, lon_F, lat_F):
    
    b = great_circle_distance_numba(lon_B, lat_B, lon_F, lat_F)
    a = great_circle_distance_numba(lon_F, lat_B, lon_F, lat_F)

    alpha = np.arcsin(a/b)  # returns 0 ~ pi/2 since 0 < a/b < 1
    # shogen (temae/oku -> east/west x north/south)
    d_lon_abs = np.abs(lon_B - lon_F)
    d_lon = lon_F - lon_B
    d_lat1 = lat_F - lat_B
    d_lat2 = lat_F + lat_B
    
    temae = d_lon_abs < 90. or 270. <= d_lon_abs < 360.
    oku = not temae
    east = 0. < d_lon < 180. or -360 < d_lon < -180.
    west = not east 
    
    shogen = 0
    
    if temae and east:
        if d_lat1 > 0: shogen = 1
        else: shogen = 4
    if temae and west:
        if d_lat1 > 0: shogen = 2
        else: shogen = 3
    if oku and east:
        if d_lat2 > 0: shogen = 1
        else: shogen = 4
    if oku and west:
        if d_lat2 > 0: shogen = 2
        else: shogen = 3                    

    if shogen == 0:
        raise ValueError('shogen error!')
        
    if shogen == 1:
        azimuth = alpha
    elif shogen == 2:
        azimuth = np.pi - alpha
    elif shogen == 3:
        azimuth = np.pi + alpha
    elif shogen == 4:
        azimuth = 2*np.pi - alpha

    return azimuth


@njit
def invert_gcd2_array(lons, lats, theta, d):

    lons_flat = lons.flatten()
    lats_flat = lats.flatten()
    org_shape = lons.shape
    lon_end_flat = np.empty_like(lons_flat)
    lat_end_flat = np.empty_like(lats_flat)

    for i in range(len(lons_flat)):
        lon = lons_flat[i]
        lat = lats_flat[i]
        _ret = invert_gcd2(lon, lat, theta, d)
        lon_end_flat[i] = _ret[0]
        lat_end_flat[i] = _ret[1]
    lons_end = lon_end_flat.reshape(org_shape)
    lats_end = lat_end_flat.reshape(org_shape)

    return lons_end, lats_end


@njit
def invert_gcd1_array(lons, lats, theta, d):

    lons_flat = lons.flatten()
    lats_flat = lats.flatten()
    org_shape = lons.shape
    lon_end_flat = np.empty_like(lons_flat)
    lat_end_flat = np.empty_like(lats_flat)

    for i in range(len(lons_flat)):
        lon = lons_flat[i]
        lat = lats_flat[i]
        _ret = invert_gcd1(lon, lat, theta, d)
        lon_end_flat[i] = _ret[0]
        lat_end_flat[i] = _ret[1]
    lons_end = lon_end_flat.reshape(org_shape)
    lats_end = lat_end_flat.reshape(org_shape)

    return lons_end, lats_end


@njit
def invert_gcd2(lon, lat, theta, d):
    """
    invert great circle distance and get new coordinate
    using Spherical Trigonometry

    Parameters
    ----------
    lon, lat: coordinate of the start point [degree]
    theta: angle from east toward the end point [degree]
    d: travel distance [km]

    Return
    ------
    coordinate(s) of the end point(s) (lon_end, lat_end) [degree]
    """

    rr = 6371.  # mk, earth radius

    # convert angles within +-360
    theta2 = np.divmod(theta, 360.)[1]

    A = np.deg2rad(90.-theta2)
    c = d/rr  # center angle between pos. vectors of start and end [radian]

    b = np.deg2rad(90.-lat)  # zenith of start point

    # cosine formula of Spherical Trigonometry
    cos_a = np.cos(b)*np.cos(c) + np.sin(b)*np.sin(c)*np.cos(A)
    a = np.arccos(cos_a)  # zenith of end point [radian]
    lat_end = 90. - np.rad2deg(a)

    if np.sin(b) == 0.:  #start point is N/S pole
        return theta2, lat_end
    if np.sin(a) == 0.:  #end point is N/S pole
        return 0., lat_end

    _N = np.cos(c) - np.cos(a)*np.cos(b)
    _D = np.sin(a)*np.sin(b)
    cos_C = _N/_D

    if cos_C > 1.:
        C = 0.
    elif cos_C < -1.:
        C = np.pi
    else:
        C = np.arccos(cos_C)  # memo: np.arccos() retruns positive value
    
    if -90 < theta2 < 90. or 270. < theta2:
        lon_end = lon+np.rad2deg(C)
    else:
        lon_end = lon-np.rad2deg(C)

    # convert angles within +-360
    lon_end2 = np.divmod(lon_end, 360.)[1]

    return lon_end2, lat_end



@njit
def invert_gcd1(lon, lat, theta, d):

    rr = 6371.  # earth radius [km]

    # cannot calc polar region
    if lat < -75 or lat > 75:
        return np.nan, np.nan

    b = np.deg2rad(90.-lat)  # zenith of start point

    if theta == 0.:
        lat_end2 = lat
        c = d/(rr*np.cos(np.deg2rad(lat)))
        lon_end2 = lon + np.rad2deg(c)

    if theta == 90.:
        lon_end = lon
        c = d/rr
        lat_end = lat + np.rad2deg(c)

        # convert angles within +-90 in lat
        if lat_end > 90.:
            lon_end2 = 180.+lon_end
            lat_end2 = 180.-lat_end
        else:
            lon_end2 = lon_end
            lat_end2 = lat_end

    if theta == 180.:
        lat_end2 = lat
        c = d/(rr*np.cos(np.deg2rad(lat)))
        lon_end2 = lon - np.rad2deg(c)

    if theta == 270.:
        lon_end = lon
        c = d/rr
        lat_end = lat - np.rad2deg(c)

        # convert angles within +-90 in lat
        if lat_end < -90.:
            lon_end2 = 180.+lon_end
            lat_end2 = -180.-lat_end
        else:
            lon_end2 = lon_end
            lat_end2 = lat_end

    # convert angles within +-360 in lon, +-90 in lat
    lon_end3 = np.divmod(lon_end2, 360.)[1]

    return lon_end3, lat_end2


@njit
def check_zonal_loop(lons):

    dlon = lons[1] - lons[0]

    if lons[-1] == lons[0]:
        return 'loop1'  # already overlapped

    l = lons[-1] + dlon

    if l == lons[0] or l+360 == lons[0] or l-360 == lons[0]: 
        return 'loop0'  # not overlapped
    else:
        return 'region'


def get_center_field(da, lon, da_bool=False):
    # converting lon2 -> lon1
    if da_bool:
        c = da.sel(longitude=lon)
    else:
        c = da.sel(longitude=lon).data
    return c


@njit
def interp_numba(ar, lons, lats, lons3, lats3, loop):
    
    iy, ix = lons3.shape
    array = np.full((iy, ix), np.nan)

    for j in range(iy):
        _lat = lats3[j]

        for i in range(ix):
            _lon = lons3[j, i]

            if np.isnan(_lon) or np.isnan(_lat): continue

            if not loop:
                if _lon < lons.min() or _lon > lons.max():
                    array[j, i] = np.nan
                    continue

            if _lat < lats.min() or _lat > lats.max():
                array[j, i] = np.nan
                continue

            # search nearest
            dlat = 100000.
            nearj = -1
            for jj, rlat in enumerate(lats):
                _dlat = np.abs(_lat-rlat)
                if _dlat < dlat:
                    dlat = _dlat
                    nearjj = nearj  # second nearest
                    nearj = jj  # nearest
            if nearjj == -1:  nearjj = 1

            dlon = 100000.
            neari = -1
            for ii, rlon in enumerate(lons):
                _dlon = np.abs(_lon-rlon)
                if _dlon < dlon:
                    dlon = _dlon
                    nearii = neari  # second nearest
                    neari = ii  # nearest
            if nearii == -1:  nearii = 1
                
            #  A---|------D
            #  |b        b|
            #  P---X------Q
            #  | c    d   |
            #  |          |
            #  |a        a|
            #  B---|------C

            a = np.abs(_lat-lats[nearjj])
            b = np.abs(_lat-lats[nearj])
            c = np.abs(_lon-lons[neari])
            d = np.abs(_lon-lons[nearii])

            A = ar[nearj, neari]
            B = ar[nearjj, neari]
            C = ar[nearjj, nearii]
            D = ar[nearj, nearii]
            
            array[j, i] = ((A*a+B*b)*d+(D*a+C*b)*c)/(a+b)/(c+d)

    return array


def add_cyclic_point_hand2(ar, lon):
    """add index 0 after index -1
    01234 -> 012340 """
    last_lon = lon[-1] + (lon[1]-lon[0])
    #last_ar =  ar[:, 0][:, np.newaxis]
    last_ar =  ar[...,:, 0][...,:, np.newaxis]
    ar = np.concatenate([ar, last_ar], axis=-1)
    lon = np.concatenate([lon, np.array([last_lon])])
    return ar, lon


@njit
def _envelope_AS_numba_simple(c, lon, lat, r, lons2, lats2, ths, da_bg, dblons, dblats, stencil, loop):

    iy, ix = len(lat), len(lon)  # may be skipped, not looped
    ir = len(r)

    AS = np.zeros((2,iy, ix))  # not looped
    rr = np.zeros((2,iy, ix))
    mm = np.empty((2,iy, ix))
    nn = np.empty((2,iy, ix))
    xx = np.empty((2,iy, ix))
    yy = np.empty((2,iy, ix))
    xy = np.empty((2,iy, ix))
    around = np.empty((8,iy,ix))

    pi = np.pi
    cos45 = np.cos(pi/4)

    for _r in range(ir):
        rad=r[_r]

        if stencil == '9g':
            for h, _ in enumerate(ths):
                around[h] = interp_numba(da_bg, dblons, dblats,
                                         lons2[_r, h, :, :], lats2[_r, h, :, 0],
                                         loop)

            e, ne, n, nw, w, sw, s, se = around

            _AS = (n+s+e+w+ne+nw+sw+se-8*c) / 8 / rad
            _m = (e-w)/4/rad + (ne+se-nw-sw)/8/rad/cos45
            _n = (n-s)/4/rad + (ne+nw-se-sw)/8/rad/cos45
            # ellips compression factor(ee) est by eign val of Hessian
            _xx = (e+w-2*c)/rad/rad
            _yy = (n+s-2*c)/rad/rad
            _xy = (ne-nw-se+sw)/4/rad/cos45

        elif stencil == '5g' or stencil == '5l':
            for h, _ in enumerate(ths):
                around[h] = interp_numba(da_bg, dblons, dblats, 
                                         lons2[_r, h, :, :], lats2[_r, h, :, 0],
                                         loop)
            e, n, w, s = around[0], around[1], around[2], around[3]

            _AS = (n+s+e+w-4*c) / 4 / rad
            _m = (e-w) / 2 / rad
            _n = (n-s) / 2 / rad
            _xx = (e+w-2*c)/rad/rad
            _yy = (n+s-2*c)/rad/rad
            _xy = np.zeros((iy,ix))

        # update arrays
        for j in range(iy):
            for i in range(ix):
                if _AS[j,i] > AS[0,j,i]:
                    rr[0,j,i] = rad
                    mm[0,j,i] = _m[j,i]
                    nn[0,j,i] = _n[j,i]
                    xx[0,j,i] = _xx[j,i]
                    yy[0,j,i] = _yy[j,i]
                    xy[0,j,i] = _xy[j,i]
                    AS[0,j,i] = _AS[j,i]
                if _AS[j,i] < AS[1,j,i]:
                    rr[1,j,i] = rad
                    mm[1,j,i] = _m[j,i]
                    nn[1,j,i] = _n[j,i]
                    xx[1,j,i] = _xx[j,i]
                    yy[1,j,i] = _yy[j,i]
                    xy[1,j,i] = _xy[j,i]
                    AS[1,j,i] = _AS[j,i]
    
    return AS, rr, mm, nn, xx, yy, xy


@njit
def search_localextrema(f, maxmin, relax=2, zloop=False,
                        as2=np.array([[0]])):
    iy, ix = f.shape

    if zloop:    # zonal loop
        wide = np.empty((iy, ix+2))
        wide[:, :1] = f[:, -1:]
        wide[:, 1:-1] = f[:, :]
        wide[:, -1:] = f[:, :1]
        o = f[1:-1, :]  # center
    else:
        wide = f
        o = f[1:-1, 1:-1]  # center

    as2_flag = False
    if as2.shape != (1,1):
        as2_flag = True
        if zloop:
            ant = as2[1:-1,:]
        else:
            ant = as2[1:-1,1:-1]

    # around 8 grids
    stencil_num = 8

    if maxmin == 'maximum':
        lmp = np.zeros((iy, ix),dtype=np.int64)
        # max search
        n = np.where(wide[ 2:  , 1:-1] - o <= 0, 1, 0)
        s = np.where(wide[  :-2, 1:-1] - o <= 0, 1, 0)
        w = np.where(wide[ 1:-1,  :-2] - o <= 0, 1, 0)
        e = np.where(wide[ 1:-1, 2:  ] - o <= 0, 1, 0)
        ne = np.where(wide[ 2:  , 2:  ] - o <= 0, 1, 0)
        se = np.where(wide[  :-2, 2:  ] - o <= 0, 1, 0)
        nw = np.where(wide[ 2:  ,  :-2] - o <= 0, 1, 0)
        sw = np.where(wide[ :-2,  :-2] - o <= 0, 1, 0)
        if as2_flag:
            _S = n + s + w + e + ne + se + nw + sw
            S = np.where(np.abs(o)>np.abs(ant),_S,0)
        else:
            S = n + s + w + e + ne + se + nw + sw
        if zloop:
            lmp[1:-1, :] = np.where(S>=stencil_num-relax, 1, 0)
        else:
            lmp[1:-1, 1:-1] = np.where(S>=stencil_num-relax, 1, 0)

    elif maxmin == 'minimum':
        lmp = np.zeros((iy, ix),dtype=np.int64)
        # min search
        n = np.where(wide[ 2:  , 1:-1] - o >= 0, 1, 0)
        s = np.where(wide[  :-2, 1:-1] - o >= 0, 1, 0)
        w = np.where(wide[ 1:-1,  :-2] - o >= 0, 1, 0)
        e = np.where(wide[ 1:-1, 2:  ] - o >= 0, 1, 0)
        ne = np.where(wide[ 2:  , 2:  ] - o >= 0, 1, 0)
        se = np.where(wide[  :-2, 2:  ] - o >= 0, 1, 0)
        nw = np.where(wide[ 2:  ,  :-2] - o >= 0, 1, 0)
        sw = np.where(wide[ :-2,  :-2] - o >= 0, 1, 0)
        if as2_flag:
            _S = n + s + w + e + ne + se + nw + sw
            S = np.where(np.abs(o)>np.abs(ant),_S,0)
        else:
            S = n + s + w + e + ne + se + nw + sw
        if zloop:
            lmp[1:-1, :] = np.where(S>=stencil_num-relax, 1, 0)
        else:
            lmp[1:-1, 1:-1] = np.where(S>=stencil_num-relax, 1, 0)

    return lmp


@njit
def search_nearest2(coords, target):

    # check target is in coords
    if target < coords.min() or coords.max() < target:
        return 0, 0

    first = True
    for i in range(len(coords)):

        v = coords[i]
        d_new = np.abs(target-v)

        if first:
            first = False
            d = d_new
            ni = i
            continue

        if d_new < d:
            d = d_new
            ni = i

    if ni == 0:
        nii = ni + 1

    elif ni == len(coords)-1:
        nii = ni - 1

    elif np.abs(target-coords[ni+1]) < np.abs(target-coords[ni-1]):
        nii = ni + 1

    else:
        nii = ni - 1

    return ni, nii


@njit
def bilinear_interp(ar, lons, lats, _lon, _lat):         
    """bi-liner interpolation"""

    shape = ar.shape

    if len(lons) not in shape or len(lats) not in shape:
        raise ValueError('lons, lats, levs, and times must have the same coordinate in ar')

    ni, nii = search_nearest2(lons, _lon)
    nj, njj = search_nearest2(lats, _lat)

    a = np.abs(_lat-lats[njj])
    b = np.abs(_lat-lats[nj])
    c = np.abs(_lon-lons[ni])
    d = np.abs(_lon-lons[nii])

    A = ar[nj, ni]
    B = ar[njj, ni]
    C = ar[njj, nii]
    D = ar[nj, nii]

    return ((A*a+B*b)*d+(D*a+C*b)*c)/(a+b)/(c+d)


@njit
def _tripod_approx_point(n, s, e, w):
    """
    Approximate a missing point value
    with other valid three point values.
    """

    if np.isnan(n):
        n2 = e+w-s
        e2,w2,s2 = e,w,s
    elif np.isnan(s):
        s2 = e+w-n
        e2,w2,n2 = e,w,n
    elif np.isnan(e):
        e2 = n+s-w
        n2,s2,w2 = n,s,w
    elif np.isnan(w):
        w2 = n+s-e
        n2,s2,e2 = n,s,e
    else:
        n2,s2,e2,w2 = n,s,e,w

    return n2, s2, e2, w2

@njit
def _calc_sole_numba(da, lons, lats, lon, lat, rad,
                     zloop, stencil='9g', factor=100.):

    # make interp z
    if stencil == '9g':
        ths = np.array([0.,45.,90.,135.,180.,225.,270.,315.,])
    else:
        ths = np.array([0.,90.,180.,270.])

    drad = rad / 10
    rad += drad

    for i in range(10):
        rad -= drad

        around = np.empty_like(ths)

        for l in range(len(ths)):
            
            if stencil == '9g':
                lon2, lat2 = invert_gcd2(lon, lat, ths[l], rad)
            else:
                lon2, lat2 = invert_gcd1(lon, lat, ths[l], rad)

            if zloop == 'loop0' or zloop == 'loop1':
                if zloop == 'loop0':
                    lon_max = lons[-1] + (lons[1] - lons[0])
                else: lon_max = lons[-1]
                lon_min = lons[0]

                if lon2 > lon_max: lon2 = lon2 - 360.
                if lon2 < lon_min: lon2 = lon2 + 360.

            around[l] = bilinear_interp(da, lons, lats, lon2, lat2)

        c = bilinear_interp(da, lons, lats, lon, lat)

        # calculate AS
        if stencil == '9g':
            e, ne, n, nw, w, sw, s, se = around

            # for nan included data, experimental
            #_e, _ne, _n, _nw, _w, _sw, _s, _se = around
            #n,s,e,w = _tripod_approx_point(_n,_s,_e,_w)
            #ne,sw,se,nw = _tripod_approx_point(_ne,_sw,_se,_nw)

            #if np.isnan([n,s,e,w,ne,sw,se,nw]).any():
            if np.isnan(n) or np.isnan(s) or np.isnan(e) or np.isnan(w) or np.isnan(ne) or np.isnan(sw) or np.isnan(se) or np.isnan(nw):
                continue

            # main parameter
            AS = (n+s+e+w+ne+nw+sw+se-8*c) / 8 / rad
            _m = (e-w)/4/rad + (ne+se-nw-sw)/8/rad/np.cos(np.pi/4)
            _n = (n-s)/4/rad + (ne+nw-se-sw)/8/rad/np.cos(np.pi/4)
            # ellips compression factor(ee) est by eign val of Hessian
            xx = (e+w-2*c)/rad/rad
            yy = (n+s-2*c)/rad/rad
            xy = (ne-nw-se+sw)/4/rad/np.cos(np.pi/4)
            H = np.array([[xx, xy], [xy, yy]])
            if np.isnan(xx) or np.isnan(xy) or np.isnan(yy):
                ee = np.nan
            else:
                eigs = LA.eig(H)[0]
                axes = np.reciprocal(np.sqrt(np.abs(eigs)))
                ee = min(axes)/max(axes)

        else:
            e, n, w, s = around
            AS = (n+s+e+w-4*c) / 4 / rad
            _m = (e-w) / 2 / rad
            _n = (n-s) / 2 / rad
            xx = (e+w-2*c)/rad/rad
            ee = 1.
            
        AS = AS * factor
        m = _m * factor
        n = _n * factor
        return c, AS, m, n, ee, xx

    # there is no clean data
    return np.nan,np.nan,np.nan,np.nan,np.nan,np.nan

@njit
def _get_both(lmp_l,lmp_h,val):
    lmp2=lmp_l+lmp_h
    _l = np.where(lmp_l,val[0],0.0)
    _h = np.where(lmp_h,val[1],0.0)
    _b = _l + _h
    return _b.flatten()[np.where(lmp2.flatten())]

@njit
def _opt_params_numba(zloop, ty, stencil, factor,
                      _AS, _ro, _m, _n,# _AS3,
                      _xx,_yy,_xy,
                      da, lons, lats, lonSkp, latSkp,
                      r, rr, lev,
                      So_thres, Do_thres, SR_thres, xx_thres):

    zloop2 = 'loop' in zloop

    if ty == "L" or ty == "H":
        if ty == 'L':
            AS = _AS[0]
            ro = _ro[0]
            m = _m[0]
            n = _n[0]
            xx = _xx[0]
            yy = _yy[0]
            xy = _yy[0]
            lmp = search_localextrema(AS, 'maximum', zloop=zloop2, as2=_AS[1])
        elif ty == 'H':
            AS = _AS[1]
            ro = _ro[1]
            m = _m[1]
            n = _n[1]
            xx = _xx[1]
            yy = _yy[1]
            xy = _xy[1]
            lmp = search_localextrema(AS, 'minimum', zloop=zloop2, as2=_AS[0])
        ls_y, ls_x = np.nonzero(lmp)
        ls_lat = latSkp[ls_y]
        ls_lon = lonSkp[ls_x]
        lmp_flat = lmp.flatten()
        ls_valV = da.flatten()[np.where(lmp_flat)]
        ls_So = AS.flatten()[np.where(lmp_flat)]
        ls_ro = ro.flatten()[np.where(lmp_flat)]
        ls_m = m.flatten()[np.where(lmp_flat)]
        ls_n = n.flatten()[np.where(lmp_flat)]
        if ty == "L":
            ls_ty = np.full(ls_n.shape, 0)
        elif ty == "H":
            ls_ty = np.full(ls_n.shape, 1)

        #ls_ee = np.ones_like(ls_ro)
        #ls_xx = np.ones_like(ls_ro)
        ls_xx = xx.flatten()[np.where(lmp_flat)]
        ls_yy = yy.flatten()[np.where(lmp_flat)]
        ls_xy = xy.flatten()[np.where(lmp_flat)]

    elif ty == 'both':
        lmp_l = search_localextrema(_AS[0], 'maximum', zloop=zloop2, as2=_AS[1])
        lmp_h = search_localextrema(_AS[1], 'minimum', zloop=zloop2, as2=_AS[0])
        lmp3 = lmp_l + lmp_h
        ls_y, ls_x = np.nonzero(lmp3)
        ls_lat = latSkp[ls_y]
        ls_lon = lonSkp[ls_x]
        ls_So = _get_both(lmp_l,lmp_h,_AS)
        ls_ro = _get_both(lmp_l,lmp_h,_ro)
        ls_m = _get_both(lmp_l,lmp_h,_m)
        ls_n = _get_both(lmp_l,lmp_h,_n)
        ls_valV = da.flatten()[np.where(lmp3.flatten())]
        _ty_l = np.where(lmp_l,0,0)
        _ty_h = np.where(lmp_h,1,0)
        _ty = _ty_l + _ty_h
        ls_ty = _ty.flatten()[np.where(lmp3.flatten())]

        #ls_ee = np.ones_like(ls_ro)
        #ls_xx = np.ones_like(ls_ro)
        ls_xx = _get_both(lmp_l,lmp_h,_xx)
        ls_yy = _get_both(lmp_l,lmp_h,_yy)
        ls_xy = _get_both(lmp_l,lmp_h,_xy)

    ls_So = np.abs(ls_So)  # positive for H
    ls_Do = ls_So * ls_ro / factor  #[gpm]
    ls_SBG = (ls_m**2.+ls_n**2.)**.5 #[gpm/100km]
    ls_SBGang = np.arctan2(ls_n, ls_m)  #[rad]
    ls_SR = ls_SBG / ls_So

    ls_lev = np.full(ls_lon.shape, lev)

    # loop for ee
    ls_ee = np.zeros(ls_lon.shape)
    for i in range(len(ls_xx)):
        xx=ls_xx[i]
        yy=ls_yy[i]
        xy=ls_xy[i]
        H = np.array([[xx, xy], [xy, yy]])
        if np.isnan(xx) or np.isnan(xy) or np.isnan(yy):
            ls_ee[i] = np.nan
        else:
            eigs = LA.eig(H)[0]
            axes = np.reciprocal(np.sqrt(np.abs(eigs)))
            ls_ee[i] = np.min(axes)/np.max(axes)

    ls_xx = np.abs(ls_xx) * factor * factor

    ## noise reduction constraints ###########
    idx = np.full((len(ls_lon)), True)
    for i in range(len(ls_lon)):
        # remove weak depression
        if ls_So[i] < So_thres:
            idx[i] = False; continue
        # remove shallow noise (mainly due to orography)
        if ls_Do[i] < Do_thres:
            idx[i] = False; continue
        # remove weak wave
        if ls_SR[i] > SR_thres:
            idx[i] = False; continue
        # remove high-ellipticity depression
        #if ls_ee[i] < ee_thres:
        #    idx[i] = False; continue
        # remove zonally plain depression
        if ls_xx[i] < xx_thres:
            idx[i] = False; continue
        # remove too small ones  # small one is included in Kasuga and Honda (2025)
        if ls_ro[i] == r[0]:
            idx[i] = False; continue
        # remove too large ones
        #if ls_ro[i] == r[-1]:
        #    idx[i] = False; continue

    # drop values
    ls_ty_0 = ls_ty[idx]
    ls_lev_0, ls_lat_0, ls_lon_0 = ls_lev[idx], ls_lat[idx], ls_lon[idx]
    ls_valV_0 = ls_valV[idx]
    ls_So_0, ls_ro_0, ls_Do_0 = ls_So[idx], ls_ro[idx], ls_Do[idx]
    ls_SBG_0, ls_SBGang_0 = ls_SBG[idx], ls_SBGang[idx]
    ls_m_0, ls_n_0, ls_SR_0 = ls_m[idx], ls_n[idx], ls_SR[idx]
    ls_ee_0, ls_xx_0 = ls_ee[idx], ls_xx[idx]

    ### ro-area unique local maximum test (yamane scheme)
    # descending sort along So
    idx0 = np.argsort(ls_So_0)[::-1]
    ls_ty_1 = ls_ty_0[idx0]
    ls_lev_1, ls_lat_1, ls_lon_1 = ls_lev_0[idx0], ls_lat_0[idx0], ls_lon_0[idx0]
    ls_valV_1 = ls_valV_0[idx0]
    ls_So_1, ls_ro_1, ls_Do_1 = ls_So_0[idx0], ls_ro_0[idx0], ls_Do_0[idx0]
    ls_SBG_1, ls_SBGang_1 = ls_SBG_0[idx0], ls_SBGang_0[idx0]
    ls_m_1, ls_n_1, ls_SR_1 = ls_m_0[idx0], ls_n_0[idx0], ls_SR_0[idx0]
    ls_ee_1, ls_xx_1 = ls_ee_0[idx0], ls_xx_0[idx0]

    # main loop of yamane scheme to remove extremely near pair
    idx1 = np.full((len(ls_lon_1)), True)
    for i in range(len(ls_lon_1)):
        if not idx1[i]: continue
        for j in range(i+1, len(ls_lon_1)):
            if ls_ty_1[i] != ls_ty_1[j]: continue
            dist = great_circle_distance_numba(
                    ls_lon_1[i], ls_lat_1[i],
                    ls_lon_1[j], ls_lat_1[j])
            if dist < ls_ro_1[i] and dist < ls_ro_1[j]:
                if ls_So_1[j] <= ls_So_1[i]:
                    idx1[j] = False  # not area local maximum
                    idx1[i] = True  # rescure the other

    # drop values and
    # all in one dictionary for DataFrame as point data
    return (ls_ty_1[idx1], ls_lev_1[idx1], ls_lat_1[idx1], ls_lon_1[idx1],
            ls_valV_1[idx1], ls_So_1[idx1], ls_ro_1[idx1], ls_Do_1[idx1],
            ls_SBG_1[idx1], ls_SBGang_1[idx1], ls_m_1[idx1], ls_n_1[idx1],
            ls_SR_1[idx1], ls_ee_1[idx1], ls_xx_1[idx1])


@njit
def _input_ex_numba(zloop, daSkp, lonSkp, latSkp, rr,
                    dai, loni, lati, ty, lev,
                    lsV_ty, lsV_lon, lsV_lat, lsV_ro):
    zloop2 = 'loop' in zloop

    if ty == 'L' or ty == 'both':
        lmp_l = search_localextrema(daSkp, 'minimum', zloop=zloop2)
        ls_y_l, ls_x_l = np.nonzero(lmp_l)
    if ty == 'H' or ty == 'both':
        lmp_h = search_localextrema(daSkp, 'maximum', zloop=zloop2)
        ls_y_h, ls_x_h = np.nonzero(lmp_h)
    # make point data
    if ty == "L":
        ls_y, ls_x = ls_y_l, ls_x_l
    elif ty == "H":
        ls_y, ls_x = ls_y_h, ls_x_h
    else:
        ls_y = np.hstack((ls_y_l,ls_y_h))
        ls_x = np.hstack((ls_x_l,ls_x_h))

    # check input extrema
    #import matplotlib.pyplot as plt
    #ax = plt.axes()
    #_s = ax.contourf(lonskp,latskp,daskp)
    #plt.colorbar(_s)

    #_ls_lat, _ls_lon = latskp[ls_y_l], lonskp[ls_x_l]
    #ax.scatter(_ls_lon,_ls_lat,color="b")
    #_ls_lat, _ls_lon = latskp[ls_y_h], lonskp[ls_x_h]
    #ax.scatter(_ls_lon,_ls_lat,color="r")

    #plt.savefig("hoge3.png")
    #plt.close()
    #exit()

    if ty == "L":
        ls_ty = np.full(ls_x.shape, 0)
        ls_val = daSkp.flatten()[np.where(lmp_l.flatten())]
    elif ty == "H":
        ls_ty = np.full(ls_x.shape, 1)
        ls_val = daSkp.flatten()[np.where(lmp_h.flatten())]
    else:
        ls_ty_l = np.full(ls_x_l.shape, 0)
        ls_ty_h = np.full(ls_x_h.shape, 1)
        ls_ty = np.hstack((ls_ty_l,ls_ty_h))
        ls_val_l = daSkp.flatten()[np.where(lmp_l.flatten())]
        ls_val_h = daSkp.flatten()[np.where(lmp_h.flatten())]
        ls_val = np.hstack((ls_val_l,ls_val_h))
    ls_lat, ls_lon = latSkp[ls_y], lonSkp[ls_x]

    _shape = ls_lon.shape
    il = len(ls_lon)
    ls_lev = np.full(_shape, lev)
    lsV_ex = np.zeros_like(lsV_ty)
    lsV_valX = np.zeros_like(lsV_ty)
    lsV_lonX = np.full(lsV_ty.shape, 999.9)
    lsV_latX = np.full(lsV_ty.shape, 999.9)
    ilV = len(lsV_ty)

    x_list = np.full(_shape, False)
    for i in range(ilV):
        dist_min = 100000.

        min_j = -1
        for j in range(il):

            if lsV_ty[i] != ls_ty[j]: continue
            if lsV_lat[i] * ls_lat[j] < 0.:  continue

            dist = great_circle_distance_numba(
                    lsV_lon[i], lsV_lat[i],
                    ls_lon[j], ls_lat[j])

            if dist < lsV_ro[i]*0.63:  # =DR_c
                lsV_ex[i] = 1
                lsV_valX[i] = ls_val[j]
                lsV_lonX[i] = ls_lon[j]
                lsV_latX[i] = ls_lat[j]
                if dist < dist_min:
                    dist_min = dist
                    min_j = j

        if not min_j == -1:
            x_list[min_j] = True

    return (ls_ty[x_list], ls_lev[x_list], ls_lat[x_list], ls_lon[x_list],
            ls_val[x_list], lsV_ex, lsV_valX, lsV_lonX, lsV_latX)
