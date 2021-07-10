import dash
import json
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


def load_cleaned_data():
    df = pd.read_csv("data/sales_data.csv", parse_dates=True)

    df["Sales"] = df["Sales"].map(lambda x: float(x[1:]))

    df["Date"] = pd.to_datetime(df["Date"])

    return df


df = load_cleaned_data()

minimum_date = min(df["Date"])

maximum_date = max(df["Date"])


app.layout = html.Div(
    [
        html.Div(
            html.H2("Colored Paper Sales Analytics Dashboard"),
            style={
                "display": "flex",
                "justifyContent": "center",
            },
        ),
        html.Div(
            [
                dcc.DatePickerRange(
                    id="date-picker-range",
                    min_date_allowed=minimum_date,
                    max_date_allowed=maximum_date,
                    initial_visible_month=minimum_date,
                    start_date=minimum_date,
                    end_date=maximum_date,
                ),
            ],
            style={
                "display": "flex",
                "justifyContent": "center",
            },
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H2("Percentage of Total Units Sold By Region"),
                        html.H4(id="unit_sales_total"),
                        dcc.Graph(id="unit_sales"),
                    ],
                    className="six columns",
                ),
                html.Div(
                    [
                        html.H3("Color Sold by Region"),
                        dcc.Dropdown(
                            id="selected_region",
                            options=[
                                {"value": x, "label": x} for x in df["Region"].unique()
                            ],
                            value=df["Region"].unique()[0],
                            clearable=False,
                        ),
                        dcc.Graph(id="color_sales"),
                    ],
                    className="six columns",
                ),
            ],
            className="row",
        ),
        html.Div([html.H2("Total Regional Sales"), dcc.Graph(id="sales_graph")]),
        dcc.Store(id="data_filtered_by_dates"),
    ]
)


@app.callback(
    Output("data_filtered_by_dates", "data"),
    [
        dash.dependencies.Input("date-picker-range", "start_date"),
        dash.dependencies.Input("date-picker-range", "end_date"),
    ],
)
def filter_by_dates(start_date, end_date):
    within_dates = df[df["Date"].between(start_date, end_date)]

    return within_dates.to_json()


@app.callback(Output("sales_graph", "figure"), Input("data_filtered_by_dates", "data"))
def update_figure(data):
    within_dates = pd.read_json(data)

    df_sales_by_region = within_dates.groupby("Region", as_index=False)["Sales"].sum()

    fig = px.bar(df_sales_by_region, x="Sales", y="Region", orientation="h")

    fig.update_xaxes(tickprefix="$")
    fig.update_layout(transition_duration=300)

    return fig


@app.callback(
    Output("unit_sales_total", "children"), Input("data_filtered_by_dates", "data")
)
def update_total_unit_sales(data):

    within_dates = pd.read_json(data)

    total_units_sold = within_dates["Units"].sum()
    return f"{total_units_sold}  Units Sold in Total Over this Time Period"


@app.callback(Output("unit_sales", "figure"), Input("data_filtered_by_dates", "data"))
def update_unit_sales(data):

    within_dates = pd.read_json(data)

    df_sales_by_region = within_dates.groupby("Region", as_index=False)["Units"].sum()

    fig = px.pie(df_sales_by_region, names="Region", values="Units")
    fig.update_layout(transition_duration=300)

    return fig


@app.callback(
    Output("color_sales", "figure"),
    [
        Input("data_filtered_by_dates", "data"),
        Input("selected_region", "value"),
    ],
)
def color_sales_by_region(data, selected_region):
    within_dates = pd.read_json(data)
    filtered_by_region = within_dates[within_dates["Region"] == selected_region]
    df_sales_by_region = filtered_by_region.groupby("Color", as_index=False)[
        "Units"
    ].sum()

    fig = px.bar(df_sales_by_region, x="Color", y="Units")
    fig.update_layout(transition_duration=300)

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
