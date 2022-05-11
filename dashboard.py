from dash import Dash, html, dcc, dash_table
import os
import plotly.express as px
import pandas as pd
import folderstats
import settings

app = Dash(__name__)

current_application = 'blender'

full_release_data = pd.read_csv('output/blender/tree_blender-2.90.0.csv')


applications = sorted(os.listdir(settings.output_dir))

release_stats = {a:'' for a in applications }
files_per_level = {a:'' for a in applications } 

for application in applications:
	release_stats[application] = pd.read_csv(os.path.join(settings.output_dir, application, 'stats_'+application+'.csv'))
	files_per_level[application] = pd.read_csv(os.path.join(settings.output_dir, application, 'files-per-level_'+application+'.csv'))

#print(files_per_level[current_application].groupby('release'))

fig_total_files = px.bar(release_stats[current_application], x = 'release', y = 'total_files', title = 'total number of files')
fig_avg_file_size = px.bar(release_stats[current_application], x = 'release', y = 'avg_file_size', title = 'avg file size (KB)')

files_per_level[current_application]['level'] = files_per_level[current_application]['level'].astype(str)
fig_files_per_level = px.line(files_per_level[current_application], x = 'release', y = 'num_files', color = 'level', title = 'num of files per level', markers = True)

fig_avg_folder_size = px.bar(release_stats[current_application], x = 'release', y = 'avg_folder_size', title = 'avg folder size (num of files in folder)') 

fig_max_tree_level = px.line(release_stats[current_application], x = 'release', y = 'max_tree_level', title = 'max tree level') 

fig_tree_width = px.line(release_stats[current_application], x = 'release', y = 'avg_num_files_level', title = '[testing] tree width? -> avg num of files per level') 

fig_tree_height = px.line(release_stats[current_application], x = 'release', y = 'avg_tree_level', title = '[testing] tree depth? -> avg depth from root to leaf folder') 

fig_vertical_growth = px.bar(release_stats[current_application], x = 'release', y = 'vertical_growth', title =  '[testing] vertical growth (%)') 
fig_horizontal_growth = px.bar(release_stats[current_application], x = 'release', y = 'horizontal_growth', title =  '[testing] horizontal growth (%)') 


def to_kb(b):
	kb = b/1024
	return round(kb, 1)


app.layout = html.Div(children = [

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


'''
	html.H2('Files per level'),
	dash_table.DataTable(
		files_per_level[current_application].head().to_dict('records')
	),
'''


if __name__ == '__main__':
	app.run_server(debug=True)