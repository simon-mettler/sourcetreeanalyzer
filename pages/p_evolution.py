from dash import Dash, html, dcc, dash_table, callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import pandas as pd
import os
import settings


def to_kb(b):
	kb = b/1024
	return round(kb, 0)


# Gets all applications
applications = sorted(os.listdir(settings.output_dir))

# Prepare dict for statistics.
release_stats = {a:'' for a in applications }
files_per_level = {a:'' for a in applications } 


# Loads statistics and files per level for every application.
for application in applications:

	files_per_level[application] = pd.read_csv(
		os.path.join(settings.output_dir, application, 'files-per-level_'+application+'.csv'))

	stats = pd.read_csv(
		os.path.join(settings.output_dir, application, 'stats_'+application+'.csv'))

	# Orders releases by name if necessary.
	if application in settings.order_by_name:
		stats.sort_values(by = 'release', inplace = True)
		stats = stats.reset_index(drop=True)

	# Store statistics in release_stats dict.
	release_stats[application] = stats

	# Converts release size column from bytes to kilobytes.
	release_stats[application]['release_size_bytes'] = release_stats[application]['release_size_bytes'].apply(to_kb)
	#release_stats[application]['avg_file_size_bytes'] = release_stats[application]['avg_file_size_bytes'].apply(to_kb)



# Page elements

# Loads application dropdown options.
app_dropdown_options = [] 
for app in applications:
	single_option = {
		"label": app,
		"value": app
	}
	app_dropdown_options.append(single_option)

# Creates application dropdown html element.
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



### Create Graphs

# Global graph configs.
config_graph = {
	'displaylogo': False,
	'toImageButtonOptions': {'format': 'png'},
}


def create_fig_size_multiple_yaxis(data):
	fig = make_subplots(specs=[[{"secondary_y": True}]])
	fig.add_trace(
    go.Scatter(
			x = data['release'], 
			y = data['num_files'],
			name="Num. Files"),
    secondary_y=False,
	)

	fig.add_trace(
    go.Scatter(
			x = data['release'], 
			y = data['release_size_bytes'],
    	name="KB"),
    secondary_y=True,
	)
	fig.update_layout(template='none')
	fig.update_layout({ 'xaxis': {'type': 'category'}})

	return fig


def create_fig_growth_num_files(data): 
	fig = px.bar(
		data,
		title = 'test',
		x = 'release', 
		y = ['growth_num_files_pct', 'growth_size_bytes_pct'],
		barmode='group',
		template = 'simple_white',
		labels = {
			'release': 'Release',
			'growth_num_files_pct': 'Metric',
		},
	)
	fig.update_layout({ 'xaxis': {'type': 'category'}})
	return fig

def create_fig_growth_release_size(data): 
	fig = px.bar(
		data,
		title = 'test',
		x = 'release', 
		y = 'growth_size_bytes_pct', 
		template = 'simple_white',
		labels = {
			'release': 'Release',
			'growth_size_bytes_pct': 'Size',
		},
	)
	fig.update_layout({ 'xaxis': {'type': 'category'}})
	return fig

def create_fig_release_size_bytes(data): 
	fig = px.line(
		data,
		title = 'Release Size (Bytes)',
		x = 'release', 
		y = 'release_size_bytes', 
		template = 'none',
		labels = {
			'release': 'Release',
			'release_size_bytes': 'Size (KB)',
		},
	)
	fig.update_layout({ 'xaxis': {'type': 'category'}})
	return fig


def create_fig_total_files(data): 
	fig = px.line(
		data,
		title = 'Total number of files',
		x = 'release', 
		y = 'num_files', 
		template = 'none',
		labels = {
			'release': 'Release',
			'num_files': 'Number of files',
		},
	)

	fig.update_layout({ 'xaxis': {'type': 'category'}})

	return fig


def create_fig_files_per_level(data, application):
	if application not in settings.order_by_name:
		# Sorting values by mtime to ensure correct xaxis ordering because 
		# plotly falls back to alphabetical ordering after grouping
		data.sort_values(by = 'mtime', inplace = True)
		data = data.reset_index(drop=True)

	fig = px.line(
		data,
		title = 'Number of files per level', 
		x = 'release', 
		y = 'num_files', 
		color = 'level', 
		#markers = True,
		template = 'none',
		category_orders={'index': data.index[::-1]}, # Reorder xaxis.
		labels = {
			'release': 'Release',
			'num_files': 'Number of files',
			'level': 'Tree level',
		},
	)

	# Update xaxis range to remove left and right chart padding.
	fig.update_xaxes(type='category')
	fig.update_xaxes( range = [0, len(data['release'].unique())-1]	) 
	fig.update_traces(connectgaps=False)
	
	return fig


