import numpy as np
import pandas as pd
import xarray as xr
import os
import sys
import pdb
import datetime
import glob


DEFAULT_ENCODING = {
    'zlib': True,
    'shuffle': True,
    'complevel': 4,
    'fletcher32': False,
    'contiguous': False,
  }


def generate_encodings(data):
    n_stations = len(data['station_id'])
    encoding = {}
    for var in data.data_vars:
        encoding[var] = DEFAULT_ENCODING.copy()
        # copy existing encoding vars from input data
        encoding[var].update({
            k:v for (k,v) in data[var].encoding.items()
            if k in ['_FillValue', 'dtype']
        })
        # special cases
        if var in ['source','station_name','station_id_sec','station_id_ter','station_name_sec','station_name_ter']:
            encoding[var]['dtype'] = str
        elif var in ['snw', 'snd', 'den']:
            encoding[var].update({
                '_FillValue': 9.96921e+36,
                'dtype': 'float32'
            })
        elif var in ['data_flag_snd','data_flag_snw','qc_flag_snw','qc_flag_snd']:
            encoding[var]['dtype'] = 'S1'
    return encoding

# Data network
network = 'US_NRCS'

# Location to download historical station data
download_dir = '../data'

# Netcdf file to save to
netcdf_dir   = '../data_final'
# Make if does not exist
if not os.path.exists(netcdf_dir):
    os.makedirs(netcdf_dir)
netcdf_file_out =  os.path.join(netcdf_dir,network+'_survey.nc')

# Go to download dir
os.chdir(download_dir)

# Get list of files
c_files = glob.glob('*_*.txt')

# Detect stations that are in AB, YK and BC and remove them to avoid overlap with CanSWE
mask_can = np.array([tt[0:2] in ['AB','BC','YK'] for tt in c_files])
files_us = np.array(c_files)
files_us = files_us[~mask_can].tolist() # List of the stations in the US

dic_index ={'snw':2,'snd':1,'time':0}
list_var= ['time','snw','snd']
list_var_snow= ['snw','snd']

# Flag to check duplicates in the dates
lcheck_dupli=True

lskip=[]
da_temp=[]

for cf in files_us:
   
   print(cf)
   sta_id = cf.split('.')[0]

   count = len(open(cf).readlines(  ))
   # Load into a dataframe
   if(count>60): # make sure that the ascii file contains snow data (at least one year)
      df = pd.read_csv(cf, skiprows=60, engine='python')
   else:
      lskip.append(sta_id)  
      continue 

   # Remove the first line
   df = df.iloc[1:]

   # Get number of columns
   ncol = len(df.columns)
    
   # Get the index that corresspond to date
   ind_date=np.arange(1,ncol,3)

   for ivar,var in enumerate(list_var):
     # Get the index that corressponds to the variable
     ind_var = ind_date+dic_index[var]

     # Extract var
     df_var = df.iloc[:,ind_var]
     df_var = df_var.join(df['Water Year'])

     # Get a single column dataframe
     df_var = df_var.melt(id_vars=['Water Year'])

     # Change column name
     df_var = df_var.rename(columns={'value':var})

     if(ivar==0):
        df_all = df_var
     else:
        df_all = df_all.join(df_var[var])

   # Remove non defined dates 
   df_all = df_all[ ~pd.isnull(df_all.time)]

   # Create index correspondingt to date
   df_all['time'] = df_all.time+" "+df_all['Water Year'].astype(int).astype(str)
   df_all['time'] = pd.DatetimeIndex(df_all.time)

   # Adjust year to account for the fact that teh first measurement of the year can be collected in late December
   mask_month=[t.month>11 for t in df_all.time]
   if(np.sum(mask_month)>0):
      df_all['time'].values[mask_month] = df_all['time'][mask_month] - pd.DateOffset(years=1)

   # Define time as the new index of the dataframe. 
   df_all.index = df_all.time

   # Convert SWE and SD to the correct SI units
   df_all['snd'] =  df_all['snd'].astype(float)*0.0254 # Convert SD from inches to m 
   df_all['snw'] =  df_all['snw'].astype(float)*25.4 # Convert SWE from inches to kg/m2 (mm)

   # Add nominal date corresponding to each measurement
   df_all['time_ref'] = df_all.variable+" 01 "+df_all['Water Year'].astype(int).astype(str)
   df_all['time_ref'] = pd.DatetimeIndex(df_all.time_ref)

   # Define mask to find all the measurement datse (time) that are more than 15 days from the corresponding nominal measurement dates (time_ref)
   mask_time = np.abs(df_all.time-df_all.time_ref)>np.timedelta64(15,'D')

   # Create an alternative time variable that correspond to 
   #      - the measurement date if this date is in agreement with the nominal date
   #      - the nominal date if the measurement date is too different from the noimnal data
   df_all['time_bis'] = df_all['time']
   df_all['time_bis'].values[mask_time] =  df_all['time_ref'][mask_time].values 

   # Create qc_flag to keep track of the change
   mask_swe_OK = ~df_all.snw.isnull()
   df_all['data_flag_snw'] = b''
   df_all['data_flag_snw'].values[mask_time & mask_swe_OK] = b'U'

   mask_sd_OK = ~df_all.snd.isnull()
   df_all['data_flag_snd'] = b''
   df_all['data_flag_snd'].values[mask_time & mask_sd_OK] = b'U'

   # Change the time index to use time_bis as the new time reference:
   df_all.index = df_all.time_bis

   # Remove unnecessary variables
   df_all = df_all.drop(['time','variable','Water Year','time_ref','time_bis'],axis=1)

   #Sort time index
   df_all = df_all.sort_index()

   # Rename time_bis into time
   df_all.index = df_all.index.rename('time')

   if(lcheck_dupli):
     lt = df_all.index.unique()
     if(len(lt) < len(df_all.index)):
         print('Pb time dim',sta_id)
         lsta.append(sta_id)  
         perc.append((2.*(len(df_all.index)-len(lt))/len(df_all.index))*100.)
         for ii in np.arange(0,(len(df_all.index)-2),1):
             if(df_all.index[ii] == df_all.index[ii+1]):
                 sta_over.append(df_all.index[ii])
                 print('Pb', df_all.index[ii])

   # Create xarray
   da = df_all.to_xarray()

   # Add station id
   da.coords['station_id'] = sta_id

   da_temp.append(da)


