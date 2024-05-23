import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import os 
from dash import dcc, html
import dash_daq as daq
import pandas as pd
import plotly.express as px


df_weather = pd.read_csv(os.path.join(os.getcwd(),'.','weatherfact.csv' ))

# Load the location data CSV file into a pandas DataFrame
df_location = pd.read_csv(os.path.join(os.getcwd(),'.','location.csv' ))

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

# Les valeurs des dropdowns à afficher
months=["Janvier","Fevrier","Mars","Avril", "Mai","Juin","Juillet","Aout","Septembre","Octobre", "Novembre","Decembre"]
years = sorted(df['Year'].unique())
saisons=["Hiver","Printemps","Eté","Automne"]
dropdown_map={
    'TAVG':"Température moyenne",
    'TMAX':"Température maximale",
    'TMIN':"Température minimale",
    'PRCP':"Précipitation",
    'SNWD':"Épaisseur de la neige",
    'WSFG':"Vitesse maximale du vent en rafale",

}

z_options = list(dropdown_map.keys())
# get country icons
def get_station_icon(station_name):
    if 'AG' in station_name:
        return 'dz.png'
    elif 'TS' in station_name:
        return 'tn.png'
    elif 'MO' in station_name:
        return 'mr.png'
    elif 'SP' in station_name:
        return 'es.png'
    else:
        return None

# Create dropdown options with icons
dropdown_options_station = []
for station in df['STATION'].unique():
    icon = get_station_icon(station)
    if icon:
        option_label = html.Span([
            html.Img(src=f'/assets/icons/{icon}', style={'height': '20px', 'margin-right': '10px', 'vertical-align': 'middle','margin-bottom':'3px'}),
            station_name_to_id[station]
        ])
    else:
        option_label = station
    dropdown_options_station.append({'label': option_label, 'value': station})

# Create dropdown Attribute with icons
dropdown_options_attr = []
for z_option in z_options:
    icon = f"{z_option.lower()}.png"
    option_label = html.Span(
    style={'display': 'flex', 'align-items': 'center','margin-top':'7px'},
    children=[
        html.Img(src=f'/assets/icons/{icon}', style={'height': '30px', 'margin-right': '10px', 'vertical-align': 'middle'}),
        dropdown_map[z_option]
    ])
    dropdown_options_attr.append({'label': option_label, 'value': z_option})
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
            html.Img(src='/assets/icons/logo.png', id="logo"),
            html.H1('Weather Dashboard'),
        ]
    ),
    html.Div([
        html.Div(className="station-container",
        children=[
            html.Label('Station', className="label-dropdown"),
            dcc.Dropdown(
                optionHeight=40,
                id='station-dropdown',
                options=dropdown_options_station, #[{'label': station_name_to_id[station], 'value': station} for station in df['STATION'].unique()],
                value=df['STATION'].unique()[0],
                placeholder="Nom de la station"
            ), 
        ]),
        html.Label("Séléctionnez une plage d'année", className="label-dropdown"),
        dcc.RangeSlider(
            id='range-slider',
            min=min(years),
            max=max(years),
            value=[min(years),max(years)],
            marks={str(i): str(i) for i in years if i % 10==0},
            step=1,
            tooltip={"placement":"bottom","always_visible":True}, 
        ),
    ], 
    className='dropdown-container'),
    #dcc.Graph(id='weather-graph'),
    dcc.Graph(id='weather-graph'),
    html.Div(id="div-map",
        children=[
        html.Div(
            id="slider", 
            children=[
            html.Label("Séléctionnez une année", id="label-slider", className="label-dropdown"),
            dcc.Slider(
                id='year-slider',
                min=min(years),
                max=max(years),
                marks={str(i): str(i) for i in years if i % 10==0},
                value=min(years),
                step=1,
                tooltip={"placement":"bottom","always_visible":True},    
            ),
        ]),
        html.Div(className="inline-dropdown",
        children=[
            html.Label('Saison', className="label-dropdown2"),
            dcc.Dropdown(
                id='season-dropdown',
                options=[{'label': saisons[i-1], 'value': i} for i in df['Season'].unique()],
                value=df['Season'].unique()[0],
                placeholder="Saison"
            )
        ]),
        html.Div(className="inline-dropdown",
        children=[
            html.Label('Trimestre', className="label-dropdown2"),
            dcc.Dropdown(
                id='quarter-dropdown',
                options=[{'label': f'{i} Trimestre', 'value': i} for i in df['Quarter'].unique()],
                value=df['Quarter'].unique()[0],
                placeholder="Trimestre"
            )
        ]),
        html.Div(className="inline-dropdown",
        children=[
            html.Label('Month', className="label-dropdown2"),
            dcc.Dropdown(
                id='month-dropdown',
                options=[{'label': months[i-1], 'value': i} for i in df['Month'].unique()],
                value=df['Month'].unique()[0],
                placeholder="Mois"
            )
        ]),
        html.Div(id="attribute-map-div",
            children=[
            html.Label("Sélectionnez un attribut", className="label-dropdown"),
            dcc.Dropdown(
                # TO DO Ajout icones à coté des options
                optionHeight=50,
                searchable=False,
                id='z-value-dropdown',
                options=dropdown_options_attr,#[{'label': dropdown_map[col], 'value': col} for col in z_options],
                value='TAVG'  # Default value
            )
        ],),
    ]),
    dcc.Graph(id='map-graph'),
    
])

