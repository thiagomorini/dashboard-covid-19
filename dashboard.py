import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go

import numpy as np
import pandas as pd
import json 

CENTER_LAT, CENTER_LON = -15.272572694355336, -54.25567404158474
MAP_ZOOM = 3.5

# Data Frame
# Filtering the data
# https://covid.saude.gov.br/
# df = pd.read_csv("HIST_PAINEL_COVIDBR_2023_Parte1_25jan2023.csv", sep=";")
# df_states = df[(~df["estado"].isna()) & (df["codmun"].isna())]
# df_brazil = df[df["regiao"] == "Brasil"]

# df_states.to_csv("df_states.csv")
# df_brazil.to_csv("df_brazil.csv")

df_states = pd.read_csv("df_states.csv")
df_brazil = pd.read_csv("df_brazil.csv")

df_states_ = df_states[df_states["data"] == "2020-05-13"]
brazil_states = json.load(open("geojson/brazil_geo.json", "r"))
df_date = df_states[df_states["estado"] == "SP"]

select_columns = {
    "casosAcumulado": "Total confirmed cases",
    "casosNovos": "New cases",
    "obitosAcumulado": "Confirmed deaths",
    "obitosNovos": "Deaths per day"
}

# Instantiating the Dash
# https://bootswatch.com/
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=5"}
    ])

def render_map(states):
    fig = px.choropleth_mapbox(
        states,
        locations="estado",
        color="casosAcumulado",
        center={"lat": CENTER_LAT, "lon": CENTER_LON},
        zoom=MAP_ZOOM,
        geojson=brazil_states,
        color_continuous_scale="Redor",
        opacity=0.6,
        hover_data={"estado": True, "casosAcumulado": True, "casosNovos": True, "obitosNovos": True})

    hovertemplate = '<b>%{customdata[0]}</b> <br><br>'
    hovertemplate += 'Confirmed cases: %{customdata[1]:,.0f} <br>'
    hovertemplate += 'New cases: %{customdata[2]:,.0f} <br>'
    hovertemplate += 'Deaths: %{customdata[3]:,.0f}'
    fig.update_traces(hovertemplate=hovertemplate)

    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Confirmed cases"),
        paper_bgcolor="#242424",
        autosize=True,
        margin=go.layout.Margin(l=0, r=0, t=0, b=0),
        showlegend=False,
        mapbox_style="carto-darkmatter"
    )
    return fig

def render_graph(plot_type, date):

    bar_plots = ["casosNovos", "obitosNovos"]

    fig2 = go.Figure(layout={"template": "plotly_dark"})
    if plot_type in bar_plots:
        fig2.add_trace(go.Bar(x=date["data"], y=date[plot_type]))
    else:
        fig2.add_trace(go.Scatter(x=date["data"], y=date[plot_type]))

    hovertemplate = '%{x} <br>'
    hovertemplate += '%{y:,.0f}'
    hovertemplate += "<extra></extra>"
    fig2.update_traces(hovertemplate=hovertemplate)

    fig2.update_layout(
        paper_bgcolor="#242424",
        plot_bgcolor="#242424",
        autosize=True,
        margin=dict(l=10, r=10, t=10, b=10),
        height=280
    )
    return fig2

fig = render_map(df_states_)
fig2 = render_graph("casosAcumulado", df_date)

