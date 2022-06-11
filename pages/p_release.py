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

application = 'flask'
release = '0.3.0'

release_data = pd.read_csv(os.path.join(settings.output_dir, application, 'tree_'+release+'.csv'))

release_data_01 = pd.read_csv(os.path.join(settings.output_dir, application, 'tree_0.3.0.csv'))
#release_data_01 = release_data_01.iloc[:-1][release_data_01['folder'] == True]
release_data_01 = release_data_01.loc[release_data_01['folder'] == True]
release_data_02 = pd.read_csv(os.path.join(settings.output_dir, application, 'tree_1.0.3.csv'))
#release_data_02 = release_data_02.iloc[:-1][release_data_02['folder'] == True]
release_data_02 = release_data_02.loc[release_data_02['folder'] == True]

merged = pd.merge(release_data_01, release_data_02, on = ['hash_id', 'hash_parent', 'name'], how = 'outer')#.fillna(0)

#merged.assign(**{'name_x': merged['name_x'].fillna(merged['name_y'])})
#mergednew = merged.assign(**{'name_x': merged['name_x'].mask(lambda x: x == 'NaN', merged['name_y'])})

merged.to_csv(os.path.join(settings.output_dir, application, 'temp_' + application + '.csv'), index = False)

source_folders = release_data.loc[release_data['folder'] == True].astype({'hash_id': 'string', 'hash_parent': 'string'})

def create_node_chart(val_1, val_2):
	if(val_1 != val_1 and val_2 != val_2):
		return "data:image/svg+xml;utf8,%253csvg%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%20viewBox%3D%270%200%2032%2032%27%20width%3D%2732%27%20height%3D%2732%27%253e%253cpath%20fill%3D%27%2523ddd%27%20d%3D%27m0%200h16v32h16V16H0z%27%20/%253e%253c/svg%253e"
	#return "data:image/svg+xml;utf8,"
	else:
		chart = px.bar(
			x=[val_1, val_2],
			y=['1', '2'],
			orientation='h'
		)

	img_svg = chart.to_image(format='svg').decode()

	img_svg2 = quote(img_svg)
	datauri = "data:image/svg+xml;utf8," + img_svg2
	return datauri


def graph_elements(source_folders):
	max_num_files_direct = source_folders[['num_files_direct_x', 'num_files_direct_y']].max().max()

	node_dict = (
		source_folders[['hash_id', 'name', 'num_files_direct_x', 'num_files_direct_y']]
		#.fillna('0')
		.rename(columns={'hash_id': 'id', 'name': 'label'})
		.to_dict('records')
	)

	edge_dict = (
			#source_folders.iloc[:-1][['hash_parent', 'hash_id']]
		source_folders[['hash_parent', 'hash_id']]
		.rename(columns={'hash_parent': 'source', 'hash_id': 'target'})
		.to_dict('records')
	)

	# Create nodes and edges.
	graph_elements = []

	for node in node_dict:
		uri = create_node_chart(node['num_files_direct_x'], node['num_files_direct_y'])
		node['uri'] = uri
		graph_elements.append({'data': node})
	for edge in edge_dict:
		graph_elements.append({'data': edge})
		#print(edge)
	
	return graph_elements



network_graph = cyto.Cytoscape(
	id = 'nwgraph',
	layout = {
		'name': 'dagre',
		#'name': 'breadthfirst',
	},
	style = {'width': '1000px', 'height': '1000px'},
	elements = graph_elements(merged),
	stylesheet = [
		{
			'selector': 'node',
			'style': {
				'label': 'data(label)',
				#'label': 'data(label)',
				'shape': 'rectangle',
				'background-image': 'data(uri)',
				'background-fit': 'cover',
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
	#dcc.Graph(id='test', figure=netbartest),
	#html.Div([nettest]),
	#app_dropdown,
	#release_dropdown_group,
	#submit_button,
	html.Div(network_graph)
])
