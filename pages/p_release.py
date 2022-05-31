from dash import Dash, html, dcc, dash_table, callback, Input, Output
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

# Application Dropdown
app_dropdown_options = [] 

for app in applications:
	single_option = {
		"label": app,
		"value": app
	}
	app_dropdown_options.append(single_option)

app_dropdown = html.Div(
	[
		dbc.Label('Application', html_for='dropdown'),
		dcc.Dropdown(
			id = 'dropdown_application',
			options = app_dropdown_options,
		),
	],
	className = 'mb-3',
)


# Release dropdown group
release_dropdown_group = html.Div(
	[
		dbc.Label('Release 1', html_for='dropdown_release1'),
		dcc.Dropdown(
			id = 'dropdown_release1',
			options = app_dropdown_options,
		),
		dbc.Label('Release 2', html_for='dropdown_release2'),
		dcc.Dropdown(
			id = 'dropdown_release2',
			options = app_dropdown_options,
		),
	],
	className = 'mb-3',
)

application = 'skywalking'
release = '2.1-2017'

release_data = pd.read_csv(os.path.join(settings.output_dir, application, 'tree_'+release+'.csv'))

source_folders = release_data.loc[release_data['folder'] == True].astype({'hash_id': 'string', 'hash_parent': 'string'})


node_dict = (
	source_folders[['hash_id', 'name']]
	#.fillna('0')
	.rename(columns={'hash_id': 'id', 'name': 'label'})
	.to_dict('records')
)


edge_dict = (
	source_folders.iloc[:-1][['hash_parent', 'hash_id']]
	.rename(columns={'hash_parent': 'source', 'hash_id': 'target'})
	.to_dict('records')
)

# Create nodes and edges.
graph_elements = []

for node in node_dict:
	graph_elements.append({'data': node})
for edge in edge_dict:
	graph_elements.append({'data': edge})

#graph_elements.append({'data': {'id': '0', 'label': 'root'}})


network_graph = cyto.Cytoscape(
	id = 'nwgraph',
	layout = {
		'name': 'dagre',
		#'name': 'breadthfirst',
	},
	style = {'width': '1000px', 'height': '1000px'},
	elements = graph_elements,
	stylesheet = [
		{
			'selector': 'node',
			'style': {
				'label': 'data(label)',
				'shape': 'rectangle',
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

submit_button = dbc.Button(
	'Submit', id='submit-button', n_clicks = 0
)

"""
@callback(
	Output('folder-tree-graph', 'figure'),
	Input('submit-button', 'n_clicks'),
	State('dropdown_application', 'value')
	State('dropdown_release', 'value')
)
def update_folder_tree(app, release):
"""


netbartest = px.bar(
	x=[20, 14, 23],
	y=['a', 'b', 'c'],
	orientation='h'
)


def datauri():
	img_svg = netbartest.to_image(format='svg').decode()
	img_svg2 = quote(img_svg)
	datauri = "data:image/svg+xml;utf8," + img_svg2
	return datauri

nettest = cyto.Cytoscape(

	id = 'nettest',
	layout = {
		'name': 'dagre',
		#'name': 'breadthfirst',
	},
	style = {'width': '1000px', 'height': '1000px'},
	elements =[
		{'data': {'id': 'A', 'uri': datauri()}},
		{'data': {'id': 'B', 'uri': datauri()}},
    {'data': {'source': 'A', 'target': 'B'}},
	],
	stylesheet = [
		{
			'selector': 'node',
			'style': {
				#'label': 'data(label)',
				'shape': 'rectangle',
				'background-image': 'data(uri)',
				#'width': 'data(num_files_direct)',
				'background-fit': 'cover',
			}
		},
	]
)


layout = dbc.Container([
	html.H1('', id = 'testtitel'),
	dcc.Graph(id='test', figure=netbartest),
	html.Div([nettest]),
	#app_dropdown,
	#release_dropdown_group,
	#submit_button,
	html.Div(network_graph)
])