def create_fig_avg_file_size_bytes(data):
	fig = px.line(
		data,
		title = 'Average file size in Bytes',
		x = 'release', 
		y = 'avg_file_size_bytes', 
		template = 'none',
		labels = {
			'release': 'Release',
			'avg_file_size_bytes': 'Avg. file size',
		},
	)
	fig.update_layout({ 'xaxis': {'type': 'category'}})
	return fig

def create_fig_max_file_size_bytes(data):
	fig = px.line(
		data,
		title = 'Max file size in Bytes',
		x = 'release', 
		y = 'max_file_size_bytes', 
		labels = {
			'release': 'Release',
			'max_file_size_bytes': 'Max. file size',
		},
	)
	fig.update_layout({ 'xaxis': {'type': 'category'}})
	return fig

def create_fig_avg_folder_size(data):
	fig = px.bar(
		data,
		title = 'Average source folder size (number of files in folder)',
		x = 'release', 
		y = 'avg_source_folder_size_num_files', 
		template = 'none',
		labels = {
			'release': 'Release',
			'avg_source_folder_size_num_files': 'Avg. folder size (num. of files in folder)',
		},
	) 
	fig.update_layout({ 'xaxis': {'type': 'category'}})
	return fig

def create_fig_max_tree_level(data):
	fig = px.line(
		data,	
		title = 'Maximum tree level',
		x = 'release', 
		y = 'max_tree_level', 
		labels = {
			'release': 'Release',
			'max_tree_level': 'Maximum tree level',
		},
	) 
	fig.update_layout({ 'xaxis': {'type': 'category'}})
	return fig


# Callbacks

# Updates title based on selected application.
@callback(
	Output('page-title', 'children'),
	Input('dropdown_application', 'value'),
)
def update_selected_app(input_value):
	if input_value:
		return input_value
	else: 
		return 'Please select an application'


# Updates figures based on selected application.
@callback(
	Output('fig-size-multipe-yaxis', 'figure'),
	Output('fig-total-files', 'figure'),
	Output('fig-growth-num-files', 'figure'),
	Output('fig-release-size-bytes', 'figure'),
	#Output('fig-tree-size', 'figure'),
	#Output('fig-metric-source-folder', 'figure'),
	Output('fig-growth-release-size', 'figure'),
	Output('fig-avg-file-size-bytes', 'figure'),
	Output('fig-files-per-level', 'figure'),
	Output('fig-avg-folder-size', 'figure'),
	Output('fig-max-tree-level', 'figure'),
	Input('dropdown_application', 'value'), 
	prevent_initial_call = True
)
def update_figure(selected_value):
	if selected_value:
		data_release = release_stats[selected_value]
		data_fpl = files_per_level[selected_value]
		release_list = release_stats[selected_value]['release'].tolist()
		return (
			create_fig_size_multiple_yaxis(data_release), 
			create_fig_total_files(data_release), 
			create_fig_growth_num_files(data_release),
			create_fig_release_size_bytes(data_release), 
			create_fig_growth_release_size(data_release),
			create_fig_files_per_level(data_fpl, selected_value), 
			create_fig_avg_file_size_bytes(data_release),
			create_fig_avg_folder_size(data_release),
			create_fig_max_tree_level(data_release),
		)


# Dash page layout.
layout = dbc.Container([
	html.H1('', id = 'page-title'),
	app_dropdown,
	dcc.Graph(id='fig-size-multipe-yaxis'), 
	dcc.Graph(id='fig-total-files', config=config_graph),
	html.Div(dbc.Accordion([
		dbc.AccordionItem([
			dcc.Graph(id='fig-growth-num-files'),
		], title='Show Growth')
	],start_collapsed=True)),
	dcc.Graph(id='fig-release-size-bytes'), 
	html.Div(dbc.Accordion([
		dbc.AccordionItem([
			dcc.Graph(id='fig-growth-release-size'),
		], title='Show Growth')
	],start_collapsed=True)),
	dcc.Graph(id='fig-files-per-level'), 
	dcc.Graph(id='fig-avg-file-size-bytes'),
	dcc.Graph(id='fig-avg-folder-size'),
	dcc.Graph(id='fig-max-tree-level')
])
