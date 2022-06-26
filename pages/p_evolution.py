from dash import Dash, html, dcc, dash_table, callback, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import os
import settings


# Load statistics from output folder as dataframe.
applications = sorted(os.listdir(settings.output_dir))

release_stats = {a:'' for a in applications }
files_per_level = {a:'' for a in applications } 


for application in applications:

	files_per_level[application] = pd.read_csv(
		os.path.join(settings.output_dir, application, 'files-per-level_'+application+'.csv'))

	df = pd.read_csv(
		os.path.join(settings.output_dir, application, 'stats_'+application+'.csv'))

	if application in settings.order_by_name:
		df.sort_values(by = 'release', inplace = True)

	release_stats[application] = df


# Stats

# Avg tree size
#def get_avg_tree_size(data):
#	return round(data['tree_size'].mean(), 2)

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


config_graph = {
	'displaylogo': False,
	'toImageButtonOptions': {'format': 'svg'},
}

def create_fig_test(data): 
	fig = px.bar(
		data,
		title = 'test',
		x = 'release', 
		y = 'growth_num_files_pct', 
		template = 'simple_white',
		labels = {
			'release': 'Release',
			'growth_num_files_pct': 'Metric',
		},
	)
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
			'release_size_bytes': 'Size (Bytes)',
		},
	)
	return fig



def create_fig_total_files(data): 
	fig = px.bar(
		data,
		title = 'Total number of files',
		x = 'release', 
		y = 'num_files', 
		template = 'simple_white',
		labels = {
			'release': 'Release',
			'num_files': 'Number of files',
		},
	)
	return fig


def create_fig_files_per_level(data):
	fig = px.line(
		data,
		title = 'Number of files per level', 
		x = 'release', 
		y = 'num_files', 
		color = 'level', 
		markers = True,
		labels = {
			'release': 'Release',
			'num_files': 'Number of files',
			'level': 'Tree level',
		},
	)

	# Set category order after grouping.
	unique_releases = data['release'].unique().tolist()
	fig.update_xaxes(
		categoryorder = 'array', 
		categoryarray = unique_releases, 
		range = [0, len(data['release'].unique())-1]
	) 
	
	return fig


def create_fig_avg_file_size_bytes(data):
	fig = px.line(
		data,
		title = 'Average file size in Bytes',
		x = 'release', 
		y = 'avg_file_size_bytes', 
		labels = {
			'release': 'Release',
			'avg_file_size_bytes': 'Avg. file size',
		},
	)
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
	return fig

def create_fig_avg_folder_size(data):
	fig = px.bar(
		data,
		title = 'Average source folder size (number of files in folder)',
		x = 'release', 
		y = 'avg_source_folder_size_num_files', 
		labels = {
			'release': 'Release',
			'avg_source_folder_size_num_files': 'Avg. folder size (num. of files in folder)',
		},
	) 
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
	Output('fig-total-files', 'figure'),
	Output('fig-release-size-bytes', 'figure'),
	#Output('fig-tree-size', 'figure'),
	#Output('fig-metric-source-folder', 'figure'),
	Output('fig-files-per-level', 'figure'),
	Output('fig-avg-file-size-bytes', 'figure'),
	Output('fig-test', 'figure'),
	Output('fig-avg-folder-size', 'figure'),
	Output('fig-max-tree-level', 'figure'),
	Input('dropdown_application', 'value'), 
	prevent_initial_call = True
)
def update_figure(selected_value):
	if selected_value:
		data_release = release_stats[selected_value]
		data_fpl = files_per_level[selected_value]
		return (
			create_fig_total_files(data_release), 
			#create_fig_metric_source_folder(data_release), 
			#create_fig_tree_size(data_release), 
			create_fig_files_per_level(data_fpl), 
			create_fig_release_size_bytes(data_release), 
			create_fig_avg_file_size_bytes(data_release),
			create_fig_test(data_release),
			create_fig_avg_folder_size(data_release),
			create_fig_max_tree_level(data_release),
		)


# Dash page layout.
layout = dbc.Container([
	html.H1('', id = 'page-title'),
	app_dropdown,
	dcc.Graph(id='fig-total-files', config=config_graph),
	html.Div(dbc.Accordion([
		dbc.AccordionItem([
			dcc.Graph(id='fig-test'),
		], title='Show Growth')
	],start_collapsed=True)),
	#dcc.Graph(id='fig-metric-source-folder'),
	#dcc.Graph(id='fig-tree-size'),
	dcc.Graph(id='fig-files-per-level'), 
	dcc.Graph(id='fig-release-size-bytes'), 
	dcc.Graph(id='fig-avg-file-size-bytes'),
	dcc.Graph(id='fig-avg-folder-size'),
	dcc.Graph(id='fig-max-tree-level')
])
