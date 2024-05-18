import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os 
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_daq as daq
import pandas as pd
import plotly.express as px
import os


# df_weather = pd.read_csv(os.path.join(os.getcwd(),'.','weatherfact.csv' ))
df_weather = pd.read_csv('weatherfact.csv')
# Load the location data CSV file into a pandas DataFrame
# df_location = pd.read_csv(os.path.join(os.getcwd(),'.','location.csv' ))
df_location=pd.read_csv('location.csv')
# Merge the weather and location data based on a common key, for example, 'STATION'
df = pd.merge(df_weather, df_location, on='STATION')


station_name_to_id = df.set_index('STATION')['NAME'].to_dict()
id_to_station_name = {name: station for station, name in station_name_to_id.items()}

# Convertir la colonne 'DATE' en datetime
df['DATE'] = pd.to_datetime(df['DATE'])

# Extraire l'année, la saison, le trimestre et le mois de la colonne 'DATE'
df['Year'] = df['DATE'].dt.year
df['Season'] = df['DATE'].dt.month % 12 // 3 + 1
df['Quarter'] = df['DATE'].dt.quarter
df['Month'] = df['DATE'].dt.month
months=["Janvier","Fevrier","Mars","Avril", "Mai","Juin","Juillet","Aout","Septembre","Octobre", "Novembre","Decembre"]
years = sorted(df['Year'].unique())
saisons=["Hiver","Printemps","Eté","Automne"]
slider_year = []
for year in years:
    step = {'label': str(year), 'method': 'update', 'args': [{'visible': [True, True]}]}
    slider_year.append(step)
# Initialisation de l'application Dash
app = dash.Dash(__name__)
server=app.server
# Configuration de la mise en page de l'application
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
            #value=False,
            label="Graph / Map",
            
            color="blue"
        )
    ], 
    className='dropdown-container'),
    dcc.Graph(id='weather-graph'),
    html.Div(id="slider", 
        children=[
        html.Label("Année",id="label-slider"),
        dcc.Slider(
            id='year-slider',
            min=min(years),
            max=max(years),
            #marks={i: years[i] for i in years},
            value=min(years),
            step=2,
            tooltip={"placement":"bottom","always_visible":True},
            
        ),
    ]),
    
    dcc.Graph(id='map-graph'),
    
])

# Mise à jour du graphique météo en fonction de la station sélectionnée
""" @app.callback(
    Output('weather-graph', 'figure'),
    [Input('station-dropdown', 'value')]
)
def update_weather_graph(selected_station):
    filtered_df = df[df['STATION'] == selected_station]
    
    fig = {
        'data': [
            {'x': filtered_df['DATE'], 'y': filtered_df['PRCP'], 'type': 'bar', 'name': 'Précipitation'},
            {'x': filtered_df['DATE'], 'y': filtered_df['TAVG'], 'type': 'line', 'name': 'Température moyenne'},
            {'x': filtered_df['DATE'], 'y': filtered_df['TMAX'], 'type': 'line', 'name': 'Température maximale'},
            {'x': filtered_df['DATE'], 'y': filtered_df['TMIN'], 'type': 'line', 'name': 'Température minimale'}
        ],
        'layout': {
            'title': f'Données météorologiques pour la station {station_name_to_id[selected_station]}',

            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Valeur'}
        }
    }
    return fig """

#--- Another graph for precipitation
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
        # Create a bar chart for precipitation
        figure = go.Figure(
            data=[
                go.Bar(
                    x=filtered_df['DATE'],  # X-axis: Month
                    y=filtered_df['PRCP'],  # Y-axis: Precipitation
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
        # Create a line chart for precipitation
        figure = go.Figure(
            data=[
                go.Scatter(
                    x=filtered_df['DATE'],  # X-axis: Month
                    y=filtered_df['PRCP'],  # Y-axis: Precipitation
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
# Mise à jour de la carte en fonction des filtres sélectionnés
@app.callback(
    Output('map-graph', 'figure'),
    [Input('year-slider', 'value'),
     Input('season-dropdown', 'value'),
     Input('quarter-dropdown', 'value'),
     Input('month-dropdown', 'value')]
)
def update_map(selected_year, selected_season, selected_quarter, selected_month):
    filtered_df = df[(df['Year'] == selected_year) &
                     (df['Season'] == selected_season) &
                     (df['Quarter'] == selected_quarter) &
                     (df['Month'] == selected_month)]
    
    # fig = px.scatter_mapbox(filtered_df, lat='LATITUDE', lon='LONGITUDE', hover_name='NAME',
    #                         hover_data=['PRCP', 'TAVG', 'TMAX', 'TMIN'], color='TMAX',
    #                         color_continuous_scale='Viridis', zoom=4, height=600)
    fig = px.density_mapbox(filtered_df, lat='LATITUDE', lon='LONGITUDE', z='TMAX',
                        radius=10,  # Ajustez le rayon pour le lissage de densité
                        center={'lat': filtered_df['LATITUDE'].mean(), 'lon': filtered_df['LONGITUDE'].mean()},
                        zoom=4,  # Ajustez le niveau de zoom
                        mapbox_style='carto-positron',  # Choisissez un style de carte Mapbox
                        color_continuous_scale='OrRd',  # Choisissez l'échelle de couleurs, ici 'OrRd' (orange-rouge)
                        )
    fig.update_layout(mapbox_style='open-street-map')
    fig.update_layout(
        mapbox={
            #lon = 3 c'est mieux
            'center': {'lat': 30, 'lon': 0},
            'zoom': 4
        }
    )
    
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
