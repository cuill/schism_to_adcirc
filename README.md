Convert SCHISM outputs to ADCIRC fort.63 (water level) and fort.61 (time series)

Run the below command to install needed libraries.
`pip install -r requirements.txt`

1. generate_adcirc_elev.py
    1) Modify the script to change the "fpath" to the SCHISM output directory "fpath=/your/directory/" e.g., on sciclone, fpath = "/sciclone/schism10/hyu05/NOAA_NWM/oper_3D/fcst", and each forecast has its own direcotry "fpath/20211018/"
    2) Modify the script to change "fpath2" to save results, e.g., fpath2="/sciclone/pscr/lcui01/ICOGS3D_dev/outputs_adcirc"
    3) Run this command `python generate_adcirc_elev.py 2021-10-18`

2. generate_station_timeseries.py
   Same as above, change the paths of "fpath" and "fpath2"
   Run `python generate_station_timeseries.py 2021-10-18`
