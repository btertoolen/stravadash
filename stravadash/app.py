# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd
import requests
import json
import polyline
from plotly.subplots import make_subplots
app = Dash(__name__)

app.css.append_css({"external_url": "/assets/main.css"})
app.server.static_folder = "assets"
image_path = 'assets/stravadash.png'

app.layout = html.Div(children=[
    html.Div(
        children=[
            html.Img(src=image_path),
            html.H1('Volume running dashboard')
        ],
        className='h1-and-image-container'
    ),
    html.H2(children='Running Totals', style={
        'textAlign': 'center', 'color': '#FF6D00'}),

    # Put totals into a table
    html.Table(id='total-table'),

    dcc.Graph(
        id='volumes-graph',
    ),

    dcc.Graph(
        id='pace-hr-graph'
    ),

    dcc.Graph(
        id='running-map'
    ),

    dcc.Interval(
        id='interval-update',
        interval=10000,
        n_intervals=0
    )

], style={'textAlign': 'center'})


@ callback(Output('running-map', 'figure'),
           Input('interval-update', 'n_intervals'))
def update_running_map(n):
    routes = ''
    lats = []
    lons = []
    with open("../data/running_map.json", 'r') as f:
        routes = json.load(f)
    decoded_polylines = []
    for item in routes['polylines']:
        decoded_points = polyline.decode(item["line"])
        for tuple in decoded_points:
            lats.append(tuple[0])
            lons.append(tuple[1])
        lats.append(None)
        lons.append(None)
    df = pd.DataFrame(decoded_polylines, columns=['lat', 'lon'])
    fig = px.line_mapbox(lat=lats, lon=lons, zoom=5.5)
    fig.update_layout(mapbox_style="carto-darkmatter")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


@ callback(Output('total-table', 'children'),
           Input('interval-update', 'n_intervals'))
def update_totals(n):
    totals = ''
    with open('../data/running_total.json', 'r') as f:
        totals = f.read()

    # Get value of count key from totals json object
    totals = json.loads(totals)
    totals_string = ''
    if totals:
        totals_string = "Number of runs: {0}\tTotal distance(km): {1}\t \
                        Time spent running(hours): {2}\tTotal elevation gain: \
                        {3}".format(
            totals["count"],
            round(totals["distance"]/1000),
            round(totals["moving_time"]/60/60),
            totals["elevation_gain"])
    return [
        html.Tr([html.Td('Number of runs'), html.Td(totals["count"])]),
        html.Tr([html.Td('Total distance(km)'), html.Td(
                round(totals["distance"]/1000))]),
        html.Tr([html.Td('Time spent running(hours)'),
                html.Td(round(totals["moving_time"]/60/60))]),
        html.Tr([html.Td('Total elevation gain'),
                html.Td(totals["elevation_gain"])])
    ]


@ callback(Output('volumes-graph', 'figure'),
           Input('interval-update', 'n_intervals'))
def update_volumes(n):
    volumes = ''
    with open('../data/weekly_volumes.json', 'r') as f:
        volumes = json.load(f)

    x = list()
    y = list()
    for item in volumes:
        x.append("Week of {}".format(item["weekStart"].split()[0]))
        y.append(item["volume"])

    y = [val for val in reversed(y)]
    x = [val for val in reversed(x)]

    # Pass an index to the DataFrame
    df = pd.DataFrame({'x': x, 'y': y}, index=[i for i in range(len(x))])
    fig = px.line(data_frame=df, x='x', y='y', title='Weekly running volume')
    fig.update_yaxes(range=[0, 100000])
    fig.update_xaxes(title_text='Week')
    fig.update_yaxes(title_text='Volume (km)')
    fig.update_layout(font=dict(family="Fira Sans, serif", size=16))
    fig.update_layout(plot_bgcolor='#1F1F1F')
    fig.update_layout(paper_bgcolor='#1F1F1F')
    fig.update_layout(font_color='#FF6D00')
    fig.update_traces(line=dict(color='#FF4800'))
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=False),
            type="category",
            gridcolor='#FFB600'  # Update grid lines color
        ),
        yaxis=dict(
            fixedrange=True,
            gridcolor='#FFB600'  # Update grid lines color
        ),
        margin=dict(l=0, r=0, t=35, b=0)  # Reduce the empty space

    )
    fig.update_yaxes(gridcolor='#FFB600', dtick=10000)
    return fig
    # Update the totals-output div with the contents of the file


@ callback(Output('pace-hr-graph', 'figure'),
           Input('interval-update', 'n_intervals'))
def update_pace_hr_graph(n):
    paces = ''

    with open('../data/pace_hr.json', 'r') as f:
        paces = json.load(f)

    x = list()
    y_pace = list()
    y_hr = list()
    for item in paces:
        x.append(item["date"].split()[0])
        y_pace.append(item["pace"])
        y_hr.append(item["heartRate"])

    df = pd.DataFrame({'x': x, 'y_pace': y_pace, 'y_hr': y_hr},
                      index=[i for i in range(len(x))])
    pace_hr_fig = make_subplots(specs=[[{"secondary_y": True}]])
    pace_hr_fig.add_bar(x=df['x'],
                        y=df['y_pace'], name='Average running pace',
                        marker=dict(color="#7077A1",
                                    line=dict(color='rgba(0, 0, 0, 1)', width=1)))
    pace_hr_fig.add_scatter(x=df['x'], y=df['y_hr'], mode='lines',
                            name='Heart Rate', secondary_y=True,
                            line=dict(color='#FF4800'), connectgaps=False)
    pace_hr_fig.update_layout(font=dict(family="Fira Sans, serif", size=16))
    pace_hr_fig.update_layout(plot_bgcolor='#1F1F1F')
    pace_hr_fig.update_layout(paper_bgcolor='#1F1F1F')
    pace_hr_fig.update_layout(font_color='#FF6D00')
    pace_hr_fig.update_layout(
        yaxis=dict(
            fixedrange=True,
            gridcolor='#FFB600'  # Update grid lines color
        ),
        xaxis=dict(
            showgrid=False
        ),
        margin=dict(l=0, r=0, t=0, b=0)  # Reduce the empty space
    )
    pace_hr_fig.update_yaxes(gridcolor='#461111', range=[4, 7])
    pace_hr_fig.update_yaxes(gridcolor='#FFBB5C', range=[
        100, 160], dtick=10, secondary_y=True)
    return pace_hr_fig


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