# Combine all the stations into one xarray
da_fin = xr.concat(da_temp, dim='station_id')

# Adjust the flags
for var in ['data_flag_snw','data_flag_snd']:
   mm = pd.isnull(da_fin[var].values)
   da_fin[var].values[mm] =b''

#Metadata for snow surveys
meta_file         = 'allStations_metadata.txt'
meta_file_path    = os.path.join('../meta',meta_file)
meta_all  =  pd.read_csv(meta_file_path, sep='|', engine='python',usecols=[0,3,4,7,8,9],names=['id','type','year','state','station_name','date_beg','date_end','lat','lon','elevation','region','watershed','wat2'])
meta_all = meta_all.convert_dtypes()

# Create station_id and remove space in string
meta_all['station_id'] = meta_all['state'].str.strip()+'_'+meta_all['id'].str.strip()
meta_all['station_id'] = meta_all['station_id'].str.strip()

# Restrict metadata to stations containing data
sta_id = da_fin.station_id.values.tolist()
meta_sel =   meta_all[meta_all.station_id.isin(sta_id)]

# Create lat, lon, elevation (including conversion into m)
da_fin['lat'] = xr.DataArray(meta_sel['lat'].astype(float),coords={'station_id':meta_sel.station_id}, dims='station_id')
da_fin['lon'] = xr.DataArray(meta_sel['lon'].astype(float),coords={'station_id':meta_sel.station_id}, dims='station_id')
da_fin['elevation'] = xr.DataArray(meta_sel['elevation'].astype(float)*0.3048,coords={'station_id':meta_sel.station_id}, dims='station_id')

# Create station name
name_ok = [tt.split('(')[0].upper().strip() for tt in meta_sel.station_name]  # Extract info from the station name
meta_sel['station_name']=name_ok
da_fin['station_name'] = xr.DataArray(meta_sel['station_name'],coords={'station_id':meta_sel.station_id}, dims='station_id')

# Add data source
source_ok=['US Natural Resources Convervation Service' for tt in da_fin.station_id ]
da_fin['source'] = xr.DataArray(source_ok,dims='station_id')

