from dash import Dash, html, dcc, dash_table, callback, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import pandas as pd
import os
import settings
from base64 import b64encode


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

application = 'zipkin'
release = '1.0.0'

release_data = pd.read_csv(os.path.join(settings.output_dir, application, 'tree_'+release+'.csv'))

source_folders = release_data.loc[release_data['folder'] == True].astype({'id': 'string', 'parent': 'string'})

node_dict = (
	source_folders[['id', 'name', 'num_files_direct']]
	.fillna(1)
	.rename(columns={'name': 'label'})
	.to_dict('records')
)

edge_dict = (
	source_folders[['parent', 'id']]
	.rename(columns={'parent': 'source', 'id': 'target'})
	.to_dict('records')
)

# Create nodes and edges.
graph_elements = []

for node in node_dict:
	graph_elements.append({'data': node})
for edge in edge_dict:
	graph_elements.append({'data': edge})

graph_elements.append({'data': {'id': '0', 'label': 'root'}})


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
				'width': 'data(num_files_direct)',
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
	img_bytes = netbartest.to_image(format='png')
	encoding = b64encode(img_bytes).decode()
	datauri = "data:image/png;base64," + encoding
	return datauri

print(datauri())

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
	app_dropdown,
	release_dropdown_group,
	submit_button,
	dcc.Graph(id='folder-tree-graph' ),
])
