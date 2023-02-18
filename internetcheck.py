"""
Script to use speedtest-cli to query internet speed every 1--10 mins and
plot to live updating step plot.
"""
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, BoxAnnotation
from bokeh.plotting import figure, curdoc
import numpy as np
from pandas import to_datetime, DatetimeIndex, Timestamp
import requests
from requests.exceptions import ConnectionError, ConnectTimeout
from speedtest import Speedtest, ConfigRetrievalError, SpeedtestBestServerFailure

from datetime import datetime
from time import sleep
from typing import Tuple


def do_speedtest() -> Tuple[Timestamp, float, float]:
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
    except (ConfigRetrievalError, SpeedtestBestServerFailure):  # if the connection drops out
        dl = 0.
        up = 0.
        sleep(300)  # try again in 5 minutes
    t: Timestamp = to_datetime(datetime.now())  # timestamp version of time now
    return t, dl, up


def ping(address: str) -> float:
    """
    Pings a given address

    Parameters
    ----------
    address
        The resolvable web address

    Returns
    -------
    pingtime
        Time taken for ping in milliseconds
    """
    try:
        response = requests.get('http://' + address, timeout=1)  # ping address
    except (ConnectionError, ConnectTimeout):
        return 0.
    pingtime = response.elapsed.total_seconds() * 1000.  # ping time in ms
    return pingtime


def callback():
    """
    Python callback event handler

    """
    wait = np.random.uniform(0, 2) * 60  # wait between 0 and 2 minutes
    print(f'Next ping in {int(wait)} seconds')
    sleep(wait)
    t, dl, up = do_speedtest()  # perform speed test
    homeping = ping('192.168.0.1')  # ping home
    googleping = ping('google.com')  # ping google
    ts = speedsource.data['Time'].tolist()  # datetimeindex to list
    ts.append(t)
    dls = speedsource.data['Download']
    dls.append(dl)
    ups = speedsource.data['Upload']
    ups.append(up)
    homes = pingsource.data['Home']
    homes.append(homeping)
    googles = pingsource.data['Google']
    googles.append(googleping)
    speedsource.data = {'Time': DatetimeIndex(ts),
                        'Download': dls, 'Upload': ups}  # update speed source data
    pingsource.data = {'Time': DatetimeIndex(ts),
                       'Home': homes, 'Google': googles}  # update ping source data
    return


# initialising
print('Starting Test')
_t, _dl, _up = do_speedtest()  # start value
_homeping = ping('192.168.0.1')
_googleping = ping('google.com')
print(f'Start values: Download = {_dl:.1f} MB/S, Upload = {_up:.1f} MB/S\n'
      f'Home ping = {int(_homeping)} ms, Google ping = {int(_googleping)} ms')
speedsource = ColumnDataSource({'Time': DatetimeIndex([_t, ]),  # init CDS
                                'Download': [_dl, ], 'Upload': [_up, ]})
pingsource = ColumnDataSource({'Time': DatetimeIndex([_t, ]),
                               'Home': [_homeping, ], 'Google': [_googleping, ]})

# figure formatting
# speed plot
print('Creating Plot')
p = figure(x_axis_type='datetime', sizing_mode='stretch_width', height=380)  # create speed plot
p.xaxis.formatter = DatetimeTickFormatter(microseconds='%I:%M %p',
                                          milliseconds='%I:%M %p', seconds='%I:%M %p', minsec='%I:%M %p',
                                          minutes='%I:%M %p', hourmin='%I:%M %p', hours='%I:%M %p',
                                          days='%d-%b', months='%b/%Y')
p.xaxis.axis_label = 'Time'
p.yaxis.axis_label = 'Speed [MB/S]'
p.xaxis.axis_label_text_font_size = '2em'
p.yaxis.axis_label_text_font_size = '2em'
p.xaxis.major_label_text_font_size = '2em'
p.yaxis.major_label_text_font_size = '2em'
# ping plot
p2 = figure(x_axis_type='datetime', sizing_mode='stretch_width', height=380, x_range=p.x_range)  # create ping plot
p2.xaxis.formatter = DatetimeTickFormatter(microseconds='%I:%M %p',
                                           milliseconds='%I:%M %p', seconds='%I:%M %p', minsec='%I:%M %p',
                                           minutes='%I:%M %p', hourmin='%I:%M %p', hours='%I:%M %p',
                                           days='%d-%b', months='%b/%Y')
p2.xaxis.axis_label = 'Time'
p2.yaxis.axis_label = 'Response Time [ms]'
p2.xaxis.axis_label_text_font_size = '2em'
p2.yaxis.axis_label_text_font_size = '2em'
p2.xaxis.major_label_text_font_size = '2em'
p2.yaxis.major_label_text_font_size = '2em'

# plotting
# speed plot
downline = p.step(x='Time', y='Download', source=speedsource, legend_label='Download',
                  line_color='blue', line_width=3, mode='after')  # download plot
upline = p.step(x='Time', y='Upload', source=speedsource, legend_label='Upload',
                line_color='orange', line_width=3, mode='after')  # upload plot
p.legend.label_text_font_size = '1.5em'
# ping plot
homeline = p2.step(x='Time', y='Home', source=pingsource, legend_label='Home Ping',
                   line_color='black', line_width=3, mode='after')  # home ping plot
googleline = p2.step(x='Time', y='Google', source=pingsource, legend_label='Google Ping',
                     line_color='black', line_width=3, mode='after', line_dash='dashed')  # google ping plot
p2.legend.label_text_font_size = '1.5em'
p2.legend.level = 'overlay'
greenping = BoxAnnotation(bottom=0, top=20, fill_color='chartreuse', fill_alpha=0.5)
amberping = BoxAnnotation(bottom=20, top=100, fill_color='gold', fill_alpha=0.5)
redping = BoxAnnotation(bottom=100, fill_color='tomato', fill_alpha=0.45)
p2.add_layout(greenping)
p2.add_layout(amberping)
p2.add_layout(redping)

# python server side
doc = curdoc()
doc.add_root(column([p, p2], sizing_mode='stretch_width'))
print('Waiting for callbacks')
doc.add_periodic_callback(callback, 1000)  # try callback every second
doc.title = 'Internet Check'
