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
