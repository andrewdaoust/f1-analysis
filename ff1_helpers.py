from fastf1.plotting import team_color
from fastf1.utils import delta_time

from bokeh.plotting import figure, show
from bokeh.transform import linear_cmap
from bokeh.models import ColumnDataSource, ColorBar
from bokeh.palettes import RdYlBu11, RdBu11
from typing import List
import pandas as pd


TIRE_COLOR = {
    'SOFT': '#fc4432',
    'MEDIUM': '#e8d402',
    'HARD': 'white',
    'INTERMEDIATE': '#3bc82c',
    'WET': '#1788ff',
}


def init_figure(**kwargs):
    p = figure(**kwargs)

    p.title.text_color = "white"

    # p.toolbar.autohide = True

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

    return p


def init_track_figure(**kwargs):
    p = figure(**kwargs)

    p.title.text_color = "black"

    # p.toolbar.autohide = True

    # p.background_fill_color = "#a6a6a6"
    # p.border_fill_color = "#a6a6a6"
    # p.outline_line_color = "#a6a6a6"

    p.axis.visible = False
    p.grid.visible = False
    p.outline_line_color = None

    return p


def configure_legend(p):
    p.legend.background_fill_color = "#525151"
    p.legend.background_fill_alpha = 0.4
    p.legend.label_text_color = "white"
    p.legend.border_line_width = 0
    

def _add_kwarg(kwargs, key, value):
    if value is not None:
        kwargs[key] = value
    return kwargs


def pick_lap(laps, lap_num):
    return laps[laps.LapNumber == lap_num]
    

def line(lines: List, title=None, x_axis_label=None, y_axis_label=None):
    p = init_figure(title=title, x_axis_label=x_axis_label, y_axis_label=y_axis_label)
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
    

def bar(data: List, title=None, x_axis_label=None, y_axis_label=None):
    p = init_figure(title=title, x_axis_label=x_axis_label, y_axis_label=y_axis_label)
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

    line(data, title=f'{driver1} v. {driver2} Fastest {session.name} Lap', x_axis_label='Time', y_axis_label='Speed [km/h]')


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

    line(data, title=f'{driver1} v. {driver2} {session.name} Laps', x_axis_label='Lap #', y_axis_label='Lap time [s]')


def compare_tire_lap_times(session, driver):
    d = session.laps.pick_driver(driver)
    lap_number = d.LapNumber.to_list()
    # lap_time = d1.LapTime
    # lap_time = lap_time / pd.Timedelta(seconds=1)

    compounds = list(set(d.Compound))
    palette = [TIRE_COLOR[c] for c in compounds]

    source = {
        'lap_number': lap_number,
    }

    for compound in compounds:
        source[compound] = []
    
    for idx, lap in d.iterlaps():
        time = lap.LapTime / pd.Timedelta(seconds=1)
        compound = lap.Compound

        for key in source.keys():
            if key in compounds:
                if key == compound:
                    source[key].append(time)
                else:
                    source[key].append(None)

    p = init_figure(title=f'{driver} {session.name} Laps', x_axis_label='Lap #', y_axis_label='Lap time [s]')
    p.vbar_stack(compounds, x='lap_number', width=0.7, color=palette, source=ColumnDataSource(source), legend_label=compounds)

    # p.legend.background_fill_color = "#525151"
    # p.legend.background_fill_alpha = 0.5
    # p.legend.label_text_color = "white"
    configure_legend(p)
    show(p)

def driver_speed_over_lap(session, driver, lap_number):
    d = session.laps.pick_driver(driver)
    if lap_number == 'fastest':
        lap = d.pick_fastest()
    else:
        lap = d[d.LapNumber == lap_number]

    telemetry = lap.get_telemetry()

    x = telemetry.X
    y = telemetry.Y
    speed = telemetry.Speed

    width = round(abs(max(x) - min(x)) / 15)
    height = round(abs(max(y) - min(y)) / 15)

    p = init_track_figure(title=f'{driver} Lap track speeds', plot_width=width, plot_height=height)

    source = ColumnDataSource(dict(x=x,y=y,speed=speed))
    mapper = linear_cmap(field_name='speed', palette=RdBu11 ,low=min(speed) ,high=max(speed))

    p.line(x='x', y='y', line_width=10, color="#ababab", source=source)
    p.circle(x='x', y='y', line_width=4, color=mapper, source=source)

    color_bar = ColorBar(
        color_mapper=mapper['transform'], width=8, 
        background_fill_color=None, title="[km/h]", 
        title_standoff=8, title_text_font_style="normal"
    )

    p.add_layout(color_bar, 'right')

    show(p)


def compare_driver_speed_over_lap(session, driver1, driver2, lap_number):
    d1 = session.laps.pick_driver(driver1)
    d1_team = d1.at[d1.index[0], 'Team']
    d1_color = team_color(d1_team)
    d2 = session.laps.pick_driver(driver2)
    d2_team = d1.at[d1.index[0], 'Team']
    d2_color = team_color(d2_team)
    if lap_number == 'fastest':
        d1_lap = d1.pick_fastest()
        d2_lap = d2.pick_fastest()
    else:
        d1_lap = d1[d1.LapNumber == lap_number]
        d2_lap = d2[d2.LapNumber == lap_number]

    d1_telemetry = d1_lap.get_telemetry()
    d2_telemetry = d2_lap.get_telemetry()

    print(len(d1_telemetry))
    print(len(d2_telemetry))

    x = d1_telemetry.X
    y = d1_telemetry.Y
    d1_speed = d1_telemetry.Speed
    d2_speed = d2_telemetry.Speed

    speed = d1_speed - d2_speed
    mask = speed >= 0
    speed.loc[mask] = 1
    speed.loc[~mask] = 0

    width = round(abs(max(x) - min(x)) / 15)
    height = round(abs(max(y) - min(y)) / 15)

    p = init_track_figure(title=f'{driver1} v. {driver2} Lap track speeds', plot_width=width, plot_height=height)

    source = ColumnDataSource(dict(x=x,y=y,speed=speed))
    mapper = linear_cmap(field_name='speed', palette=[d2_color, d1_color] ,low=0 ,high=1)

    p.line(x='x', y='y', line_width=10, color="#ababab", source=source)
    p.circle(x='x', y='y', line_width=4, color=mapper, source=source)

    # color_bar = ColorBar(
    #     color_mapper=mapper['transform'], width=8, 
    #     background_fill_color=None, title="[km/h]", 
    #     title_standoff=8, title_text_font_style="normal"
    # )

    # p.add_layout(color_bar, 'right')

    show(p)
