#!/bin/bash

# define base directory
dirBase=$HOME/analysis/snowcourse

# define metadata directory
dirMeta=${dirBase}/meta

# define data directory
dirData=${dirBase}/data
mkdir -p $dirData

# define metadata file
fileMeta=${dirMeta}/snowcourse_metadata.txt

# define website
website=https://wcc.sc.egov.usda.gov/reportGenerator/view_csv/customGroupByMonthReport/monthly/
suffix='SNOW|id=""|name/POR_BEGIN,POR_END:1,2,3,4,5,6/WTEQ::collectionDate,SNWD::value,WTEQ::value'

# loop through the lines in the file
while IFS= read -r station; do

 # get state and id
 state=`echo "${station}" | cut -d "|" -f 8`
 id=`echo "${station}" | cut -d "|" -f 2`

 # define outoput file
 outfile=${dirData}/${state}_${id// /}.txt
 echo $outfile

 # build website
 webString="${website}${id// /}:${state}:${suffix}"

 # download data
 wget "${webString}" -a ${dirData}/log.txt -O $outfile

done < "$fileMeta"
