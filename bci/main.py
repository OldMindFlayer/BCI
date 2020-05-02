import sys
import time
from threading import Thread
import win32api, win32process, win32con

from config import config_init
from pnhandler import PNHandler
from amp_inlet import get_inlet_amp
from experiment_record import ExperimentRecord
from experiment_realtime import ExperimentRealtime
from stimulator import Stimulator

def main():
    setpriority(pid=None,priority=5)
    
    config = config_init(sys.argv)
    
    # Debug mode uses LSL_Generator for debuging
    if config['general'].getboolean('debug_mode'):
        print('Debug Mode!!!')
        sys.path.append(config['paths']['lsl_stream_generator_path'])
        sys.path.append(config['paths']['lsl_stream_generator_path'] + '/pynfb')
        from generators import run_eeg_sim
        freq = config['amp_config'].getint('fs_amp')
        name = config['amp_config']['lsl_stream_name_amp']
        labels = ['channel{}'.format(i) for i in range(config['amp_config'].getint('n_channels_amp'))]
        lsl_stream_debug = lambda: run_eeg_sim(freq, name=name, labels=labels)
        lsl_stream_debug_tread = Thread(target=lsl_stream_debug, args=())
        lsl_stream_debug_tread.daemon = True
        lsl_stream_debug_tread.start()
        print("generators.run_eeg_sim start DEBUG LSL \"{}\"".format(config['amp_config']['lsl_stream_name_amp']))
    
    # initiate stream of PN and Amp data
    pnhandler = PNHandler(config)
    pnhandler.start()
    inlet_amp = get_inlet_amp(config)
    time.sleep(1.5)
    
    # record train data
    if config['general'].getboolean('record_enable'):    
        experiment_record = ExperimentRecord(config, pnhandler, inlet_amp)
        experiment_record.record_data()
        input("Data is recorded, press Enter to continue...")
    
    # start realtime experiment
    if not config['general'].getboolean('record_enable'):
        return
    
    # stimulate during realtime
    stimulator = Stimulator(config)
    stimulator.connect()

    #
    try:
        experiment_realtime = ExperimentRealtime(config, pnhandler, inlet_amp, stimulator)
        experiment_realtime.fit()
        experiment_realtime.decode()
    finally:
        
        stimulator.close_connection()

    
    
def setpriority(pid=None,priority=1):
    """ Set The Priority of a Windows Process.  Priority is a value between 0-5 where
        2 is normal priority.  Default sets the priority of the current
        python process but can take any valid process ID. """
    priorityclasses = [win32process.IDLE_PRIORITY_CLASS,
                       win32process.BELOW_NORMAL_PRIORITY_CLASS,
                       win32process.NORMAL_PRIORITY_CLASS,
                       win32process.ABOVE_NORMAL_PRIORITY_CLASS,
                       win32process.HIGH_PRIORITY_CLASS,
                       win32process.REALTIME_PRIORITY_CLASS]
    if pid == None:
        pid = win32api.GetCurrentProcessId()
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    win32process.SetPriorityClass(handle, priorityclasses[priority])

    
    
if __name__ == '__main__':
    main()    
    
    