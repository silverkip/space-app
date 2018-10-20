import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
import numpy as np

from scrap import getLaunches, geocode

mapbox_access_token = 'pk.eyJ1IjoiYW5kcmV5ZGVuIiwiYSI6ImNqbmhwdGlkMjBhYzQzanJzbTM3NzdobW8ifQ.ZR_vrBuTDB1-byVDkuxn4g'
mapbox_style = 'mapbox://styles/andreyden/cjnhrugdjbmfl2rmmiv5dpojt'

launches = pd.DataFrame(data=getLaunches(True)+getLaunches())

launches = launches[~launches['lat'].isna()]

print(launches['lat'].isna().any())

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
            'TIMER'
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
                        )
                    ],
                    layout=go.Layout(
                        hovermode='closest',
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
                        ),
                    )
                ),
                config={'displayModeBar': False}
            )
        ]),
        html.Div(
            id='rocket',
            children='Temp'
        )
    ]
)

@app.callback(Output('rocket', 'children'),
              [Input('map', 'clickData')])
def update_on_click(clickData):

    launch = launches[launches['lat'] == clickData['points'][0]['lat']]

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
                        html.Div(className="picture"),
                        html.Div(
                            className="info",
                            children=[
                                html.P(children=[html.B(children=k.capitalize()), ': '+ str(v)])
                                for k, v in row.items() 
                                if k in ['vehicle', 'time', 'location', 'pad', 'window']
                                if v != "nan"
                            ]
                        ), 
                        html.Div(
                            className="description", 
                            children=launch['description'],
                        )
                    ]
                )
            ]
        ) for index, row in launch.iterrows()
    ]


if __name__ == '__main__':
    app.run_server()
