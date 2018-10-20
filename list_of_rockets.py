import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
import numpy as np

app = dash.Dash()

app.css.append_css({
   'external_url': (
       'main.css'
   )
})

app.layout = html.Div([
    html.Div(
        className='rockets',
        children='temp'
    ) for _ in range(10)
])

if __name__ == '__main__':
    app.run_server()
