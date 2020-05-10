# BCI

## requirements
* install Anaconda3 distribution
* install pylsl
> pip install pylsl
* for gebug mode (to emulate amplifier):
    * download NFB Lab from https://github.com/nikolaims/nfb into the same folder BCI was downloaded

### start in custom mode (parameters in the file config.ini -> general)
> python main.py

### start in default mode
> python main.py -default

### start in record mode (only recording PN and Amplifier data)
> python main.py -record

### start in realtime mode (fit recorded data and run realtime experiment)
> python main.py -realtime

### start in debug mode
> python main.py -debug

