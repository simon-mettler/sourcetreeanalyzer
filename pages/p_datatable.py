from dash import Dash, html, dcc, dash_table, callback, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import os
import settings

def to_kb(b):
	kb = b/1024
	return round(kb, 1)


applications = sorted(os.listdir(settings.output_dir))

app_stats_dict = {
	'app': [],
	'num_files_first': [],
	'num_files_last': [],
	'avg_file_size_kb_last': [],
	'release_size_kb_last': [],
}

for application in applications:

	df = pd.read_csv(
		os.path.join(settings.output_dir, application, 'stats_'+application+'.csv'))

	if application in settings.order_by_name:
		df.sort_values(by = 'release', inplace = True)

	app_stats_dict['app'].append(application)
	app_stats_dict['num_files_first'].append(df.iloc[0]['num_files'])
	app_stats_dict['num_files_last'].append(df.iloc[-1]['num_files'])
	app_stats_dict['avg_file_size_kb_last'].append(df.iloc[-1]['avg_file_size_bytes'])
	app_stats_dict['release_size_kb_last'].append(df.iloc[-1]['release_size_bytes'])


app_stats_df = pd.DataFrame.from_dict(app_stats_dict)

# Calculates % growth between values from two columns.
def pct_growth(col1, col2):
	return ((col2 - col1) / col1) * 100

app_stats_df['growth_num_files'] = app_stats_df['num_files_last'] - app_stats_df['num_files_first']
app_stats_df['growth_num_files_pct'] = round(pct_growth(app_stats_df['num_files_first'], app_stats_df['num_files_last']), 2)
app_stats_df['avg_file_size_kb_last'] = app_stats_df['avg_file_size_kb_last'].apply(to_kb)


data_table_num_files = app_stats_df[['app', 'num_files_first', 'num_files_last', 'growth_num_files', 'growth_num_files_pct']]
data_table_num_files.columns = ['Application', 'First Release','Last Release','Growth (Number of files)','Growth (%)']

table_num_files = dash_table.DataTable(
	data_table_num_files.to_dict('records'),
	style_as_list_view=True,
	sort_action = 'native',
	columns=[{'id': c, 'name': c} for c in data_table_num_files.columns],
	style_cell={'textAlign': 'left'},
	style_data_conditional=[
		{
			'if': {'row_index': 'odd'},
			'backgroundColor': 'rgb(250, 250, 250)',
		}
	],
)


data_table_size = app_stats_df[['app', 'release_size_kb_last', 'avg_file_size_kb_last']]

fig = px.scatter(
	data_table_size,
	title = 'xxx',
	x = 'release_size_kb_last', 
	y = 'avg_file_size_kb_last', 
	template = 'none',
	labels = {
		'release_size_kb_last': 'Release size',
		'avg_file_size_kb_last': 'Avg. file size',
	},
)

data_table_size.columns = ['Application', 'Latest Release Size (KB)','Average File Size (KB)']

table_size = dash_table.DataTable(
	data_table_size.to_dict('records'),
	style_as_list_view=True,
	sort_action = 'native',
	columns=[{'id': c, 'name': c} for c in data_table_size.columns],
	style_cell={'textAlign': 'left'},
	style_data_conditional=[
		{
			'if': {'row_index': 'odd'},
			'backgroundColor': 'rgb(250, 250, 250)',
		}
	],
)



# Page layout
layout = dbc.Container([
	html.H1('Datatables'),
	html.H2('Number of source files'),
	html.P('This table shows the number of source files in the first and last release and the growth rate in absolute numbers and as percentage growth'),
	table_num_files,
	html.H2('Project and file size'),
	html.P('This table shows the latest release project size and the average file size in KB.'),
	table_size,
	dcc.Graph(figure=fig)
])

