"""
Script: preprocess.py
=====================

Description:
------------

	Goes from raw ascii data, chunked in files,
	to a set of pandas dataframes that are properly 
	formatted.

	outputs:
	formatted/[df_name].df



Usage:
------

	python preprocess.py -i $input_dir -o data.df

##################
Jay Hack
jhack@stanford.edu
Fall 2014
##################
"""
import os
import pickle
import pandas as pd
from scikit_hammertime import *

class Preprocess(object):
	"""
		takes care of all preprocessing 
	"""
	def __init__(self):
		"""
			presets
		"""
		#=====[ Presets	]=====
		self.input_dir = '/data/aers/entries'
		self.output_dir = '/data/aers/formatted'
		# self.process_years = [2013, 2014]
		self.process_years = [2014]
		# self.process_quarters = [1, 2, 3, 4]
		self.process_quarters = [1]

		#=====[ Drug Names	]=====
		self.drug_names = [] #contains all drug names
		self.db = DB()



	################################################################################
	####################[ FILENAME PARSING	]#######################################
	################################################################################


	def parse_quarter_dirname(self, quarter_dir):
		"""
			given AERS directory name, returns 
				year, quarter
		"""
		quarter_dir = os.path.split(quarter_dir)[-1]
		year = int(quarter_dir[:4])
		quarter = int(quarter_dir[5])
		return year, quarter


	def parse_filename(self, filepath):
		"""
			given a .txt filename, returns 
				file_descriptor, year, quarter
		"""
		filename = os.path.split(filepath)[-1]
		file_descriptor = filename[:4].upper()
		year = int(filename[4:6])
		quarter = int(filename[7])
		return file_descriptor, year, quarter




	################################################################################
	####################[ FORMAT INDIVIDUAL FILES	]###############################
	################################################################################


	def retain_columns(self, df, col_list):
		drop_columns = set(df.columns).difference(set(col_list))
		df = df.drop(drop_columns, axis=1, inplace=True)


	def format_DRUG(self, df):
		self.retain_columns(df, ['primaryid', 'drugname'])
		df.drugname = df.drugname.str.lower().str.strip().astype('category')
		df = df.groupby('primaryid').drugname.agg(lambda x: list(x))

		#=====[ add drug_names	]=====
		print '	---> updating drug_names'
		for x in df:
			self.drug_names += x

		#=====[ Map drugnames to ids	]=====
		df = df.apply(lambda x: list(set([self.db.query(str(y)) for y in x])))
		df = df.apply(lambda x: [y for y in x if not y is None])
		return df


	def format_REAC(self, df):
		self.retain_columns(df, ['primaryid', 'pt'])
		df.pt = df.pt.str.lower().str.strip().astype('category')
		df = df.groupby('primaryid').pt.agg(lambda x: list(x))
		return df


	def format_INDI(self, df):
		self.retain_columns(df, ['primaryid', 'indi_pt'])
		df.indi_pt = df.indi_pt.str.lower().str.strip().astype('category')
		df = df.groupby('primaryid').indi_pt.agg(lambda x: list(x))
		return df


	def format_quarter(self, quarter_dir):
		"""
			given a path to a directory containing data files, 
			(i.e. data/faers_ascii_2014q1)
			returns a dataframe containing all the information

			also fill in drug_names
		"""
		#=====[ Step 1: Get ascii_dir, name	]=====
		year, quarter = self.parse_quarter_dirname(quarter_dir)
		print '=====[ %d, %d ]=====' % (year, quarter)
		ascii_dir = os.path.join(quarter_dir, 'ascii')
		if not os.path.exists(ascii_dir):
			ascii_dir = os.path.join(quarter_dir, 'ASCII')
		assert os.path.exists(ascii_dir)


		#=====[ Step 2: load/format each independently	]=====
		dfs = {}
		format_funcs = {
							'DRUG':self.format_DRUG,
							'REAC':self.format_REAC,
							'INDI':self.format_INDI
						}
		for filename in [os.path.join(ascii_dir, p) for p in os.listdir(ascii_dir) if p.endswith('.txt')]:

			file_descriptor, year, quarter = self.parse_filename(filename)
			if file_descriptor in format_funcs.keys() and filename.endswith('.txt'):
				
				print '	---> Loading: %s' % file_descriptor
				df = pd.read_csv(filename, delimiter='$')

				print '	---> Formatting: %s' % file_descriptor
				df = format_funcs[file_descriptor](df)

				dfs[file_descriptor] = df

		#=====[ Step 3: join on primaryid	]=====
		joined = pd.concat(dfs.values(), keys=dfs.keys(), axis=1)
		return joined



	def preprocess(self):

		print '=====[ PREPROCESSING BEGIN ]====='
		#=====[ Step 2: For each quarter... ]=====
		self.dfs = []
		quarter_dirs = [os.path.join(self.input_dir, p) for p in os.listdir(self.input_dir)]
		for quarter_dir in quarter_dirs:

			year, quarter = self.parse_quarter_dirname(quarter_dir)
			if year in self.process_years and quarter in self.process_quarters:

				dump_path_pickle = os.path.join(self.output_dir, str(year) + 'q' + str(quarter) + '.df')
				dump_path_csv = os.path.join(self.output_dir, str(year) + 'q' + str(quarter) + '.csv')
				df = self.format_quarter(quarter_dir)

				# pickle.dump(df, open(dump_path_pickle, 'w'))
				# df.to_csv(open(dump_path_csv, 'w'))
				# print '-----> Dumping to: %s' % dump_path_pickle
				
				self.dfs.append(df)

		print '=====[ PREPROCESSING COMPLETE ]====='





	def save_drugnames(self, path='/data/aers/formatted/drug_names.pkl'):
		"""
			saves drugnames (a list) to prespecified path 
		"""
		# print '-----> Saving drug_names to %s' % path
		self.drug_names = list(set(self.drug_names))
		self.drug_names.pop(0)
		# pickle.dump(self.drug_names, open(path, 'w'))





if __name__ == '__main__':

	p = Preprocess()
	p.preprocess()
	p.save_drugnames()



