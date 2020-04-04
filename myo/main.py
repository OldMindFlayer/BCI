import sys
import time
from threading import Thread
import win32api, win32process, win32con

from config import config_init
from pnhandler import PNHandler
from experiment_record import ExperimentRecord
from experiment_realtime import ExperimentRealtime

def main():
    setpriority(pid=None,priority=5)
    
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
    
    pnhandler = PNHandler(config, TCP_IP='127.0.0.1', TCP_PORT = 7010, BUFFER_SIZE = 1800)
    pnhandler.start()
    time.sleep(1.5)

    experiment_record = ExperimentRecord(config, pnhandler)
    experiment_record.record_data()
    lsl_inlet_amp = experiment_record.get_inlet_amp()
    
    experiment_realtime = ExperimentRealtime(config, lsl_inlet_amp, pnhandler)
    experiment_realtime.fit()
    experiment_realtime.decode()
    
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
    
    