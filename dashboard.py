from dash import Dash, html, dcc, dash_table, callback, Input, Output
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import plotly.express as px
import pandas as pd
import folderstats
import settings
import os
from pages import p_evolution, p_index, p_release, p_datatable #, p_release2

cyto.load_extra_layouts()

app = Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions=True



navbar = dbc.NavbarSimple(
	[
		dbc.NavItem( dbc.NavLink('Evolution', href='/evolution') ),
		dbc.NavItem( dbc.NavLink('Release', href='/release') ),
		dbc.NavItem( dbc.NavLink('Datatable', href='/datatable') ),
		dbc.NavItem( dbc.NavLink('About', href='#') ),
	],
	brand = 'SourceTreeAnalyzer',
	brand_href = '/'
)


app.layout= html.Div([
	dcc.Location(id = 'url', refresh = False),
	navbar,
	html.Div(id = 'page-content')
])


@callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
	if pathname == '/evolution':
		return p_evolution.layout
	elif pathname == '/release':
		return p_release.layout
	#elif pathname == '/release2':
		#return p_release2.layout
	elif pathname == '/datatable':
		return p_datatable.layout
	else:
		return p_index.layout




if __name__ == '__main__':
	app.run_server(debug=True)
