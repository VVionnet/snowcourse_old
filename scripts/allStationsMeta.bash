#!/bin/bash

# define base directory
dirBase=$HOME/analysis/snowcourse

# define metadata directory
dirMeta=${dirBase}/meta

# define metadata file
fileMeta=${dirMeta}/tables/allStations_meta.html

# make a temporary directory
mkdir -p ${dirMeta}/temp

# define metadata files
temp=${dirMeta}/temp/allStations_temp.txt
meta=${dirMeta}/temp/allStations_meta.txt

# extract the metadata
# NOTE: get lines starting with "SNOW"
# NOTE: include extra 3 lines in case there is a newline in the middle of the record
grep -A3 "^SNOW" $fileMeta > $temp

# ensure a separate line for each station
# 1st command (tr '\n' '\t') gets rid of new lines
# 2nd command (gsed 's/SNOW/\nSNOW/g') adds a newline before the word "SNOW"
# 3rd command (tail -n +2) removes the empty first line
# NOTE: use gsed instead of sed
tr '\n' '\t' < $temp | gsed 's/SNOW/\nSNOW/g' | tail -n +2 > $meta

# loop through the lines in the file
while IFS= read -r line; do

 # split line into cells based on the tab delimiter
 IFS=$'\t'    # define tab delimiter
 vec=($line)  # split line

 # get the station ID
 # NOTE: format is "station name (id)"
 name="${vec[3]}"    # the station name is the 3rd element of the vector
 pref="${name##*(}"  # get everything after the last "(" character
 id="${pref%%)*}"    # get everything before the last ")" character

 # concatenate metadata the vector using the "|" delimiter
 split=" | "
 regex="$( printf "${split}%s" "${vec[@]}" )"
 station="${regex:${#split}}" # remove leading separator

 # write out the station ID and the original metadata vector
 echo $id " | " $station

done < "$meta"
