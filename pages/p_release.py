from dash import Dash, html, dcc, dash_table, callback, Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import pandas as pd
import os
import settings
from base64 import b64encode
from urllib.parse import quote


applications = sorted(os.listdir(settings.output_dir))

# Page elements

# Application dropdown.
app_dropdown_options = [] 

for app in applications:
	single_option = {
		"label": app,
		"value": app
	}
	app_dropdown_options.append(single_option)

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

# Release dropdown.
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



submit_button = dbc.Button(
	'Submit', id='submit-button', n_clicks = 0
)



def graph_elements(source_folders):

	node_dict = (
		source_folders[['id', 'name']]
		.fillna('0')
		.rename(columns={'name': 'label'})
		.to_dict('records')
	)

	edge_dict = (
		source_folders.iloc[:-1][['parent', 'id']]
		.rename(columns={'parent': 'source', 'id': 'target'})
		.to_dict('records')
	)

	# Create nodes and edges.
	graph_elements = []

	for node in node_dict:
		graph_elements.append({'data': node})
	for edge in edge_dict:
		graph_elements.append({'data': edge})
	
	return graph_elements


def create_network_graph(source_folders):
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
					'background-color': 'rgb(222,222,222)',
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


# Update release dropdown options based on selected application.
@callback(
	Output('dropdown-release', 'options'),
	Input('dropdown-application', 'value'),
	prevent_initial_call = True
)
def update_release_options(app):
	print('1 callback')
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


@callback(
	Output('network-graph', 'children'),
	Input('submit-button', 'n_clicks'),
	State('dropdown-application', 'value'),
	State('dropdown-release', 'value'),
	prevent_initial_call = True
)
def update_graph(n_clicks, app, release):
	print(app, release)
	release_data = pd.read_csv(os.path.join(settings.output_dir, app, 'tree_'+release+'.csv'))
	source_folders = release_data.loc[release_data['folder'] == True].astype({'id': 'string', 'parent': 'string'})
	return create_network_graph(source_folders)


layout = dbc.Container([
	html.H1('', id = 'testtitel'),
	app_dropdown,
	release_dropdown,
	submit_button,
	html.Div('', id = 'network-graph')
])
