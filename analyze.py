import os
import pandas as pd
import folderstats
import settings

# Creates a dict containing applications and releases: {'application': ['release']}
applications = {a: sorted(os.listdir(os.path.join(settings.input_dir, a))) for a in sorted(os.listdir(settings.input_dir)) if not a.startswith('.')}

# Iterate over all releases to get stats.
for application in applications:

	release_stats = {
		'release': [],
		'total_folders': [],
		#'total_source_folders': [],
		'total_files': [],
		'total_size': [],
		'avg_file_size': [],
		'avg_folder_size': [],
		'max_tree_level': [],
		'avg_tree_level': [],
		'max_num_files_level': [],
		'avg_num_files_level': [],
		'tree_size': []
	}

	files_per_level = {
		'release': [],
		'level': [],
		'num_files': [],
	}

	os.makedirs(os.path.join(settings.output_dir, application), exist_ok = True)

	print(f"Started analyzing {application}")

	for release in applications[application]:
		release_stats['release'].append(release)

		print(f"Analyzing {release}")

		# Get folder structure from current release as dataframe using 'folderstats' module.
		folder_stats = folderstats.folderstats(
			os.path.join(settings.input_dir, application, release), 
			ignore_hidden = True, 
			filter_extension = settings.file_extensions
		)

		# Convert depth to level
		folder_stats['depth'] = folder_stats['depth'] + 1
		folder_stats.rename(columns = {'depth': 'level'}, inplace = True)

		# Export to csv.
		folder_stats[['id', 'parent', 'name', 'extension', 'size', 'mtime', 'folder', 'num_files', 'level']].to_csv(os.path.join(settings.output_dir, application, 'tree_' + release + '.csv'), index = False)

		# Average tree level.
		levels = folder_stats.loc[ (folder_stats['folder'] == True) & (~folder_stats['id'].isin(folder_stats['parent'])) ]
		avg_tree_level = round(levels['level'].mean(), 4)
		release_stats['avg_tree_level'].append(avg_tree_level)

		# Total number of folders and files.
		total_num_files = folder_stats.loc[folder_stats['folder'] == False].shape[0]
		total_num_folders = folder_stats.loc[folder_stats['folder'] == True].shape[0]
		release_stats['total_files'].append(total_num_files)
		release_stats['total_folders'].append(total_num_folders)

		release_stats['total_size'].append(folder_stats.loc[folder_stats['folder'] == True, ['size']].sum()['size'])

		# Average file size in bytes.
		release_stats['avg_file_size'].append(round(folder_stats.loc[folder_stats['folder'] == False, ['size']].mean()['size'], 2))

		# Average folder size (number of files in folder)
		release_stats['avg_folder_size'].append(round(total_num_files / total_num_folders, 2))
		
		# Maximum tree level.
		release_stats['max_tree_level'].append(folder_stats['level'].max())

		# Number of files per level. 
		fpl = folder_stats.loc[folder_stats['folder'] == False].value_counts('level').to_frame().reset_index()
		fpl.columns = ['level', 'num_files']
		fpl['release'] = release
		fpl.sort_values(by = 'level', ascending = True, inplace = True)
		
		files_per_level['release'] += fpl['release'].to_list()
		files_per_level['level'] += fpl['level'].to_list()
		files_per_level['num_files'] += fpl['num_files'].to_list()

		release_stats['max_num_files_level'].append(round(fpl['num_files'].max(), 2))

		avg_num_files_level = round(fpl['num_files'].mean(), 2)
		release_stats['avg_num_files_level'].append(avg_num_files_level)

		release_stats['tree_size'].append(avg_num_files_level/avg_tree_level)


	df_release_stats = pd.DataFrame.from_dict(release_stats)
	df_files_per_level = pd.DataFrame.from_dict(files_per_level)


	df_release_stats['vertical_growth'] = df_release_stats['avg_tree_level'].pct_change().mul(100).round(2)
	df_release_stats['horizontal_growth'] = df_release_stats['avg_num_files_level'].pct_change().mul(100).round(2)

	# Export to csv.
	df_release_stats.to_csv(os.path.join(settings.output_dir, application, 'stats_' + application + '.csv'), index = False)
	df_files_per_level.to_csv(os.path.join(settings.output_dir, application, 'files-per-level_' + application + '.csv'))

	print(f"Exported {application} results to csv")

	#print('-' * 60)
print("Done...")