# Layout (Layout bootstrap)
app.layout = dbc.Container(
    children=[
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("COVID-19 Evolution in Brazil"),
                    dbc.Button("BRAZIL", color="primary", id="location-button", size="sm")
                ], style={"background-color": "#1E1E1E", "margin": "-20px", "padding": "20px"}),

                html.P("Enter the date on which you want information:", style={
                    "margin-top": "30px"}),
                html.Div(id="div-date",
                    children=[
                        dcc.DatePickerSingle(
                            id="date-picker",
                            min_date_allowed=df_brazil["data"].min(),
                            max_date_allowed=df_brazil["data"].max(),
                            initial_visible_month=df_brazil["data"].min(),
                            date=df_brazil["data"].max(),
                            display_format="MMMM D, YYYY",
                            style={"border": "0px solid black"}
                        )
                    ]                    
                ),

                dbc.Row([
                    # First card
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Span("Recovered cases"),
                                html.H5(style={"color": "#adfc92"}, id="recovered-cases-text"),
                                html.Span("In monitoring"),
                                html.H6(id="in-monitoring-text")
                            ])
                        ], color="light", outline=True, style={
                            "margin-top": "10px",
                            "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)",
                            "color": "#ffffff",
                            "font-size": 12
                        })
                    ], md=4),

                    # Second card
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Span("Total confirmed cases"),
                                html.H5(style={"color": "#389fd6"}, id="total-confirmed_cases-text"),
                                html.Span("New cases on date"),
                                html.H6(id="new-cases-on-date-text")
                            ])
                        ], color="light", outline=True, style={
                            "margin-top": "10px",
                            "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)",
                            "color": "#ffffff",
                            "font-size": 12
                        })
                    ], md=4),

                    # Third card
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Span("Confirmed deaths"),
                                html.H5(style={"color": "#df2935"}, id="confirmed-deaths-text"),
                                html.Span("Deaths on date"),
                                html.H6(id="deaths-on-date-text")
                            ])
                        ], color="light", outline=True, style={
                            "margin-top": "10px",
                            "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)",
                            "color": "#ffffff",
                            "font-size": 12
                        })
                    ], md=4)                        
                ]),

                html.Div([
                    html.P("Select the type of data you want to view:", style={
                        "margin-top": "15px"}),
                    dcc.Dropdown(
                        id="location-dropdown",
                        options=[{"label": j,"value": i} for i, j in select_columns.items()],
                        value="casosNovos"
                    ),
                    dcc.Graph(id="line-graph", figure=fig2)
                ])
            ], md=5, style={"padding": "20px", "height":"99.9vh", "background-color": "#242424"}),

            dbc.Col([
                dcc.Loading(id="loading-1", type="default",
                    children=[
                        dcc.Graph(id="choropleth-map", figure=fig, 
                            style={
                                "height": "99.9vh",
                                "margin_right": "10px"
                            })
                    ])
            ], md=7)        
        ], className="g-0"), # className="g-0" == no_gutters
    ], fluid=True
)

# Interactivity
@app.callback(
    [
        Output("recovered-cases-text", "children"),
        Output("in-monitoring-text", "children"),
        Output("total-confirmed_cases-text", "children"),
        Output("new-cases-on-date-text", "children"),
        Output("confirmed-deaths-text", "children"),
        Output("deaths-on-date-text", "children")
    ],
    [
        Input("date-picker", "date"),
        Input("location-button", "children")
    ]
)
def display_status(date, location):
    if location.upper() == "BRAZIL":
        df_data_on_date = df_brazil[df_brazil["data"] == date]
    else:
        df_data_on_date = df_states[(df_states["estado"] == location) & (df_states["data"] == date)] 

    recuperados_novos = "-" if df_data_on_date["Recuperadosnovos"].isna().values[0] else f'{int(df_data_on_date["Recuperadosnovos"].values[0]):,}'.replace(",", ".") 
    acompanhamentos_novos = "-" if df_data_on_date["emAcompanhamentoNovos"].isna().values[0]  else f'{int(df_data_on_date["emAcompanhamentoNovos"].values[0]):,}'.replace(",", ".") 
    casos_acumulados = "-" if df_data_on_date["casosAcumulado"].isna().values[0]  else f'{int(df_data_on_date["casosAcumulado"].values[0]):,}'.replace(",", ".") 
    casos_novos = "-" if df_data_on_date["casosNovos"].isna().values[0]  else f'{int(df_data_on_date["casosNovos"].values[0]):,}'.replace(",", ".") 
    obitos_acumulado = "-" if df_data_on_date["obitosAcumulado"].isna().values[0]  else f'{int(df_data_on_date["obitosAcumulado"].values[0]):,}'.replace(",", ".") 
    obitos_novos = "-" if df_data_on_date["obitosNovos"].isna().values[0]  else f'{int(df_data_on_date["obitosNovos"].values[0]):,}'.replace(",", ".") 

    return (
            recuperados_novos, 
            acompanhamentos_novos, 
            casos_acumulados, 
            casos_novos, 
            obitos_acumulado, 
            obitos_novos,
            )

@app.callback(
    Output("line-graph", "figure"),
    [
        Input("location-dropdown", "value"),
        Input("location-button", "children")
    ]
)
def plot_line_graph(plot_type, location):
    if location.upper() == "BRAZIL":
        df_data_on_location = df_brazil.copy()
    else:
        df_data_on_location = df_states[df_states["estado"] == location]

    fig2 = render_graph(plot_type, df_data_on_location)
    return fig2

@app.callback(
    Output("choropleth-map", "figure"), 
    [Input("date-picker", "date")]
)
def plot_map(date):
    df_data_on_states = df_states[df_states["data"] == date]
    fig = render_map(df_data_on_states)
    return fig

@app.callback(
    Output("location-button", "children"),
    [
        Input("choropleth-map", "clickData"),
        Input("location-button", "n_clicks")
    ]
)
def update_location(click_data, n_clicks):
    changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if click_data is not None and changed_id != "location-button.n_clicks":
        state = click_data["points"][0]["location"]
        return "{}".format(state)
    else:
        return "BRAZIL"

if __name__ == "__main__":
    app.run_server(debug=True)
