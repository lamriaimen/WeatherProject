import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import dash_daq as daq
import os

# Load your data
df_weather = pd.read_csv('weatherfact.csv')
df_location = pd.read_csv('location.csv')

df = pd.merge(df_weather, df_location, on='STATION')

station_name_to_id = df.set_index('STATION')['NAME'].to_dict()
id_to_station_name = {name: station for station, name in station_name_to_id.items()}

df['DATE'] = pd.to_datetime(df['DATE'])
df['Year'] = df['DATE'].dt.year
df['Season'] = df['DATE'].dt.month % 12 // 3 + 1
df['Quarter'] = df['DATE'].dt.quarter
df['Month'] = df['DATE'].dt.month

months = ["Janvier", "Fevrier", "Mars", "Avril", "Mai", "Juin", "Juillet", "Aout", "Septembre", "Octobre", "Novembre", "Decembre"]
years = sorted(df['Year'].unique())
saisons = ["Hiver", "Printemps", "Eté", "Automne"]

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    id="global",
    children=[
        html.Div(
            className="header",
            children=[
                html.Img(src='/assets/logo.png', id="logo"),
                html.H1('Weather Dashboard'),
            ]
        ),
        html.Div([
            html.Div(className="station-container",
            children=[
                html.Label('Station', className="label-dropdown"),
                dcc.Dropdown(
                    id='station-dropdown',
                    options=[{'label': station_name_to_id[station], 'value': station} for station in df['STATION'].unique()],
                    value=df['STATION'].unique()[0],
                    placeholder="Nom de la station"
                ),
            ]),
            html.Div(className="inline-dropdown",
            children=[
                html.Label('Year', className="label-dropdown"),
                dcc.Dropdown(
                    id='year-dropdown',
                    options=[{'label': i, 'value': i} for i in years],
                    value=df['Year'].unique()[0],
                    placeholder="Année"
                )
            ]),
            html.Div(className="inline-dropdown",
            children=[
                html.Label('Saison', className="label-dropdown"),
                dcc.Dropdown(
                    id='season-dropdown',
                    options=[{'label': saisons[i-1], 'value': i} for i in df['Season'].unique()],
                    value=df['Season'].unique()[0],
                    placeholder="Saison"
                )
            ]),
            html.Div(className="inline-dropdown",
            children=[
                html.Label('Trimestre', className="label-dropdown"),
                dcc.Dropdown(
                    id='quarter-dropdown',
                    options=[{'label': f'{i} Trimestre', 'value': i} for i in df['Quarter'].unique()],
                    value=df['Quarter'].unique()[0],
                    placeholder="Trimestre"
                )
            ]),
            html.Div(className="inline-dropdown",
            children=[
                html.Label('Month', className="label-dropdown"),
                dcc.Dropdown(
                    id='month-dropdown',
                    options=[{'label': months[i-1], 'value': i} for i in df['Month'].unique()],
                    value=df['Month'].unique()[0],
                    placeholder="Mois"
                )
            ]),
            daq.BooleanSwitch(
                className="inline-dropdown",
                id='toggle-switch',
                label="Graph / Map",
                color="blue"
            )
        ], className='dropdown-container'),
        dcc.Graph(id='weather-graph'),
        html.Div(id="slider",
            children=[
            html.Label("Année", id="label-slider"),
            dcc.Slider(
                id='year-slider',
                min=min(years),
                max=max(years),
                value=min(years),
                step=2,
                tooltip={"placement": "bottom", "always_visible": True},
            ),
        ]),
        dcc.Graph(id='map-graph'),
    ]
)

@app.callback(
    Output('weather-graph', 'figure'),
    [
        Input('station-dropdown', 'value'),
        Input('year-dropdown', 'value'),
        Input('season-dropdown', 'value'),
        Input('quarter-dropdown', 'value'),
        Input('month-dropdown', 'value'),
        Input('toggle-switch', 'on')
    ]
)
def update_graph(selected_station, year, season, quarter, month, toggle):
    filtered_df = df[
        (df['STATION'] == selected_station) &
        (df['Year'] == year) &
        (df['Season'] == season) &
        (df['Quarter'] == quarter) &
        (df['Month'] == month)
    ]

    if toggle:
        figure = go.Figure(
            data=[
                go.Bar(
                    x=filtered_df['DATE'],
                    y=filtered_df['PRCP'],
                    name='Precipitation'
                )
            ],
            layout=go.Layout(
                title=f'Données météorologiques pour la station {station_name_to_id[selected_station]}',
                xaxis={'title': 'Date'},
                yaxis={'title': 'Precipitation'},
            )
        )
    else:
        figure = go.Figure(
            data=[
                go.Scatter(
                    x=filtered_df['DATE'],
                    y=filtered_df['PRCP'],
                    mode='lines+markers',
                    name='Precipitation'
                )
            ],
            layout=go.Layout(
                title=f'Données météorologiques pour la station {station_name_to_id[selected_station]}',
                xaxis={'title': 'Date'},
                yaxis={'title': 'Precipitation'},
            )
        )

    return figure

@app.callback(
    Output('map-graph', 'figure'),
    [
        Input('year-slider', 'value'),
        Input('season-dropdown', 'value'),
        Input('quarter-dropdown', 'value'),
        Input('month-dropdown', 'value')
    ]
)
def update_map(selected_year, selected_season, selected_quarter, selected_month):
    filtered_df = df[(df['Year'] == selected_year) &
                     (df['Season'] == selected_season) &
                     (df['Quarter'] == selected_quarter) &
                     (df['Month'] == selected_month)]

    fig = px.density_mapbox(filtered_df, lat='LATITUDE', lon='LONGITUDE', z='TMAX',
                            radius=10,
                            center={'lat': filtered_df['LATITUDE'].mean(), 'lon': filtered_df['LONGITUDE'].mean()},
                            zoom=4,
                            mapbox_style='carto-positron',
                            color_continuous_scale='OrRd')
    fig.update_layout(mapbox_style='open-street-map')
    fig.update_layout(
        mapbox={
            'center': {'lat': 30, 'lon': 0},
            'zoom': 4
        }
    )
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
