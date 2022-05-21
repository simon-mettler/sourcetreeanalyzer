from dash import Dash, html, dcc, dash_table, callback, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import pandas as pd
import os
import settings


application = 'caffeine'
release = '3.1.0'

release_data = pd.read_csv(os.path.join(settings.output_dir, application, 'tree_'+release+'.csv'))

source_folders = release_data.loc[ release_data['folder'] == True ].astype({'id': 'string', 'parent': 'string'})

node_dict = source_folders[['id', 'name']].rename(columns={'name': 'label'}).to_dict('records')
edge_dict = source_folders[['parent', 'id']].rename(columns={'parent': 'source', 'id': 'target'}).to_dict('records')

graph_elements = []

for node in node_dict:
	graph_elements.append({'data': node})

for edge in edge_dict:
	graph_elements.append({'data': edge})

graph_elements.append({'data': {'id': '0', 'label': 'root'}})
#sourcedig = dict(source_folders)


network_graph = cyto.Cytoscape(
	id = 'nwgraph',
	layout = {
		'name': 'dagre',
		'curve-style': 'taxi'
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
				#'curve-style': 'taxi',
			}
		}
	]
)

layout = dbc.Container([
	html.H1('', id = 'testtitel'),
	network_graph,
])

'''
	layout = {
		'name': 'breadthfirst',
		'roots': '[id = "0"]'
	},
'''
