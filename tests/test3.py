# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 18:07:05 2020

@author: AlexVosk
"""

import numpy as np

a = np.zeros((4))
b = np.ones(shape=(2,4))
c = np.zeros(shape=(2,4))*np.nan
d = np.asarray([1, 0, np.nan, np.nan, 1, 0, 1, np.nan]).reshape(2,4)




medians = np.nanmedian(d, axis=0)
print(medians)

a[~np.isnan(medians)] = medians[~np.isnan(medians)]
print(a)

#func = lambda array: 
#np.apply_along_axis