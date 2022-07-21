import os
import pandas as pd
import folderstats
import settings
import pathlib
import hashlib
import base64


# Creates a dict containing applications and releases: {'application': ['release']}
applications = {
	a: sorted(os.listdir(os.path.join(settings.input_dir, a))) 
	for a in sorted(os.listdir(settings.input_dir)) if not a.startswith('.')
}


# Iterates over all applications to get statistics for each release.
for application in applications:
	
	print(f"Started analyzing {application}")

	release_stats = {
		'release': [],
		'mtime': [],
		'release_size_bytes': [],
		'num_files': [],
		'max_file_size_bytes': [],
		'avg_file_size_bytes': [],
		'num_folders': [],
		'num_source_folders': [],
		'max_source_folder_size_num_files': [],
		'avg_source_folder_size_num_files': [],
		'avg_source_folder_size_bytes': [],
		'max_tree_level': [],
		'avg_tree_level': [],
		'max_num_files_level': [],
		'avg_num_files_level': [],
		'max_num_folders_level': [],
		'avg_num_folders_level': [],
	}

	level_stats = {
		'release': [],
		'mtime': [],
		'level': [],
		'num_files': [],
		'num_folders': [],
	}


	# Creates output folders if not existing.
	os.makedirs(os.path.join(settings.output_dir, application), exist_ok = True)


	# Iterate over all releases to get stats/metrics.
	for release in applications[application]:

		print(f"Analyzing {release}")
		release_stats['release'].append(release)

		# Get folder structure from current release as dataframe using 'folderstats' module.
		fs = folderstats.folderstats(
			os.path.join(settings.input_dir, application, release), 
			ignore_hidden = True, 
			hash_name = 'md5',
			exclude = settings.exclude,
			filter_extension = settings.file_extensions
		)


		# Count number of files in folder (direct children).
		# 'Number of Files' from folderstats module can't be used since 
		# it counts all files in a folder AND its subfolders.
		num_files_direct = pd.DataFrame(fs[fs['folder'] == False]
			.value_counts('parent')
			.reset_index()
		)
		num_files_direct.columns = ['id', 'num_files_direct']
		fs = pd.merge(fs, num_files_direct, on = 'id', how = 'left')

		# Convert tree depth to level.
		fs['depth'] = fs['depth'] + 1

		# Cut path to start at root release folder.
		def cut_path(p):
			path = pathlib.Path(p)
			return path.relative_to(*path.parts[:3])

		fs['path'] = fs['path'].apply(cut_path)

		# Creates hash from path.
		# This ensures consistent id's even if nodes are added to the folder tree.
		def hash_path(p):
			hash_value = hashlib.md5(str(p).encode('utf-8')).hexdigest()
			return hash_value

		fs['hash_id'] = fs['path'].apply(hash_path)
		
		fs = pd.merge(fs, fs[['hash_id', 'id']], left_on = 'parent', right_on = 'id', how = 'left')

		# Delete unused columns.
		fs.drop(columns=['id_y','id_x', 'parent', 'uid', 'ctime', 'atime',  'path'], inplace=True)

		# Rename columns
		fs.rename(columns = {
			'depth': 'level', 
			'hash_id_y': 'parent',
			'hash_id_x': 'id',
			'size': 'size_bytes'
		}, 
		inplace = True)

		# Removes all folders which do not contain at least one source file in its subtree.
		fs = fs.drop(fs[(fs['folder'] == True) & (fs['num_files'] == 0)].index)

		# Export detailed release statistics to csv.
		fs.to_csv(
			os.path.join(settings.output_dir, application, 'tree_' + release + '.csv'), 
			index = False
		)


		# Calculate release metrics.

		# Adds modification time to release statistics.
		release_stats['mtime'].append(fs.iloc[0]['mtime'])
		mtime = fs.iloc[0]['mtime']

		# Gets total number of source folders.
		num_source_folders = fs.loc[ fs['id'].isin(fs[fs['folder'] == False]['parent'])]
		release_stats['num_source_folders'].append(len(num_source_folders))

		# Calculates source folder size (number of files)
		release_stats['max_source_folder_size_num_files'].append(fs['num_files_direct'].max())

		# Calculates average tree level.
		levels = fs.loc[ (fs['folder'] == True) & (~fs['id'].isin(fs['parent'])) ] # Gets all folder leaf nodes.
		avg_tree_level = round(levels['level'].mean(), 4)
		release_stats['avg_tree_level'].append(avg_tree_level)

		# Gets total number of folders and files.
		num_files = fs.loc[fs['folder'] == False].shape[0] 		# Total number of files.
		num_folders = fs.loc[fs['folder'] == True].shape[0] 	# Total number of folders.
		release_stats['num_files'].append(num_files)
		release_stats['num_folders'].append(num_folders)

		# Gets release size in bytes.
		release_size_bytes = fs.loc[fs['folder'] == False, ['size_bytes']].sum()['size_bytes']
		release_stats['release_size_bytes'].append(release_size_bytes)

		# Gets max file size in bytes.
		release_stats['max_file_size_bytes'].append(
			fs.loc[fs['folder'] == False, ['size_bytes']].max()['size_bytes'])

		# Calculates average file size in bytes.
		release_stats['avg_file_size_bytes'].append(
			round(fs.loc[fs['folder'] == False, ['size_bytes']].mean()['size_bytes'], 2))

		# Calculates average folder size (number of files in folder).
		release_stats['avg_source_folder_size_num_files'].append(
			round(num_files / num_source_folders.shape[0], 2))

		# Calculates average folder size (bytes).
		release_stats['avg_source_folder_size_bytes'].append(
			round(release_size_bytes / num_source_folders.shape[0], 0))
		
		# Gets maximum tree level.
		max_tree_level = fs.loc[fs['folder'] == True]['level'].max()
		release_stats['max_tree_level'].append(max_tree_level)


		# Get level statistics. 

		# Gets number of files per level.
		files = fs.loc[fs['folder'] == False].value_counts('level').to_frame().reset_index()
		files.columns = ['level', 'num_files']
		files['mtime']= mtime
		files['release'] = release

		# Gets number of folders per level.
		folders = fs.loc[fs['folder'] == True].value_counts('level').to_frame().reset_index()
		folders.columns = ['level', 'num_folders']
		folders['mtime']= mtime
		folders['release'] = release

		# Merges folder and file stats to one dataframe.
		files_folders = pd.merge(folders, files, on=['level', 'release', 'mtime'], how = 'outer')
		files_folders.sort_values(by = 'level', ascending = True, inplace = True)

		level_stats['release'] += files_folders['release'].to_list()
		level_stats['mtime'] += files_folders['mtime'].to_list()
		level_stats['level'] += files_folders['level'].to_list()
		level_stats['num_files'] += files_folders['num_files'].to_list()
		level_stats['num_folders'] += files_folders['num_folders'].to_list()

		# Gets max number of files and folders per level.
		release_stats['max_num_files_level'].append(files_folders['num_files'].max())
		max_num_folders_level = files_folders['num_folders'].max()
		release_stats['max_num_folders_level'].append(max_num_folders_level)

		# Gets average number of files and folders per level.
		avg_num_files_level = round(files_folders['num_files'].mean(), 2)
		avg_num_folders_level = round(files_folders['num_folders'].mean(), 2)
		release_stats['avg_num_files_level'].append(avg_num_files_level)
		release_stats['avg_num_folders_level'].append(avg_num_folders_level)


	# Convert dicts to dataframes.
	df_release_stats = pd.DataFrame.from_dict(release_stats)
	df_release_stats.sort_values(by = 'mtime', inplace = True)
	df_level_stats = pd.DataFrame.from_dict(level_stats)

	# Calculate % growth rates.
	def pct_growth(series):
		return series.pct_change().mul(100).round(2)

	# Adds calculated growth rates to dataframe.
	df_release_stats['growth_size_bytes'] = df_release_stats['release_size_bytes'].diff()
	df_release_stats['growth_size_bytes_pct'] = pct_growth(df_release_stats['release_size_bytes'])
	df_release_stats['growth_num_files'] = df_release_stats['num_files'].diff()
	df_release_stats['growth_num_files_pct'] = pct_growth(df_release_stats['num_files'])
	df_release_stats['growth_num_source_folders'] = df_release_stats['num_source_folders'].diff()
	df_release_stats['growth_num_source_folders_pct'] = pct_growth(df_release_stats['num_source_folders'])
	df_release_stats['growth_avg_source_folder_size_num_files_pct'] = pct_growth(df_release_stats['avg_source_folder_size_num_files'])
	df_release_stats['growth_avg_source_folder_size_bytes'] = df_release_stats['avg_source_folder_size_bytes'].diff()
	df_release_stats['growth_avg_source_folder_size_bytes_pct'] = pct_growth(df_release_stats['avg_source_folder_size_bytes'])
	df_release_stats['growth_max_tree_level'] = df_release_stats['max_tree_level'].diff()
	df_release_stats['growth_max_tree_level_pct'] = pct_growth(df_release_stats['max_tree_level'])
	df_release_stats['growth_avg_tree_level_pct'] = pct_growth(df_release_stats['avg_tree_level'])
	df_release_stats['growth_max_num_files_level'] = df_release_stats['max_num_files_level'].diff()
	df_release_stats['growth_max_num_files_level_pct'] = pct_growth(df_release_stats['max_num_files_level'])
	df_release_stats['growth_avg_num_files_level_pct'] = pct_growth(df_release_stats['avg_num_files_level'])
	df_release_stats['growth_tree_depth_pct'] = pct_growth(df_release_stats['avg_tree_level'])
	df_release_stats['growth_tree_width_pct'] = pct_growth(df_release_stats['avg_num_files_level'])
	df_release_stats['growth_tree_size_pct'] = pct_growth(df_release_stats['tree_size'])

	# Exports results to csv.
	df_release_stats.to_csv(
		os.path.join(settings.output_dir, application, 'stats_' + application + '.csv'), 
		index = False)
	df_level_stats.to_csv(
		os.path.join(settings.output_dir, application, 'files-per-level_' + application + '.csv'), 
		index = False)


	print(f"Exported {application} results to csv")


print("Done...")
