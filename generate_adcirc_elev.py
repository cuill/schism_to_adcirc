'''
Usage: python generate_adcirc_elev.py YYYY-MM-DD
'''

import sys
from datetime import datetime, timedelta
from time import time 
import argparse

import numpy as np
import numpy.ma as ma
from netCDF4 import MFDataset, Dataset

if __name__ == '__main__':

    t0=time()

    argparser = argparse.ArgumentParser()
    argparser.add_argument('date', type=datetime.fromisoformat, help='input file date')
    args=argparser.parse_args()
    date=args.date
    startdate=date-timedelta(days=1)

    fpath = "/sciclone/schism10/hyu05/NOAA_NWM/oper_3D/fcst"
    fpath2="/sciclone/pscr/lcui01/ICOGS3D_dev/outputs_adcirc"
    #ds=MFDataset(f"{fpath}/{date.strftime('%Y%m%d')}/schout_*.nc")
    ds=Dataset(f"{fpath}/{date.strftime('%Y%m%d')}/schout_{date.strftime('%Y%m%d')}.nc")

    #get coordinates/bathymetry
    x=ds['SCHISM_hgrid_node_x'][:]
    y=ds['SCHISM_hgrid_node_y'][:]
    depth=ds['depth'][:]
    NP=depth.shape[0]

    #get elements and split quads into tris
    elements=ds['SCHISM_hgrid_face_nodes'][:,:]
    tris = []
    for ele in elements:
        ele=ele[~ele.mask]
        if len(ele) == 3:
            tris.append([ele[0], ele[1], ele[2]])
        elif len(ele) == 4:
            tris.append([ele[0], ele[1], ele[3]])
            tris.append([ele[1], ele[2], ele[3]])
    NE=len(tris)
    NV=3
    
    #get times
    times=ds['time'][:]
    #print(times)
    ntimes=len(times)

    #get elev 
    elev=ds['elev'][:,:]
    #mask dry node
    maxelev=np.max(elev,axis=0)
    idry=np.zeros(NP)
    idxs=np.where(maxelev+depth <= 1e-6)
    #print(idxs)
    elev[:,idxs]=-99999.0

    ds.close()

    with Dataset(f"{fpath2}/schout_elev_{date.strftime('%Y%m%d')}.nc", "w", format="NETCDF4") as fout:
        #dimensions
        fout.createDimension('time', None)
        fout.createDimension('node', NP)
        fout.createDimension('nele', NE)
        fout.createDimension('nvertex', NV)

        #variables
        fout.createVariable('time', 'f8', ('time',))
        fout['time'].long_name="Time"
        fout['time'].units = f'seconds since {startdate.year}-{startdate.month}-{startdate.day} 00:00:00 UTC'
        fout['time'].base_date=f'{startdate.year}-{startdate.month}-{startdate.day} 00:00:00 UTC'
        fout['time'].standard_name="time"
        fout['time'][:] = times

        fout.createVariable('x', 'f8', ('node',))
        fout['x'].long_name="node x-coordinate"
        fout['x'].standard_name="longitude"
        fout['x'].units="degrees_east"
        fout['x'].positive="east"
        fout['x'][:]=x

        fout.createVariable('y', 'f8', ('node',))
        fout['y'].long_name="node y-coordinate"
        fout['y'].standard_name="latitude"
        fout['y'].units="degrees_north"
        fout['y'].positive="north"
        fout['y'][:]=y

        fout.createVariable('element', 'i', ('nele','nvertex',))
        fout['element'].long_name="element"
        fout['element'].standard_name="face_node_connectivity"
        fout['element'].start_index=1
        fout['element'].units="nondimensional"
        fout['element'][:]=np.array(tris)

        fout.createVariable('depth', 'f8', ('node',))
        fout['depth'].long_name="distance below NAVD88"
        fout['depth'].standard_name="depth below NAVD88"
        fout['depth'].coordinates="time y x"
        fout['depth'].location="node"
        fout['depth'].mesh="adcirc_mesh"
        fout['depth'].units="m"
        fout['depth'][:]=depth

        fout.createVariable('zeta','f8', ('time', 'node',), fill_value=-99999.)
        fout['zeta'].standard_name="sea_surface_height_above_navd88"
        fout['zeta'].coordinates="time y x"
        fout['zeta'].location="node"
        fout['zeta'].mesh="adcirc_mesh"
        fout['zeta'].units="m"
        fout['zeta'][:,:]=elev

        fout.title = 'SCHISM Model output'
        fout.source = 'SCHISM model output version v10'
        fout.references = 'http://ccrm.vims.edu/schismweb/'

    print(f'It took {time()-t0} to interpolate')
