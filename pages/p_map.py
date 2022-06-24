from dash import Dash, html, dcc, dash_table, callback, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import pandas as pd
import os
import settings
from base64 import b64encode
from urllib.parse import quote
from functools import reduce

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

application = 'qbittorrent'
dfs = []
matrix = []

prefixed = [filename for filename in sorted(os.listdir(os.path.join(settings.output_dir, application))) if filename.startswith("tree_")]


for file in prefixed:
	df = pd.read_csv(os.path.join(settings.output_dir, application, file))
	#dfs.append(df['id','num_files_direct'])
	dfs.append(df.loc[(df['folder'] == True) & (df['num_files_direct'] > 0)][['id','num_files_direct', 'level']])

matrixdf = reduce(lambda df1,df2: pd.merge(df1,df2,on=['id', 'level'], how = 'outer'), dfs)

matrixdff = matrixdf.iloc[:,2:-1].fillna(0).values.tolist()
#matrixdff = matrixdf.iloc[:,2:-1].fillna(0).sort_values(by='level').values.tolist()
map_graph = px.imshow(matrixdff, aspect='auto')

#release = '0.2.0'

#release_data = pd.read_csv(os.path.join(settings.output_dir, application, 'tree_'+release+'.csv'))



"""
@callback(
	Output('folder-tree-graph', 'figure'),
	Input('dropdown_application', 'value')
)
def update_folder_tree(app):
"""


layout = dbc.Container([
	html.H1('', id = 'testtitel'),
	#app_dropdown,
	dcc.Graph(figure=map_graph)
])
