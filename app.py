import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime as dt
from time import gmtime, localtime
# local imports
from pages import divTemplate, mapTemplate, INDEX_PAGE, MAIN_PAGE, ROCKETS_PAGE
from consts import LAUNCHES, FUTURE_LAUNCHES

app = dash.Dash(__name__)
server = app.server

# add prewritten css
app.css.append_css({
   'external_url': (
       'main.css'
   )
})

app.config.suppress_callback_exceptions = True

app.layout = html.Div(
    children=[
        dcc.Location(id='url', refresh=False),
        html.Div(className='main', id='Main')
    ]
)

#################################################
################## CALL BACKS ###################
#################################################

@app.callback(Output('Main', 'children'),
              [Input('url', 'pathname')])
def displayRocketList(path_name):
    if path_name == '/':
        return MAIN_PAGE
    elif path_name == '/rockets':
        return ROCKETS_PAGE
    else:
        return INDEX_PAGE

def toTimeDate(T):
    if T == 'TBD':
        return dt(3000, 12, 31)
    else:
        return dt.strptime(T[-20:-1], '%Y-%m-%d %H:%M:%S')

@app.callback(Output('map', 'figure'),
    [Input('date_picker', 'start_date'),
     Input('date_picker', 'end_date')])
def updateMarkersOnDate(st, fin):
    if st and fin:
        times = LAUNCHES['time'].apply(toTimeDate)
        times = times.apply(lambda x: dt.strptime(st, '%Y-%m-%d') <= x <= dt.strptime(fin, '%Y-%m-%d'))
        return mapTemplate(LAUNCHES[times])
    else:
        return mapTemplate(LAUNCHES)

@app.callback(Output('rocket', 'children'),
              [Input('map', 'clickData'),
               Input('tabs', 'value'),
               Input('date_picker', 'start_date'),
               Input('date_picker', 'end_date')])
def updateLaunchList(clickData, tab, st, fin):
    if tab == 'tab-1':
        if not clickData:
            return html.Div(style={'height': "1000px"})
        sameCoords = LAUNCHES['lat'] == clickData['points'][0]['lat']
        comp = lambda x : dt.strptime(st, '%Y-%m-%d') <= \
                          toTimeDate(x) <= \
                          dt.strptime(fin, '%Y-%m-%d')
        inDateRange = LAUNCHES['time'].apply(comp)
        launch = LAUNCHES[sameCoords & inDateRange]
        return [divTemplate(index, row) for index, row in launch.iterrows()]
    elif tab == 'tab-2':
        return [divTemplate(index, row) for index, row in LAUNCHES.iterrows()]

@app.callback(Output('Timer', 'children'),
              [Input('interval-component', 'n_intervals')])
def timeToNearestLaunch(n):
    T = FUTURE_LAUNCHES[0]['time']
    T = T[-20:-1]

    diff = dt.strptime(T, '%Y-%m-%d %H:%M:%S') - dt.utcnow()
    hours, minutes = divmod(diff.seconds/60,60)
    return [html.H1([
                html.A('Next launch:', className='ref', id='next_launch_link'),
                html.H1(
                    ' {} days {} hours {} minutes {} seconds'.format(diff.days,
                                                                     int(hours),
                                                                     int(minutes),
                                                                     diff.seconds%60),
                    id='timer'
                )
            ])]

showing_next_launch_info = False

@app.callback(Output('next_launch', 'children'),
              [Input('next_launch_link', 'n_clicks')])
def showNextLaunchInfo(n_clicks):
    if n_clicks:
        global showing_next_launch_info
        if (showing_next_launch_info):
            showing_next_launch_info = False
            return ''
        else:
            showing_next_launch_info = True
            return divTemplate(1, FUTURE_LAUNCHES[0])

if __name__ == '__main__':
    #app.scripts.config.serve_locally = False
    app.run_server(debug=True)
