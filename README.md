# Processing scripts for USA snowcourse data

## Obtain metadata for the snowcourses in each state, province or territory.

This is a manual process. Download the tables from the following websites:
https://wcc.sc.egov.usda.gov/nwcc/rgrpt?report=snowcourse&state=AB\
https://wcc.sc.egov.usda.gov/nwcc/rgrpt?report=snowcourse&state=AK\
https://wcc.sc.egov.usda.gov/nwcc/rgrpt?report=snowcourse&state=AZ\
https://wcc.sc.egov.usda.gov/nwcc/rgrpt?report=snowcourse&state=BC\
https://wcc.sc.egov.usda.gov/nwcc/rgrpt?report=snowcourse&state=CA\
https://wcc.sc.egov.usda.gov/nwcc/rgrpt?report=snowcourse&state=CO\
https://wcc.sc.egov.usda.gov/nwcc/rgrpt?report=snowcourse&state=ID\
https://wcc.sc.egov.usda.gov/nwcc/rgrpt?report=snowcourse&state=MT\
https://wcc.sc.egov.usda.gov/nwcc/rgrpt?report=snowcourse&state=NM\
https://wcc.sc.egov.usda.gov/nwcc/rgrpt?report=snowcourse&state=NV\
https://wcc.sc.egov.usda.gov/nwcc/rgrpt?report=snowcourse&state=OR\
https://wcc.sc.egov.usda.gov/nwcc/rgrpt?report=snowcourse&state=UT\
https://wcc.sc.egov.usda.gov/nwcc/rgrpt?report=snowcourse&state=WA\
https://wcc.sc.egov.usda.gov/nwcc/rgrpt?report=snowcourse&state=WY\
https://wcc.sc.egov.usda.gov/nwcc/rgrpt?report=snowcourse&state=YK\

The tables of metadata are saved in a file `XX_meta.html`
where `XX` is the 2-character abbreviation for the state, province or territory.

NOTE: This step could be automated using `wget`; however, this gets complicated because the data are stored in tables.

## Process the metadata

Run the script `./processMeta.bash > snowcourse_metadata.txt`
to create a tab-delimited file

## Download the data

Run the script `./downloadFilez.bash` to download the data
