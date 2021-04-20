# Processing scripts for USA snowcourse data

## Obtain metadata for all snow courses

This is a manual process. Download the table from the following website:
https://wcc.sc.egov.usda.gov/nwcc/yearcount?network=snow&counttype=listwithdiscontinued&state=

Save the metadata as `allStations_metadata.html`

NOTE: This step could be automated using `wget`; however, this gets complicated because the data are stored in tables.

## Process the metadata

Run the script `./allStationsMeta.bash > ../meta/allStations_metadata.txt`
to create the metadata file delimited by "|"

## Download the data

Run the script `./downloadFilez.bash` to download the data

## Convert the data in netcdf

Run the script `./US_SC_to_netcdf.py` to convert the data into Netcdf. The format of the netcdf is the same as for CanSWE, the historical Canadian SWE dataset. 

The script is made of 5 stages: (i) loop over the individual datafiles to combine them into a single xarray dataset, (ii) add the relevant metadata for each measueement site, (iii) apply simple QC based on range thresholding and (iv) add the attributes of each data and metadata and (v) generate the final netcdf. 

The script includes a check on the measurement date to make sure that it corresponds approximatively (+/- 15 days) to the nominal date (beginning od each month). If it not the case, the nominal date is used as the measurement data and a flag is added. 

Requires the following python package: xarray, pandas, numpy
