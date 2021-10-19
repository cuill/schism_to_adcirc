'''
Usage: python generate_station_timeseries.py YYYY-MM-DD
'''

from datetime import datetime, timedelta
from time import time
import argparse

import numpy as np
import pandas as pd
from netCDF4 import Dataset, stringtochar

argparser = argparse.ArgumentParser()
argparser.add_argument('date', type=datetime.fromisoformat, help='input file date')
args=argparser.parse_args()
date=args.date

df=pd.read_csv("stations_noaa-coops_164.csv", index_col=[0])
#name=df['Name']
sid=df['ID']
lon=df['lon']
lat=df['lat']
nstation=len(sid)
namelen=50

#read model output
fpath = "/sciclone/schism10/hyu05/NOAA_NWM/oper_3D/fcst"
fpath2="/sciclone/pscr/lcui01/ICOGS3D_dev/outputs_adcirc"
data=np.loadtxt(f"{fpath}/{date.strftime('%Y%m%d')}/staout_1")
time=data[:,0]
nt=len(time)
#print(nt)
#print(nstation)
model=np.ndarray(shape=(nt,nstation), dtype=float)
model[:,:]=data[:,1:]

startdate=date-timedelta(days=1)
times=np.empty((nt),'f')
times[:]=[(i+1)*30*60 for i in range(nt)]

#write to netcdf file
with Dataset(f"{fpath2}/schout_elev_timeseries_at_obs_locations_{date.strftime('%Y%m%d')}.nc", "w", format="NETCDF4") as fout:
    #dimensions
    fout.createDimension('station', nstation)
    fout.createDimension('namelen', namelen)
    fout.createDimension('time', None)

    #variables
    fout.createVariable('time', 'f8', ('time',))
    fout['time'].long_name="Time"
    fout['time'].units = f'seconds since {startdate.year}-{startdate.month}-{startdate.day} 00:00:00 UTC'
    fout['time'].base_date=f'{startdate.year}-{startdate.month}-{startdate.day} 00:00:00 UTC'
    fout['time'].standard_name="time"
    fout['time'][:] = times

    fout.createVariable('station_name', 'c', ('station','namelen',))
    fout['station_name'].long_name="station name"
    names=[]
    names=np.empty((nstation,), 'S'+repr(namelen))
    for i in np.arange(nstation):
        str_in=df['Name'][i]
        strlen=len(str_in)
        str_out=list(str_in)
        tmp="".join(str_out[j] for j in range(strlen))
        names[i]=str(sid[i])+" "+tmp
    namesc=stringtochar(names)
    fout['station_name'][:]=namesc

    fout.createVariable('x', 'f8', ('station',))
    fout['x'].long_name="longitude"
    fout['x'].standard_name="longitude"
    fout['x'].units="degrees_east"
    fout['x'].positive="east"
    fout['x'][:]=lon

    fout.createVariable('y', 'f8', ('station',))
    fout['y'].long_name="latitude"
    fout['y'].standard_name="latitude"
    fout['y'].units="degrees_north"
    fout['y'].positive="north"
    fout['y'][:]=lat

    fout.createVariable('zeta', 'f8', ('time', 'station',), fill_value=-99999.)
    fout['zeta'].long_name="water surface elevation above navd88"
    fout['zeta'].standard_name="sea_surface_height_above_navd88"
    fout['zeta'].units="m"
    fout['zeta'][:,:]=model

    fout.title = 'SCHISM Model output'
    fout.source = 'SCHISM model output version v10'
    fout.references = 'http://ccrm.vims.edu/schismweb/'
