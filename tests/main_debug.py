import sys
from pn2lsl import PN2LSL
#from lsl_stream_generator import LSL_Generator
import time
import importlib
from pylsl import resolve_streams
from threading import Thread
from experiment import Experiment
from config import config_init
from pathlib import Path
from stream_decode_v2 import Decode
import numpy as np
from matplotlib import pyplot as plt
import h5py


def main():

    print('Debug Mode!!!')
    sys.path.append('C:/MyoDecodeProject/nfb/')
    sys.path.append('C:/MyoDecodeProject/nfb/pynfb/')
    from generators import run_eeg_sim
    freq = 500
    name = 'NVX136_Data'
    labels = ['channel{}'.format(i) for i in range(64)]
    lsl_stream_debug = lambda: run_eeg_sim(freq, name=name, labels=labels)
    lsl_stream_debug_tread = Thread(target=lsl_stream_debug, args=())
    lsl_stream_debug_tread.daemon = True
    lsl_stream_debug_tread.start()
    print("generators.run_eeg_sim start DEBUG LSL \"{}\"".format(name))
    while True:
        time.sleep(3)
    
    
if __name__ == '__main__':
    main()    
    
    