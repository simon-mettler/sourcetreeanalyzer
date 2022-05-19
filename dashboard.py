from dash import Dash, html, dcc, dash_table, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import folderstats
import settings
import os
from pages import p_evolution, p_index


app = Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])


def to_kb(b):
	kb = b/1024
	return round(kb, 1)


navbar = dbc.NavbarSimple(
	[
		dbc.NavItem( dbc.NavLink('Release Summary', href='/evolution') ),
		dbc.NavItem( dbc.NavLink('About', href='#') ),
	],
	brand = 'SourceTreeAnalyzer',
	brand_href = '/'
)

app.layout = html.Div([
	dcc.Location(id = 'url', refresh = False),
	navbar,
	html.Div(id = 'page-content')
])


@callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
	if pathname == '/evolution':
		return p_evolution.layout
	else:
		return p_index.layout


if __name__ == '__main__':
	app.run_server(debug=True)