# Mise à jour du graphique météo en fonction de la station sélectionnée
@app.callback(
    Output('weather-graph', 'figure'),
    [Input('station-dropdown', 'value'),
     Input('range-slider', 'value')]
)
def update_weather_graph(selected_station,year_slider):
    start_year, end_year = year_slider
    filtered_df = df[(df['STATION'] == selected_station) &
                     (df['DATE'] >= pd.to_datetime(f'{start_year}-01-01')) &
                     (df['DATE'] <= pd.to_datetime(f'{end_year}-12-31'))]
    fig = go.Figure()
    #print(filtered_df)
    # Add precipitation bar trace
    fig.add_trace(
        go.Bar(
            x=filtered_df['DATE'],
            y=filtered_df['PRCP'],
            name='Précipitation',
            hoverinfo='x+y'
        )
    )

    # Add average temperature line trace
    fig.add_trace(
        go.Scatter(
            x=filtered_df['DATE'],
            y=filtered_df['TAVG'],
            mode='lines',
            name='Température moyenne',
            hoverinfo='x+y',
        )
    )

    # Add maximum temperature line trace
    fig.add_trace(
        go.Scatter(
            x=filtered_df['DATE'],
            y=filtered_df['TMAX'],
            mode='lines',
            name='Température maximale',
            hoverinfo='x+y'
        )
    )

    # Add minimum temperature line trace
    fig.add_trace(
        go.Scatter(
            x=filtered_df['DATE'],
            y=filtered_df['TMIN'],
            mode='lines',
            name='Température minimale',
            hoverinfo='x+y'
        )
    )

    # Add minimum temperature line trace
    fig.add_trace(
        go.Scatter(
            x=filtered_df['DATE'],
            y=filtered_df['SNWD'],
            mode='lines',
            name="Épaisseur de la neige",
            hoverinfo='x+y'
        )
    )
    # Add minimum temperature line trace
    fig.add_trace(
        go.Scatter(
            x=filtered_df['DATE'],
            y=filtered_df['WSFG'],
            mode='lines',
            name="Vitesse maximale du vent en rafale",
            hoverinfo='x+y'
        )
    )

    # Update layout
    fig.update_layout(
        title={
            'text':f'Données météorologiques pour la station {station_name_to_id[selected_station]}',
            'xanchor': 'center',
            'x': 0.5,
        },
        xaxis_title='Date',
        yaxis_title='Valeur',
        hovermode='x',  # ensures hover information appears on all traces at the same x value
        xaxis=dict(type='date'),
    )
    return fig

#--- Another graph for precipitation
""" @app.callback(
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

                title={
                    'text':f'Données météorologiques pour la station {station_name_to_id[selected_station]}',
                    'xanchor': 'center',
                    'x': 0.5,
                },
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
                title={
                    'text':f'Données météorologiques pour la station {station_name_to_id[selected_station]}',
                    'xanchor': 'center',
                    'x': 0.5,
                },
                xaxis={'title': 'Date'},
                yaxis={'title': 'Precipitation'},
                
            )
        )

    return figure """
    
# Mise à jour de la carte en fonction des filtres sélectionnés
@app.callback(
    Output('map-graph', 'figure'),
    [Input('year-slider', 'value'),
     Input('season-dropdown', 'value'),
     Input('quarter-dropdown', 'value'),
     Input('month-dropdown', 'value'),
     Input('z-value-dropdown', 'value')]
)
def update_map(selected_year, selected_season, selected_quarter, selected_month,z_value):
    filtered_df = df[(df['Year'] == selected_year) &
                     (df['Season'] == selected_season) &
                     (df['Quarter'] == selected_quarter) &
                     (df['Month'] == selected_month)]
    
    # fig = px.scatter_mapbox(filtered_df, lat='LATITUDE', lon='LONGITUDE', hover_name='NAME',
    #                         hover_data=['PRCP', 'TAVG', 'TMAX', 'TMIN'], color='TMAX',
    #                         color_continuous_scale='Viridis', zoom=4, height=600)
    match z_value:
        case 'TMAX':
            color='OrRd'
        case 'TMIN':
            color="Blues"
        case 'TAVG':
            color=[[0, '#589e57'], [0.5, '#406f49'], [1, '#344a35']]
        case 'PRCP':
            color=[[0, '#2596be'], [0.5, '#165a72'], [1, '#0b2d39']]
        case 'SNWD':
            color="mint"
        case 'WSFG':
            color=[[0,'#acd3e0'],[0.5,'#8dc4dc'],[1, '#a6daff']]
        case _:
            color="Viridis"
    fig = px.density_mapbox(filtered_df, lat='LATITUDE', lon='LONGITUDE', z=z_value,
                        radius=10,  # Ajustez le rayon pour le lissage de densité
                        center={'lat': filtered_df['LATITUDE'].mean(), 'lon': filtered_df['LONGITUDE'].mean()},
                        zoom=4,  # Ajustez le niveau de zoom
                        mapbox_style='carto-positron',  # Choisissez un style de carte Mapbox
                        color_continuous_scale= color,  # Choisissez l'échelle de couleurs, ici 'OrRd' (orange-rouge)
                        range_color=(filtered_df[z_value].min(),filtered_df[z_value].max()),
                        hover_data=["STATION"],
                        
                        )
    fig.update_layout(mapbox_style='open-street-map')
    fig.update_layout(
        mapbox={
            #lon = 3 c'est mieux
            'center': {'lat': 30, 'lon': 0},
            'zoom': 4
        },
        hoverlabel=dict(bgcolor="white",font_size=13, font_family="Segoe UI"),
    )
    fig.update_traces(customdata=[[station_name_to_id.get(station_id, "Unknown")] for station_id in filtered_df['STATION']])
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
