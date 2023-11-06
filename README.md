# Processing scripts for USA snowcourse data

## Obtain metadata for all snow courses

This is a manual process. Download the table from the following website:
https://wcc.sc.egov.usda.gov/nwcc/yearcount?network=snow&counttype=listwithdiscontinued&state=

Save the metadata as `allStations_metadata.html` (Stream 1) or save the data in csv format (Stream 2)

NOTE: This step could be automated using `wget`; however, this gets complicated because the data are stored in tables.

## Process the metadata

(Stream 1) : Run the script `./allStationsMeta.bash > ../meta/allStations_metadata.txt` to create the metadata file delimited by "|"

(Stream 2) : Run the Python code script `prepare_meta.py` to create the metadata file delimited by "|"

## Download the data

Run the script `./downloadFilez.bash` to download the data

## Convert the data in NetCDF

Run the script `./US_SC_to_netcdf.py` to convert the data into NetCDF. The format of the NetCDF is the same as for CanSWE, the historical Canadian SWE dataset (Vionnet et al., 2021) 

The script is made of 5 stages: (i) loop over the individual datafiles to combine them into a single xarray dataset, (ii) add the relevant metadata for each measurement site, (iii) apply a simple QC based on range thresholding and (iv) add the attributes of each data and metadata and (v) generate the final netcdf. 

The script includes a check on the measurement date to make sure that it corresponds approximatively (+/- 15 days) to the nominal date (beginning of each month). If it is not the case, the nominal date is used as the measurement date and a flag is added ('U') (see the attributes of the NetCDF). When such date inconsistency occurs, the reported SWE value corresponds to an estimated value (NCRS, personal communication, 2021). We recommend to remove set this value to NaN when using this dataset for model evaluation. 

The NetCDF file contains a variable that describes the type of SWE measurements. A value of 7 is used for 'Aerial markers'. This is specific to this US dataset. Note that stations originally identified as aerial markers may correspond to snow courses for the more recent years since these remote sites can be more easily acessed using modern helicopters. However, it is not possible to make a clear distinction (NCRS, personal communication, 2021). This is one of the limitation of this dataset. 
  

Requires the following python package: xarray, pandas, numpy

## References 
Vionnet, V., Mortimer, C., Brady, M., Arnal, L. and Brown, R.: Canadian historical Snow Water Equivalent dataset (CanSWE, 1928-2020), submitted to Earth System Science Data, May 2021 

