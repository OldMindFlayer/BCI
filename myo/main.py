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


def main():
    config = config_init(sys.argv)
    
    # Debug mode uses LSL_Generator for debuging
    if config['general'].getboolean('debug_mode'):
        print('Debug Mode!!!')
        sys.path.append(config['paths']['lsl_stream_generator_path'])
        sys.path.append(config['paths']['lsl_stream_generator_path'] + '/pynfb')
        from generators import run_eeg_sim
        freq = config['general'].getint('fs_amp')
        name = config['general']['lsl_stream_name_amp']
        labels = ['channel{}'.format(i) for i in range(config['general'].getint('n_channels_amp'))]
        lsl_stream_debug = lambda: run_eeg_sim(freq, name=name, labels=labels)
        lsl_stream_debug_tread = Thread(target=lsl_stream_debug, args=())
        lsl_stream_debug_tread.daemon = True
        lsl_stream_debug_tread.start()
        print("generators.run_eeg_sim start DEBUG LSL \"{}\"".format(config['general']['lsl_stream_name_amp']))
    
    pn2lsl = PN2LSL(TCP_IP='127.0.0.1', TCP_PORT = 7010, BUFFER_SIZE = 1800, debug=False)
    pn2lsl.start()
    time.sleep(2)

    #while True:
    #    time.sleep(3)

    exp = Experiment(config)
    exp.record_data(config['general'].getint('experiment_time_record'))
    inlet_amp = exp.get_inlet_amp()
    inlet_pn = exp.get_inlet_pn()
    
    decoder = Decode(config, inlet_amp, inlet_pn)
    decoder.decode()
 
    
    Pn=np.array([c[1] for c in decoder.get_coordbuff()])
    Dec=np.array([c[0] for c in decoder.get_coordbuff()])

    for i in range(Pn.shape[1]):
        plt.plot(Pn[1000:,i]+100*i)
        plt.plot(Dec[1000:,i]+100*i)
    plt.show()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
if __name__ == '__main__':
    main()    
    
    