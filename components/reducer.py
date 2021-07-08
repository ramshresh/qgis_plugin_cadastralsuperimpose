
# Python code to demonstrate
# return the sum of values of dictionary
# with same keys in list of dictionary
  
import collections, functools, operator
  
# Initialising list of dictionary
ini_dict = [{'a':5, 'b':10, 'c':90},
            {'a':45, 'b':78}, 
            {'a':90, 'c':10}]
  
def group_key_val(ini_dict, method='add'):
    if method =='add':        
        # sum the values with same keys
        result = dict(functools.reduce(operator.add,
                 map(collections.Counter, ini_dict)))
        print("resultant dictionary : ", str(result))
        return result

group_key_val(ini_dict)
      

