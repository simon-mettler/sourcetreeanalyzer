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

application = 'calibre'
release = '3.0.0'
mode = 'num_files'

release_data = pd.read_csv(os.path.join(settings.output_dir, application, 'tree_'+release+'.csv'))

release_data_01 = pd.read_csv(os.path.join(settings.output_dir, application, 'tree_2.85.1.csv'))
#release_data_01 = release_data_01.iloc[:-1][release_data_01['folder'] == True]
release_data_01 = release_data_01.loc[release_data_01['folder'] == True]
release_data_02 = pd.read_csv(os.path.join(settings.output_dir, application, 'tree_3.0.0.csv'))
#release_data_02 = release_data_02.iloc[:-1][release_data_02['folder'] == True]
release_data_02 = release_data_02.loc[release_data_02['folder'] == True]

merged = pd.merge(release_data_01, release_data_02, on = ['id', 'parent', 'name'], how = 'outer')#.fillna(0)

#merged.to_csv(os.path.join(settings.output_dir, application, 'temp_' + application + '.csv'), index = False)

source_folders = release_data.loc[release_data['folder'] == True].astype({'id': 'string', 'parent': 'string'})


def create_node_chart(val_1, val_2, range_max):

	if(val_1 > 0 or val_2 > 0):

		"""
		chart = px.funnel_area(names=['a', 'b'], values=[4,6])
		"""
		chart = px.bar(
			x=[val_2, val_1],
			y=['2', '1'],
			orientation='h',
			color=["red", "goldenrod"], color_discrete_map="identity"
		)
		#chart.update_xaxes(range = [0, range_max])
		chart.update_layout(
			plot_bgcolor = 'rgb(222,222,222)',
			paper_bgcolor = 'rgb(222,222,222)',
			bargap = 0,
		)
		chart.update_xaxes(visible=False)


		img_svg = chart.to_image(format='svg').decode()

		img_svg2 = quote(img_svg)
		datauri = "data:image/svg+xml;utf8," + img_svg2
		return datauri
	else:
		return "data:image/svg+xml;utf8,"


def graph_elements(source_folders):

	max_num_files = source_folders[[mode + '_x', mode + '_y']].max().max()

	node_dict = (
		source_folders[['id', 'name', mode+'_x', mode+'_y']]
		#.fillna('0')
		.rename(columns={'name': 'label'})
		.to_dict('records')
	)

	edge_dict = (
			#source_folders.iloc[:-1][['hash_parent', 'hash_id']]
		source_folders[['parent', 'id']]
		.rename(columns={'parent': 'source', 'id': 'target'})
		.to_dict('records')
	)

	# Create nodes and edges.
	graph_elements = []

	for node in node_dict:
		uri = create_node_chart(node[mode+'_x'], node[mode + '_y'], max_num_files)
		node['uri'] = uri
		graph_elements.append({'data': node})
		print('create node')
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
	style = {'width': '100%', 'height': '1000px'},
	elements = graph_elements(merged),
	stylesheet = [
		{
			'selector': 'node',
			'style': {
				'label': 'data(label)',
				#'label': 'data(label)',
				'shape': 'rectangle',
				'background-image': 'data(uri)',
				'background-fit': 'contain',
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


layout = dbc.Container([
	html.H1('', id = 'testtitel'),
	#app_dropdown,
	#release_dropdown_group,
	#submit_button,
	html.Div(network_graph)
])
