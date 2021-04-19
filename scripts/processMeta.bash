#!/bin/bash

# define base directory
dirBase=$HOME/analysis/snowcourse

# define metadata directory
dirMeta=${dirBase}/meta

# make a temporary directory
mkdir -p ${dirMeta}/temp

# loop through files
for file in ${dirMeta}/tables/*.html; do

 # get the state
 fname=$(basename $file)
 state=${fname%%_*}
 #echo Processing metadata for $state

 # define metadata files
 temp=${dirMeta}/temp/${state}_temp.txt
 meta=${dirMeta}/temp/${state}_meta.txt

 # extract the metadata
 # NOTE: include a space after state to avoid the state in the file name
 # NOTE: includes 3 lines after the state code (more than what is needed)
 # NOTE: the second grep call includes the case where the state is at the end of the line
 grep -B1 -A3 "${state} " $file | grep -v Current >  $temp
 grep -B1 -A3 "${state}$" $file | grep -v Current >> $temp

 # ensure a separate line for each station
 # 1st command (tr '\n' '\t') gets rid of new lines
 # 2nd command (gsed 's/--/\n/g') replaces station delimiter with a new line
 # 3rd command (grep "SNOW") restricts attention to snow courses
 # 4th command (gsed 's/\t/|/g') replace tabs with the "|" delimiter 
 # NOTE: use gsed instead of sed
 tr '\n' '\t' < $temp | gsed 's/--/\n/g' | grep "SNOW" | gsed 's/\t/|/g' > $meta
 
 # loop through the lines in the file
 while IFS= read -r line; do

  echo $line

  # strip out the extraneous information
  chek=`echo "${line}" | cut -d ">" -f 1`
  echo "$chek" | grep -q "SNOW" && trim="$line" || trim=`echo "$line" | cut -d ">" -f 2`
  trim=`echo "${trim%<*}" | gsed 's/^[|][|][|]*//g' | gsed 's/^[|]*//g'` # remove delimiters at the start

  # restrict attention to desired columns
  station=`echo "${trim}" | cut -d "|" -f1-8`
  echo $station
  
 done < "$meta"

done
