import time, datetime
from inspect import currentframe, getframeinfo

import os

def get_file(currentframe):
    frameinfo =getframeinfo(currentframe)
    return os.path.basename(frameinfo.filename)
def get_lineno(currentframe):
    frameinfo =getframeinfo(currentframe)
    return frameinfo.lineno
def get_line(currentframe):
    return "[Line {} ]: {}".format(get_lineno(currentframe), get_file(currentframe))
    

def logger(message=''):
    ts = time.time()
    sttime = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H:%M:%S - ')

    with open(r"C:\Users\Ram_DFID\Desktop\cadastralsuperimpose_logs.txt", 'a') as logfile:
        logfile.write(sttime + ' : ' + message + '\n')


# Python code to demonstrate
# return the sum of values of dictionary
# with same keys in list of dictionary
  
import collections, functools, operator
    
def group_key_val(ini_dict, method='add'):
    if method =='add':        
        # sum the values with same keys
        result = dict(functools.reduce(operator.add,
                 map(collections.Counter, ini_dict)))
        result_dec2 = {key : round(result[key], 2) for key in result}
        return result_dec2


        
