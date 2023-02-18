"""
Script to use speedtest-cli to query internet speed every 1--10 mins and
plot to live updating step plot.
"""
from bokeh.models import ColumnDataSource, DatetimeTickFormatter
from bokeh.plotting import figure, curdoc
import numpy as np
from pandas import to_datetime, DatetimeIndex
from speedtest import Speedtest, ConfigRetrievalError

from datetime import datetime
from time import sleep


def do_speedtest():
    """
    Do the speed test and retrieve upload/ download speeds.
    
    Returns
    -------
    t: Timestamp
        Current time in pandas timestamp format
    dl: float
        Download speed in MB
    up: float
        Upload speed in MB
    """
    try:
        st = Speedtest()  # do speed test
        dl = st.download() / 1024 ** 2  # in MB from B
        up = st.upload() / 1024 ** 2  # in MB from B
    except ConfigRetrievalError:  # if the connection drops out
        dl = 0.
        up = 0.
        sleep(300)  # try again in 5 minutes
    t = to_datetime(datetime.now())  # timestamp version of time now
    return t, dl, up


def callback():
    """
    Python callback event handler

    """
    wait = np.random.uniform(0, 9)  # wait between 0 and 9 minutes
    print(f'Next ping in {wait:.1f} mins')
    sleep(wait * 60)
    t, dl, up = do_speedtest()  # perform speed test
    ts = source.data['Time'].tolist()  # datetimeindex to list
    ts.append(t)
    dls = source.data['Download']
    dls.append(dl)
    ups = source.data['Upload']
    ups.append(up)
    source.data = {'Time': DatetimeIndex(ts),
        'Download': dls, 'Upload': ups}  # update source data
    return


# initialising
print('Starting Test')
_t, _dl, _up = do_speedtest()  # start value
print(f'Start values: Download = {_dl:.1f} MB, Upload = {_up:.1f} MB')
source = ColumnDataSource({'Time': DatetimeIndex([_t, ]),  # init CDS
    'Download': [_dl, ], 'Upload': [_up, ]})

# figure formatting
print('Creating Plot')
p = figure(x_axis_type='datetime', sizing_mode='stretch_width')  # create plot
p.xaxis.formatter = DatetimeTickFormatter(microseconds='%I:%M %p',
    milliseconds='%I:%M %p', seconds='%I:%M %p', minsec='%I:%M %p',
    minutes='%I:%M %p', hourmin='%I:%M %p', hours='%I:%M %p',
    days='%d-%b', months='%b/%Y')
p.xaxis.axis_label = 'Time'
p.yaxis.axis_label = 'Speed [MB]'
p.xaxis.axis_label_text_font_size = '4em'
p.yaxis.axis_label_text_font_size = '3em'
p.xaxis.major_label_text_font_size = '2em'
p.yaxis.major_label_text_font_size = '2em'

# plotting
line = p.step(x='Time', y='Download', source=source, legend_label='Download',
    line_color='blue', line_width=3, mode='after')  # download plot
upline = p.step(x='Time', y='Upload', source=source, legend_label='Upload',
    line_color='orange', line_width=3, mode='after')  # upload plot
p.legend.label_text_font_size = '1.5em'

# python server side
doc = curdoc()
doc.add_root(p)
print('Waiting for callbacks')
doc.add_periodic_callback(callback, 60000)  # try callback every minute
doc.title = 'Internet Check'