# Add measurement type and detect potential Aerial markers
type_ok = []
for sta in sta_id:
    ext = meta_sel.loc[meta_sel.station_id==sta]

    tt = ext.station_name.values[0]
    if('AERIAL' in tt or ' AM' in tt): 
       type_ok.append(7) # Use special value for aerial markers
    else:
       type_ok.append(0) # Default is multi point manual measurement

da_fin['type_mes'] = xr.DataArray(type_ok,dims='station_id')

# Adapt station_id
sta_ok = ['NRCS_'+tt for tt in da_fin.station_id.values]
da_fin['station_id'] = sta_ok

# Move to coords
da_fin=da_fin.set_coords(['station_id','time'])

# Add snow density (in kg/m3)
da_fin['den'] = da_fin['snw'] / da_fin['snd']


# Simple QC

# Create the QC flags
yy=np.chararray((len(da_fin.station_id),len(da_fin.time)))
yy[:]=b''
da_fin['qc_flag_snw'] = xr.DataArray(yy,coords={'station_id':da_fin.station_id,'time':da_fin.time},dims=('station_id','time'))  # Add the correct flag
da_fin['qc_flag_snd'] = xr.DataArray(yy,coords={'station_id':da_fin.station_id,'time':da_fin.time},dims=('station_id','time'))  # Add the correct flag

# Remove negative SWE
mask_swe_neg = da_fin.snw.values<0.
da_fin.snw.values[mask_swe_neg] = np.nan
da_fin.qc_flag_snw.values[mask_swe_neg] = b'W' # SWE range threshold flag.

# Remove negative SD
mask_snd_neg = da_fin.snd.values<0.
da_fin.snd.values[mask_snd_neg] = np.nan
da_fin.qc_flag_snd.values[mask_snd_neg] = b'H' # SD range threshold flag.

# Remove SD=0 and SWE>0
mask_nosnd_swe = np.logical_and(da_fin.snd.values==0.,da_fin.snw.values>0.)
da_fin.snd.values[mask_nosnd_swe] = np.nan
da_fin.snw.values[mask_nosnd_swe] = np.nan
da_fin.qc_flag_snd.values[mask_nosnd_swe] = b'D' # density range threshold flag. (because it would fail density threshold)
da_fin.qc_flag_snw.values[mask_nosnd_swe] = b'D' # density range threshold flag. (because it would fail density threshold)

# Remove SD>0 and SWE=0
mask_snd_noswe = np.logical_and(da_fin.snd.values>0.,da_fin.snw.values==0.)
da_fin.snd.values[mask_snd_noswe] = np.nan
da_fin.snw.values[mask_snd_noswe] = np.nan
da_fin.qc_flag_snd.values[mask_snd_noswe] = b'D' # density range threshold flag. (because it would fail density threshold)
da_fin.qc_flag_snw.values[mask_snd_noswe] = b'D' # density range threshold flag. (because it would fail density threshold)

# Check on snow density
da_fin['den'] = xr.full_like(da_fin.snd,fill_value=np.nan)
mask_sd  = da_fin.snd.values>0.
da_fin.den.values[mask_sd] = da_fin.snw.values[mask_sd]/da_fin.snd.values[mask_sd]

# Swe threshold: 0-8000 (as in mountainous areas for CanSWE); set data qc flag to 'W'
da_fin['qc_flag_snw']=xr.where(da_fin.snw>8000,b'W',da_fin.qc_flag_snw)
da_fin['snw']=xr.where(da_fin.snw>8000,np.nan,da_fin.snw)

# Snow depth threshold: 0-8 (as in mountainous areas for CanSWE); set data qc flag to 'H'
da_fin['qc_flag_snd']=xr.where(da_fin.snd>8,b'H',da_fin.qc_flag_snd)
da_fin['snd']=xr.where(da_fin.snd>8,np.nan,da_fin.snd)

# Density threshold 25-700; set data qc flag to 'D' (note this changed form Z 24 March 2021)
mask_pb_den = np.logical_or(da_fin.den.values<25,da_fin.den.values>700)
da_fin.snd.values[mask_pb_den] = np.nan
da_fin.snw.values[mask_pb_den] = np.nan
da_fin.den.values[mask_pb_den] = np.nan
da_fin.qc_flag_snd.values[mask_pb_den] = b'D'
da_fin.qc_flag_snw.values[mask_pb_den] = b'D'

