import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from datetime import datetime as dt
from time import gmtime, localtime

from scrap import getLaunches, geocode

mapbox_access_token = 'pk.eyJ1IjoiYW5kcmV5ZGVuIiwiYSI6ImNqbmhwdGlkMjBhYzQzanJzbTM3NzdobW8ifQ.ZR_vrBuTDB1-byVDkuxn4g'
mapbox_style = 'mapbox://styles/andreyden/cjnhrugdjbmfl2rmmiv5dpojt'

past = getLaunches(True)
to_be_launched = getLaunches()
launches = pd.DataFrame(data=past+to_be_launched)
launches = launches[~launches['lat'].isna()]


app = dash.Dash(__name__)

app.css.append_css({
   'external_url': (
       'main.css'
   )
})

app.layout = html.Div(
    className='main',
    children=[
        html.H1(
            'LAUNCH.IO'
        ),
        html.H1(
            id='Timer',
            children='0'
        ),
        html.Div([
            dcc.Graph(
                id='map',
                figure=go.Figure(
                    data=[
                        go.Scattermapbox(
                            lat=launches['lat'],
                            lon=launches['long'],
                            mode='markers',
                            marker=dict(
                                size=14,
                                color='limegreen'
                            ),
                            hoverinfo='text',
                            text=launches['location'],
                        )],
                    layout=go.Layout(
                        hovermode='closest',
                        margin=go.layout.Margin(
                            l=10,
                            r=10,
                            b=0,
                            t=0,
                            pad=8
                        ),
                        mapbox=dict(
                            accesstoken=mapbox_access_token,
                            style=mapbox_style,
                            bearing=0,
                            center=dict(
                                lat=45,
                                lon=-73
                            ),
                            pitch=0,
                            zoom=1
                        )
                    )
                ),
                config={'displayModeBar': False}
            )
        ]),
        html.Div(
            dcc.Interval(
                id='interval-component',
                interval=1000,
                n_intervals=0
            )
        ),
        html.Div([
            dcc.Tabs(id="tabs", value='tab-1', children=[
                dcc.Tab(label='All launches on this locatino', value='tab-1'),
                dcc.Tab(label='ALL', value='tab-2'),
            ]),
            html.Div(
                id='rocket'
            )
        ])
    ]
)

@app.callback(Output('rocket', 'children'),
              [Input('map', 'clickData'), Input('tabs', 'value')])
def update_on_click(clickData, tab):
    launch = launches[launches['lat'] == clickData['points'][0]['lat']]

    if tab == 'tab-1':
        return [
            html.Div(
                className="launch",
                children=[
                    html.Div(
                        className="top",
                        children=[html.H1("Mission: "+row['mission'])],
                    ),
                    html.Div(
                        className="bottom",
                        children=[
                            html.Img(src=row['image']),
                            html.Div(className="text",
                            children=[
                                html.Div(
                                    className="info",
                                    children=[
                                        html.P(children=[html.B(children=k.capitalize()), ': '+ str(v)])
                                        for k, v in row.items()
                                        if k in ['vehicle', 'time', 'location', 'pad', 'window'] and str(v) != "nan"
                                    ]
                                ),
                                html.Div(
                                    className="description",
                                    children=launch['description'],
                                )
                            ])

                        ]
                    )
                ]
            ) for index, row in launch.iterrows()
        ]
    elif tab == 'tab-2':
        return [
            html.Div(
                className="launch",
                children=[
                    html.Div(
                        className="top",
                        children=[html.H1("Mission: "+row['mission'])],
                    ),
                    html.Div(
                        className="bottom",
                        children=[
                            html.Img(src=row['image']),
                            html.Div(className="text",
                            children=[
                                html.Div(
                                    className="info",
                                    children=[
                                        html.P(children=[html.B(children=k.capitalize()), ': '+ str(v)])
                                        for k, v in row.items()
                                        if k in ['vehicle', 'time', 'location', 'pad', 'window'] and str(v) != "nan"
                                    ]
                                ),
                                html.Div(
                                    className="description",
                                    children=launch['description'],
                                )
                            ])

                        ]
                    )
                ]
            ) for index, row in launches.iterrows()
        ]

@app.callback(Output('Timer', 'children'),
              [Input('interval-component', 'n_intervals')])
def timeToNearestLaunch(n):
    T = to_be_launched[0]['time']
    T = T[-20:-1]

    diff = dt.strptime(T, '%Y-%m-%d %H:%M:%S') - dt.utcnow()
    tz_diff = localtime().tm_hour - gmtime().tm_hour #(gmtime().tm_day - localtime().tm_day)*24
    full_seconds = 24*3600*diff.days
    hours = int((full_seconds-diff.seconds)/3600/24) - tz_diff
    minutes = int((diff.seconds-hours*60)/60/24)
    return 'Next launch: {} day(s) {} hour(s) {} minute(s) {} second(s)'.format(diff.days,
                                                                   hours,
                                                                   minutes,
                                                                   diff.seconds%60)

if __name__ == '__main__':
    app.scripts.config.serve_locally = False
    app.run_server()
