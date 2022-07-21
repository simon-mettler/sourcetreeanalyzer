from dash import Dash, html, dcc, dash_table, callback, Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import pandas as pd
import os
import settings
from base64 import b64encode
from urllib.parse import quote


# Gets list of all applications.
applications = sorted(os.listdir(settings.output_dir))


# Page elements

# Creates options for application dropdown.
app_dropdown_options = [] 

for app in applications:
	single_option = {
		"label": app,
		"value": app
	}
	app_dropdown_options.append(single_option)

# Creates application dropdown element.
app_dropdown = html.Div(
	[
		dbc.Label('Application', html_for='dropdown-application'),
		dcc.Dropdown(
			id = 'dropdown-application',
			options = app_dropdown_options,
		),
	],
	className = 'mb-3',
)

# Creates release dropdown element.
release_dropdown = html.Div(
	[
		dbc.Label('Release', html_for='dropdown-release'),
		dcc.Dropdown(
			id = 'dropdown-release',
			options = [],
		),
	],
	className = 'mb-3',
)

# Creates submit dropdown element.
submit_button = dbc.Button(
	'Submit', id='submit-button', n_clicks = 0
)


def graph_elements(source_folders):
	# Returns a dict containing graph nodes and edges from folder structure.
	# Used to populate cytoscape graph.
	# Param 'source_folders': dataframe containing folders id, name, parent and num of files.

	# Gets all nodes (folders).
	node_dict = (
		source_folders[['id', 'name', 'num_files_direct']]#.astype(str)
		.fillna(0)
		.rename(columns={'name': 'label'})
		.to_dict('records')
	)

	# Gets all edges (parent/child relationship).
	edge_dict = (
		source_folders.iloc[:-1][['parent', 'id']]
		.rename(columns={'parent': 'source', 'id': 'target'})
		.to_dict('records')
	)

	# Adds nodes and edges to graph_elements dict.
	graph_elements = []
	for node in node_dict:
		graph_elements.append({'data': node})
	for edge in edge_dict:
		graph_elements.append({'data': edge})
	
	return graph_elements


def create_network_graph(source_folders):
	# Returns cytoscape network graph als plotly figure element.
	# Param 'source_folders': dataframe containing folders id, name, parent and num of files.

	num_files_max = source_folders['num_files_direct'].max()

	fig = cyto.Cytoscape(
		layout = {
			'name': 'dagre',
		},
		style = {'width': '100%', 'height': '1000px'},
		elements = graph_elements(source_folders),
		stylesheet = [
			{
				'selector': 'node',
				'style': {
					'label': 'data(label)',
					'shape': 'rectangle',
					'border-width': '1px',
					'border-color': 'black',
					'background-color': f"mapData(num_files_direct, 0, {num_files_max}, white, red)",
				}
			},
			{
				'selector': 'node:selected',
				'style': {
					'background-color': 'red',
				}
			},
			{
				'selector': 'edge',
				'style': {
					'width': '2px',
					'line-color': 'rgb(219,219,219)',
				}
			}
		]
	)
	return fig 


# Updates release dropdown options based on selected application.
@callback(
	Output('dropdown-release', 'options'),
	Input('dropdown-application', 'value'),
	prevent_initial_call = True
)
def update_release_options(app):
	# Returns all releases from selected application.
	# Param 'app': sring, selected application

	# Gets all releases from selected app.
	releases = pd.read_csv(os.path.join(settings.output_dir, app, 'stats_'+app+'.csv'))
	releases = releases['release'].unique().tolist()
	release_dropdown_options = []

	for release in releases:
		single_option = {
			"label": release,
			"value": release 
		}
		release_dropdown_options.append(single_option)

	return release_dropdown_options


# Updates network graph based on selected app and release.
@callback(
	Output('network-graph', 'children'),
	Input('submit-button', 'n_clicks'),
	State('dropdown-application', 'value'),
	State('dropdown-release', 'value'),
	prevent_initial_call = True
)
def update_graph(n_clicks, app, release):
	# Returns network graph figure.
	# Param 'app': string, selected application 
	# Param 'release': string, selected release

	release_data = pd.read_csv(os.path.join(settings.output_dir, app, 'tree_'+release+'.csv'))
	source_folders = release_data.loc[release_data['folder'] == True].astype({'id': 'string', 'parent': 'string'})

	return create_network_graph(source_folders)


# Creates dash layout.
layout = dbc.Container([
	html.H1('', id = 'testtitel'),
	app_dropdown,
	release_dropdown,
	submit_button,
	html.Div('', id = 'network-graph')
])