#Add attributes

# Type
da_fin.type_mes.attrs['standard_name'] = 'measurement_type'
da_fin.type_mes.attrs['long_name'] = 'Method of measurement for snow water equivalent'
da_fin.type_mes.attrs['description'] = 'WMO standard -- 0: MULTI POINT MANUAL SNOW SURVEY; 1: SINGLE POINT MANUAL SNOW WATER EQUIVALENT MEASUREMENT; 2: SNOW PILLOW OR SNOW SCALE; 3: PASSIVE GAMMA; 4: GNSS/GPS METHODS; 5: COSMIC RAY ATTENUATION; 6: TIME DOMAIN REFLECTOMETRY -- US Specific: 7: AERIAL MARKERS (ESTIMATED VALUE)'
 
# Source
da_fin.source.attrs['long_name'] = 'Data provider'
da_fin.source.attrs['standard_name'] = 'source'

# Elevation
da_fin.elevation.attrs['long_name'] = 'Station elevation' 
da_fin.elevation.attrs['standard_name'] = 'elevation' 
da_fin.elevation.attrs['units'] = 'm'

# Latitude
da_fin.lat.attrs['long_name'] = 'Station latitude' 
da_fin.lat.attrs['standard_name'] = 'latitude' 
da_fin.lat.attrs['units'] = 'degrees_north'

# Longitude
da_fin.lon.attrs['long_name'] = 'Station longitude' 
da_fin.lon.attrs['standard_name'] = 'longitude' 
da_fin.lon.attrs['units'] = 'degrees_east'

#SWE
da_fin.snw.attrs['long_name'] = 'Surface snow water equivalent'
da_fin.snw.attrs['standard_name'] = 'surface_snow_amount'
da_fin.snw.attrs['units'] = 'kg m**-2'

#SD
da_fin.snd.attrs['long_name'] = 'Surface snow depth'
da_fin.snd.attrs['standard_name'] = 'surface_snow_thickness'
da_fin.snd.attrs['units'] = 'm'
da_fin.snd.attrs['description'] = '"thickness" in the standard_name means the vertical extent of the snowpack'

#Den
da_fin.den.attrs['long_name'] = 'Bulk density of surface snow'
da_fin.den.attrs['standard_name'] = 'surface_snow_density'
da_fin.den.attrs['units'] = 'kg m**-3'
da_fin.den.attrs['description'] = 'Bulk snow density, defined as den = snw/snd'

# 
da_fin.data_flag_snw.attrs['long_name']='Agency data quality flag: snow water equivalent'
da_fin.data_flag_snw.attrs['standard_name']='data_quality_flag_agency_snw'
da_fin.data_flag_snw.attrs['description']='U: US specific - precise sampling date not available - adjusted to nominal survey date - corresponds to estimated value'

#
da_fin.data_flag_snd.attrs['long_name']='Agency data quality flag: snow depth'
da_fin.data_flag_snd.attrs['standard_name']='data_quality_flag_agency_snd'
da_fin.data_flag_snd.attrs['description']='U: US specific - precise sampling date not available - adjusted to nominal survey date - corresponds to estimated value'

#
da_fin.qc_flag_snw.attrs['long_name']='Data quality flag: snow water equivalent'
da_fin.qc_flag_snw.attrs['standard_name']='data_quality_flag_snw'
da_fin.qc_flag_snw.attrs['description']='W: snow water equivalent > 8000 kg m-2 or < 0 kg m-2; D: density failed 25 - 700 kg m-3 threshold and snow water equivalent set to nan'

#
da_fin.qc_flag_snd.attrs['long_name']='Data quality flag: snow depth'
da_fin.qc_flag_snd.attrs['standard_name']='data_quality_flag_snd'
da_fin.qc_flag_snd.attrs['description']='H: snow depth > 3 m or < 0 m; D: density failed 25 - 700 kg m-3 threshold and snow depth set to nan'

# General attributes
da_fin.attrs['Conventions'] = 'CF-1.9'
da_fin.attrs['title']       = 'NRCS snow survey dataset'
da_fin.attrs['source']      = "Manual snow surveys and aerial markers"


# Save netcdf
encoding = generate_encodings(da_fin)
da_fin.to_netcdf(netcdf_file_out,format='NETCDF4',encoding=encoding)
