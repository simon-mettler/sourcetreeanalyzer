from dash import Dash, html, dcc, dash_table, callback, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import os
import settings


applications = sorted(os.listdir(settings.output_dir))

app_stats_dict = {
	'app': [],
	'num_files_first': [],
	'num_files_last': [],
}

for application in applications:

	df = pd.read_csv(
		os.path.join(settings.output_dir, application, 'stats_'+application+'.csv'))

	if application in settings.order_by_name:
		df.sort_values(by = 'release', inplace = True)

	app_stats_dict['app'].append(application)
	app_stats_dict['num_files_first'].append(df.iloc[0]['num_files'])
	app_stats_dict['num_files_last'].append(df.iloc[-1]['num_files'])


app_stats_df = pd.DataFrame.from_dict(app_stats_dict)

def pct_growth(col1, col2):
	return ((col2 - col1) / col1) * 100

app_stats_df['growth'] = app_stats_df['num_files_last'] - app_stats_df['num_files_first']
app_stats_df['growth_pct'] = round(pct_growth(app_stats_df['num_files_first'], app_stats_df['num_files_last']), 2)
app_stats_df.columns = ['Application', 'Num. of files first release', 'Num. of files last release', 'Growth', 'Growth %']


table_num_files = dash_table.DataTable(
	app_stats_df.to_dict('records'),
	style_as_list_view=True,
	sort_action = 'native',
	columns=[{'id': c, 'name': c} for c in app_stats_df.columns],
	style_cell={'textAlign': 'left'},
	style_data_conditional=[
		{
			'if': {'row_index': 'odd'},
			'backgroundColor': 'rgb(250, 250, 250)',
		}
	],
)


layout = dbc.Container([
	html.H1('Datatables'),
	html.H2('Number of source files'),
	html.P('This table shows the number of source files in the first and last release and the growth rate in absolute numbers and as percentage growth'),
	table_num_files,
])

