# Prepare metadata file in format required by the bash script that downloads data
# The csv file can be obtained https://wcc.sc.egov.usda.gov/nwcc/yearcount?network=snow&counttype=listwithdiscontinued&state=

import numpy as np
import pandas as pd
import os
import sys
import pdb


#Metadata for snow surveys (in)
meta_file_in         = 'allStations_meta.csv'
meta_file_path    = os.path.join('../meta/tables',meta_file_in)

meta_all  =  pd.read_csv(meta_file_path)
meta_all = meta_all.convert_dtypes()


# Create station_ID
id_ok = [tt.split('(')[-1].split(')')[0] for tt in meta_all.site_name] 
meta_all['station_id'] = id_ok

meta_out = meta_all[['station_id','ntwk','wyear','state','site_name','start','enddate','latitude','longitude','elev','county','huc']]

#Metadata for snow surveys (out)
meta_file_out         = 'allStations_metadata.txt'
meta_file_path    = os.path.join('../meta/',meta_file_out)

meta_out.to_csv( meta_file_path,sep='|',header=False,index=False)

