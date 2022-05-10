from fastf1.plotting import team_color
from fastf1.utils import delta_time

from bokeh.plotting import figure, show
from typing import List
import pandas as pd


def init_figure(title=None, x_label=None, y_label=None):
    p = figure()
    p.background_fill_color = "#525151"
    # p.background_fill_alpha = 0.5
    p.border_fill_color = "#525151"

    p.xaxis.axis_line_color = "white"
    p.xaxis.axis_label_text_color = "white"
    p.xaxis.major_tick_line_color = "white"
    p.xaxis.major_label_text_color = "white"
    p.xaxis.minor_tick_line_color = "white"

    p.xgrid.grid_line_alpha = 0.4

    p.yaxis.axis_line_color = "white"
    p.yaxis.axis_label_text_color = "white"
    p.yaxis.major_tick_line_color = "white"
    p.yaxis.major_label_text_color = "white"
    p.yaxis.minor_tick_line_color = "white"

    p.ygrid.grid_line_alpha = 0.4

    if title is not None:
        p.title.text = title
        p.title.text_color = "white"
    
    if x_label is not None:
        p.xaxis.axis_label = x_label

    if y_label is not None:
        p.yaxis.axis_label = y_label

    return p
    

def _add_kwarg(kwargs, key, value):
    if value is not None:
        kwargs[key] = value
    return kwargs


def pick_lap(laps, lap_num):
    return laps[laps.LapNumber == lap_num]
    

def line(lines: List, title=None, x_label=None, y_label=None):
    p = init_figure(title=title, x_label=x_label, y_label=y_label)
    for li in lines:
        x = li['x']
        y = li['y']
        
        kwargs = {
            'color': li.get('color', 'cornflowerblue'),
            'line_width': li.get('line_width', 2),
        }
        
        kwargs = _add_kwarg(kwargs, 'legend_label', li.get('legend_label')) 
        
        if x.dtype == 'timedelta64[ns]':
            x = x / pd.Timedelta(seconds=1)
        if y.dtype == 'timedelta64[ns]':
            y = y / pd.Timedelta(seconds=1)
        
        p.line(x, y, **kwargs)
    show(p)
    

def bar(data: List, title=None, x_label=None, y_label=None):
    p = init_figure(title=title, x_label=x_label, y_label=y_label)
    for d in data:
        x = d['x']
        y = d['y']
        
        if x.dtype == 'timedelta64[ns]':
            x = x / pd.Timedelta(seconds=1)
        if y.dtype == 'timedelta64[ns]':
            y = y / pd.Timedelta(seconds=1)
        
        kwargs = {
            'x': x,
            'top': y,
            'color': d.get('color', 'cornflowerblue'),
        }
        
        kwargs = _add_kwarg(kwargs, 'legend_label', d.get('legend_label'))
        kwargs = _add_kwarg(kwargs, 'width', d.get('width'))
        
        p.vbar(**kwargs)
    show(p)
    
    
def compare_session_bests(session, driver1, driver2):
    d1 = session.laps.pick_driver(driver1)
    d1_team = d1.at[d1.index[0], 'Team']
    d1_fastest = d1.pick_fastest()
    d1_car_data = d1_fastest.get_car_data()

    d2 = session.laps.pick_driver(driver2)
    d2_team = d2.at[d2.index[0], 'Team']
    d2_fastest = d2.pick_fastest()
    d2_car_data = d2_fastest.get_car_data()

    data = [
        {
            'x': d1_car_data['Time'],
            'y': d1_car_data['Speed'],
            'color': team_color(d1_team),
            'legend_label': driver1,
        },
        {
            'x': d2_car_data['Time'],
            'y': d2_car_data['Speed'],
            'color': team_color(d2_team),
            'legend_label': driver2
        }
    ]

    line(data, title=f'{driver1} v. {driver2} Fastest {session.name} Lap', x_label='Time', y_label='Speed [km/h]')


def compare_session_laps(session, driver1, driver2):
    d1 = session.laps.pick_driver(driver1)
    d1_team = d1.at[d1.index[0], 'Team']
    d1_lap_number = d1.LapNumber
    d1_lap_time = d1.LapTime

    d2 = session.laps.pick_driver(driver2)
    d2_team = d2.at[d2.index[0], 'Team']
    d2_lap_number = d2.LapNumber
    d2_lap_time = d2.LapTime

    data = [
        {
            'x': d1_lap_number,
            'y': d1_lap_time,
            'color': team_color(d1_team),
            'legend_label': driver1,
        },
        {
            'x': d2_lap_number,
            'y': d2_lap_time,
            'color': team_color(d2_team),
            'legend_label': driver2
        }
    ]

    line(data, title=f'{driver1} v. {driver2} {session.name} Laps', x_label='Time', y_label='Speed [km/h]')
