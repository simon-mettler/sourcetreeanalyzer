from dash import Dash, html, dcc, dash_table, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import folderstats
import settings
import os

app = Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])

current_application = 'caffeine'

#full_release_data = pd.read_csv('output/zipkin/tree_1.2.1.csv')


applications = sorted(os.listdir(settings.output_dir))

release_stats = {a:'' for a in applications }
files_per_level = {a:'' for a in applications } 

for application in applications:
	release_stats[application] = pd.read_csv(os.path.join(settings.output_dir, application, 'stats_'+application+'.csv'))
	files_per_level[application] = pd.read_csv(os.path.join(settings.output_dir, application, 'files-per-level_'+application+'.csv'))

#print(files_per_level[current_application].groupby('release'))

fig_total_files = px.bar(
	release_stats[current_application], 
	title = 'total number of files',
	x = 'release', 
	y = 'total_files', 
)

fig_avg_file_size = px.bar(
	release_stats[current_application], 
	title = 'avg file size (KB)',
	x = 'release', 
	y = 'avg_file_size', 
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
	y = 'avg_folder_size', 
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
	title =  '[testing] vertical growth (%)',
	x = 'release', 
	y = 'vertical_growth', 
)

fig_horizontal_growth = px.bar(
	release_stats[current_application], 
	x = 'release', 
	y = 'horizontal_growth', 
	title =  '[testing] horizontal growth (%)'
)


def to_kb(b):
	kb = b/1024
	return round(kb, 1)

navbar = dbc.NavbarSimple(
	[
		dbc.NavItem( dbc.NavLink('Release Summary', href='/release-summary') ),
		dbc.NavItem( dbc.NavLink('About', href='#') ),
	],
	brand = 'SourceTreeAnalyzer',
	brand_href = '/'
)

app.layout = html.Div([
	dcc.Location(id = 'url', refresh = False),
	navbar,
	html.Div(id = 'page-content')
])

p_index = dbc.Container([
	html.H1('Index page'),
])

p_releas_summary = dbc.Container([
	html.H1('Testing (Blender 2.2.x - 3.1.x)'),
	dcc.Graph( id='total_files', figure = fig_total_files),
	dcc.Graph( id='avg_file_size', figure = fig_avg_file_size),
	dcc.Graph( id='avg_folder_size', figure = fig_avg_folder_size),
	dcc.Graph( id='files_per_level', figure = fig_files_per_level),
	dcc.Graph( id='max_tree_level', figure = fig_max_tree_level),
	dcc.Graph( id='tree_width', figure = fig_tree_width),
	dcc.Graph( id='tree_height', figure = fig_tree_height),
	dcc.Graph( id='horizontal_growth', figure = fig_horizontal_growth),
	dcc.Graph( id='vertical_growth', figure = fig_vertical_growth),
])

@callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
	if pathname == '/release-summary':
		return p_releas_summary
	else:
		return p_index


if __name__ == '__main__':
	app.run_server(debug=True)
