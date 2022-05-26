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
		'size_bytes': [],
		'num_files': [],
		'avg_file_size_bytes': [],
		'num_folders': [],
		'num_source_folders': [],
		'avg_source_folder_size_num_files': [],
		'avg_source_folder_size_bytes': [],
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

	# Create output folders if not existing.
	os.makedirs(os.path.join(settings.output_dir, application), exist_ok = True)

	print(f"Started analyzing {application}")

	for release in applications[application]:
		release_stats['release'].append(release)

		print(f"Analyzing {release}")

		# Get folder structure from current release as dataframe using 'folderstats' module.
		fs = folderstats.folderstats(
			os.path.join(settings.input_dir, application, release), 
			ignore_hidden = True, 
			filter_extension = settings.file_extensions
		)


		# Count number of files in folder (direct children). Used for the 'source folder size' metric).
		# fs['num_files'] can't be used since it counts all files in a folder AND its subfolders
		num_files_direct= pd.DataFrame(fs[fs['folder'] == False]
			.value_counts('parent')
			.reset_index()
		)
		num_files_direct.columns = ['id', 'num_files_direct']
		fs = pd.merge(fs, num_files_direct, on = 'id', how = 'left')


		# Convert depth to level
		fs['depth'] = fs['depth'] + 1

		fs.rename(columns = {
			'depth': 'level', 
			'parent_x': 'parent', 
			'size': 'size_bytes'
		}, 
		inplace = True)


		# Export detailed release statistics to csv.
		fs[[
			'id', 
			'parent', 
			'name', 
			'extension', 
			'size_bytes', 
			'folder', 
			'num_files', 
			'num_files_direct', 
			'level'
		]].to_csv(
			os.path.join(settings.output_dir, application, 'tree_' + release + '.csv'), 
			index = False
		)


		# All source folders.
		num_source_folders = fs.loc[ fs['id'].isin(fs[fs['folder'] == False]['parent'])]
		release_stats['num_source_folders'].append(len(num_source_folders))


		# Average tree level.
		levels = fs.loc[ (fs['folder'] == True) & (~fs['id'].isin(fs['parent'])) ]
		avg_tree_level = round(levels['level'].mean(), 4)
		release_stats['avg_tree_level'].append(avg_tree_level)

		# Total number of folders and files.
		num_files = fs.loc[fs['folder'] == False].shape[0] 		# Total number of files.
		num_folders = fs.loc[fs['folder'] == True].shape[0] 	# Total number of folders.
		release_stats['num_files'].append(num_files)
		release_stats['num_folders'].append(num_folders)

		size_bytes = fs.loc[fs['folder'] == True, ['size_bytes']].sum()['size_bytes']
		release_stats['size_bytes'].append(size_bytes)

		# Average file size in bytes.
		release_stats['avg_file_size_bytes'].append(round(fs.loc[fs['folder'] == False, ['size_bytes']].mean()['size_bytes'], 2))

		# Average folder size (number of files in folder)
		release_stats['avg_source_folder_size_num_files'].append(round(num_files / num_source_folders.shape[0], 2))
		release_stats['avg_source_folder_size_bytes'].append(round(size_bytes / num_source_folders.shape[0], 0))
		
		# Maximum tree level.
		release_stats['max_tree_level'].append(fs['level'].max())

		# Number of files per level. 
		fpl = fs.loc[fs['folder'] == False].value_counts('level').to_frame().reset_index()
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
