# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 13:06:01 2020

@author: AlexVosk
"""


from pathlib import Path
import sys
stimulator_path = str(Path('pnhandler_test.py').resolve().parents[1]/'bci/')
sys.path.append(stimulator_path)

import time
import configparser
from pnhandler import PNHandler


# test PNHandler class and it's get_next_chunk_pn() method
def test(config):
    pnhandler = PNHandler(config)
    pnhandler.start()
    time.sleep(3)
    time_start = time.time()
    time_test = 60
    while (time.time() < time_start + time_test):
        chunk_pn, timestamp_pn = pnhandler.get_next_chunk_pn()
        if chunk_pn is not None:
            print(chunk_pn[:, [27, 53, 77, 101, 125]])


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('pnhandler_config.ini')
    
    test(config)