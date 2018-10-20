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
    id='main',
    children=[
        html.H1(
            '{Name of App}'
        ),
        html.H1(
            '{Name of App}'
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
                                color='green'
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
    return 'lat:{}, lon:{}'.format(clickData['points'][0]['lat'],
                                   clickData['points'][0]['lon'])

if __name__ == '__main__':
    app.run_server()
