from dash import Dash, html, dcc, dash_table, callback, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import os
import settings

current_application = 'skywalking'

applications = sorted(os.listdir(settings.output_dir))


release_stats = {a:'' for a in applications }
files_per_level = {a:'' for a in applications } 

# Load statistics from output folder as dataframe.
for application in applications:
	release_stats[application] = pd.read_csv(os.path.join(settings.output_dir, application, 'stats_'+application+'.csv'))
	files_per_level[application] = pd.read_csv(os.path.join(settings.output_dir, application, 'files-per-level_'+application+'.csv'))


'''

fig_total_files = px.bar(
	release_stats[current_application], 
	title = 'total number of files',
	x = 'release', 
	y = 'total_files', 
)

'''

fig_avg_file_size = px.bar(
	release_stats[current_application], 
	title = 'avg file size (Bytes)',
	x = 'release', 
	y = 'avg_file_size_bytes', 
)

files_per_level[current_application]['level'] = files_per_level[current_application]['level'].astype(str)

fig_files_per_level = px.line(
	files_per_level[current_application], 
	title = 'num of files per level', 
	x = 'release', 
	y = 'num_files', 
	color = 'level', 
	markers = True,
)

fig_avg_folder_size = px.bar(
	release_stats[current_application], 
	title = 'avg folder size (num of files in folder)',
	x = 'release', 
	y = 'avg_source_folder_size_num_files', 
) 

fig_max_tree_level = px.line(
	release_stats[current_application], 
	title = 'max tree level',
	x = 'release', 
	y = 'max_tree_level', 
) 

fig_tree_width = px.line(
	release_stats[current_application], 
	title = '[testing] tree width? -> avg num of files per level',
	x = 'release', 
	y = 'avg_num_files_level',
)

fig_tree_height = px.line(
	release_stats[current_application], 
	title = '[testing] tree depth? -> avg depth from root to leaf folder',
	x = 'release', 
	y = 'avg_tree_level', 
)

fig_vertical_growth = px.bar(
	release_stats[current_application], 
	title =  '[testing] tree depth growth (%)',
	x = 'release', 
	y = 'growth_tree_depth_pct', 
)

fig_horizontal_growth = px.bar(
	release_stats[current_application], 
	title =  '[testing] tree width growth (%)',
	x = 'release', 
	y = 'growth_tree_width_pct', 
)

dropdown_options = [] 
for app in applications:
	single_option = {
		"label": app,
		"value": app
	}
	dropdown_options.append(single_option)


def create_fig_total_files(data): 
	# Creates bar chart showing the total number of files per release.
	fig = px.bar(
		data,
		title = 'total number of files',
		x = 'release', 
		y = 'num_files', 
	)
	return fig

app_dropdown = html.Div(
	[
		dbc.Label('Select Application', html_for='dropdown'),
		dcc.Dropdown(
			id = 'my-dropdown',
			options = dropdown_options,
			value = 'zipkin',
		),
	],
	className = 'mb-3',
)

# Dash page layout.
layout = dbc.Container([
	html.H1('', id = 'testtitel'),
	app_dropdown,
	dcc.Graph( id='total_files' ),
	dcc.Graph( id='avg_file_size', figure = fig_avg_file_size),
	dcc.Graph( id='avg_folder_size', figure = fig_avg_folder_size),
	dcc.Graph( id='files_per_level', figure = fig_files_per_level),
	dcc.Graph( id='max_tree_level', figure = fig_max_tree_level),
	dcc.Graph( id='tree_width', figure = fig_tree_width),
	dcc.Graph( id='tree_height', figure = fig_tree_height),
	dcc.Graph( id='horizontal_growth', figure = fig_horizontal_growth),
	dcc.Graph( id='vertical_growth', figure = fig_vertical_growth),
])


"""
Updates title based on selected application.

"""
@callback(
	Output('testtitel', 'children'),
	Input('my-dropdown', 'value')
)
def update_selected_app(input_value):
	return input_value


@callback(
	Output('total_files', 'figure'),
	Input('my-dropdown', 'value')
)
def update_figure(selected_value):
	if selected_value:
		data = release_stats[selected_value]
		return create_fig_total_files(data)
	else:
		return px.bar(
			[],
			title = 'Please select an application...'
		)
