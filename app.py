import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from datetime import date, datetime

import pandas as pd


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

df = pd.read_csv("data/sales_data.csv", parse_dates=True)

df["Sales"] = df["Sales"].map(lambda x: float(x[1:]))

df["Date"] = pd.to_datetime(df["Date"])

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
                "verticalAlign": "center",
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
    ]
)


@app.callback(
    Output("sales_graph", "figure"),
    [
        dash.dependencies.Input("date-picker-range", "start_date"),
        dash.dependencies.Input("date-picker-range", "end_date"),
    ],
)
def update_figure(start_date, end_date):
    #     filtered_df = df[df.year == selected_year]
    within_dates = df[df["Date"].between(start_date, end_date)]

    df_sales_by_region = within_dates.groupby("Region", as_index=False)["Sales"].sum()

    fig = px.bar(df_sales_by_region, x="Sales", y="Region", orientation="h")

    fig.update_xaxes(tickprefix="$")
    fig.update_layout(transition_duration=300)

    return fig


@app.callback(
    Output("unit_sales_total", "children"),
    [
        dash.dependencies.Input("date-picker-range", "start_date"),
        dash.dependencies.Input("date-picker-range", "end_date"),
    ],
)
def update_total_unit_sales(start_date, end_date):
    within_dates = df[df["Date"].between(start_date, end_date)]

    total_units_sold = within_dates["Units"].sum()
    return f"{total_units_sold}  Units Sold in Total Over this Time Period"


@app.callback(
    Output("unit_sales", "figure"),
    [
        dash.dependencies.Input("date-picker-range", "start_date"),
        dash.dependencies.Input("date-picker-range", "end_date"),
    ],
)
def update_unit_sales(start_date, end_date):
    #     filtered_df = df[df.year == selected_year]
    within_dates = df[df["Date"].between(start_date, end_date)]

    df_sales_by_region = within_dates.groupby("Region", as_index=False)["Units"].sum()

    fig = px.pie(df_sales_by_region, names="Region", values="Units")
    fig.update_layout(transition_duration=300)

    return fig


@app.callback(
    Output("color_sales", "figure"),
    [
        dash.dependencies.Input("date-picker-range", "start_date"),
        dash.dependencies.Input("date-picker-range", "end_date"),
        dash.dependencies.Input("selected_region", "value"),
    ],
)
def color_sales_by_region(start_date, end_date, value):
    within_dates = df[df["Date"].between(start_date, end_date)]
    filtered_by_region = within_dates[within_dates["Region"] == value]
    df_sales_by_region = filtered_by_region.groupby("Color", as_index=False)[
        "Units"
    ].sum()

    fig = px.bar(df_sales_by_region, x="Color", y="Units")
    fig.update_layout(transition_duration=300)

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
    print()
