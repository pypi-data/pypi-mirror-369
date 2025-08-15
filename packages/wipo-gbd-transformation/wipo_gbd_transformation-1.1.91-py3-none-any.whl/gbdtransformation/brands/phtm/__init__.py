# instruction to render the output to JSON format
render = 'JSON'
source = 'national'

# PH/4/1981/00000115
# PH/M/0001/01573483 
# A/M/0001/01421820 B/M/0001/01364251 

# PH4198100000115
# PHM000101573483 
# AM000101421820 BM000101364251 
# PH/4199800004477
appnum_mask = [ 'PH\\/?\\d\\d{4}(\\d*)', 'PHM\\d{4}(\\d*)', 'AM\\d{4}(\\d*)', 'BM\\d{4}(\\d*)' ]
regnum_mask = [ 'PH\\/?\\d\\d{4}(\\d*)', 'PHM\\d{4}(\\d*)', 'AM\\d{4}(\\d*)', 'BM\\d{4}(\\d*)' ]
