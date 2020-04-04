# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 11:45:44 2020

@author: AlexVosk
"""

import numpy as np


chunk_pn_to_stack = np.zeros((2, 4)) * np.nan
chunk_amp = np.ones((2, 4))
chunk_pn = np.ones((2, 4))
for i in range(chunk_pn.shape[0]):
    chunk_pn[i,:] = chunk_pn[i,:] * i
print(chunk_pn)
timestamp_amp = np.array([2,1])
timestamp_pn = np.array([0.5, 0.6])
timestamp_pn = timestamp_pn - timestamp_pn[0] + timestamp_amp[0]
print(timestamp_pn)
chunk_pn_to_stack[np.searchsorted(timestamp_amp[:-1], timestamp_pn), :] = chunk_pn
print(np.searchsorted(timestamp_amp[:-1], timestamp_pn))
print(chunk_pn_to_stack)



