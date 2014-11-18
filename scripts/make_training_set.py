"""
Script: make_training_set.py
============================

Description:
------------

	Goes from preprocessed dfs to a set of documents 
	mapping sets of words to their labels


Arguments:
----------

	-i (--input): input directory
	-o (--output): output file

Usage:
------

	python preprocess.py -i $DATA_DIR -o data.df

##################
Jay Hack
jhack@stanford.edu
Fall 2014
##################
"""
import os
import pickle
from collections import defaultdict, Counter
from itertools import combinations
import random
import pandas as pd
from scikit_hammertime import *


def get_legal_drugs_reacs(df, num_occurrences=10, topn=50):
	"""
		returns a set of drugs
	"""
	occurrences_DRUG = []
	occurrences_REAC = []
	for ix, row in df.iterrows():
		occurrences_DRUG += row.DRUG
		occurrences_REAC += row.REAC

	counts_DRUG = Counter(occurrences_DRUG)
	counts_REAC = Counter(occurrences_REAC)

	legal_DRUG = set([k for k in counts_DRUG.keys() if counts_DRUG[k] > num_occurrences])
	# legal_REAC = set([k[0] for k in counts_REAC.most_common(topn)])
	legal_REAC = set(counts_REAC.keys())
	return legal_DRUG, legal_REAC


def get_X_y_positive(df):
	"""
		given a dataframe, gathers all pairs that occur together 
		and maps them to their adverse effects 
	"""
	DRUGs, REACs = [], []
	for ix, row in df.iterrows():

		#=====[ Only looking at combos of drugs	]=====
		if not len(row.DRUG) >= 2 and len(row.DRUG) <= 4:
			continue

		combos = list(combinations(row.DRUG, 2))
		DRUGs += combos
		REACs += [row.REAC]*len(combos)

	return DRUGs, REACs



def get_co_occurrences(df):
	"""
		given a dataframe, returns
			dict: Words -> Set of co-occurring words
	"""
	co_occurrence = defaultdict(lambda: set([]))
	for ix, row in df.iterrows():

		drugs = row.DRUG
		for i in range(len(drugs)):
			for w in drugs[:i] + drugs[i+1:]:
				co_occurrence[drugs[i]].add(w)

	return co_occurrence


def get_X_y_negative(df, co_occurrences, num_samples=1000000):
	"""
		given a dataframe, returns sets that never 
		occurred together
	"""
	DRUGs_neg = []
	for i in range(num_samples):
		d1 = random.choice(co_occurrences.keys())
		d2 = random.choice(co_occurrences.keys())
		while d2 == d1 or d2 in co_occurrences[d1]:
			d2 = random.choice(co_occurrences.keys())
		DRUGs_neg.append((d1, d2))
	
		if i % 1000 == 0:
			print '	%d' % i
	

	REACs_neg = [[]]*len(DRUGs_neg)

	return DRUGs_neg, REACs_neg










if __name__ == '__main__':

	#=====[ Step 1: load in dataframes to 'data'	]=====
	print '-----> Loading data'
	data = load_data(num_dfs=1, data_dir='/data/aers/formatted/', verbose=False)

	#=====[ Step 2: get the legal drugs	]=====
	print '-----> Getting legal drugs'
	legal_DRUG, legal_REAC = get_legal_drugs_reacs(data, num_occurrences=10, topn=50)

	#=====[ Step 3: reduce dataset to only legal drugs	]=====
	print '-----> Reducing data.DRUGS to only legal drugs'
	data.DRUG = data.DRUG.apply(lambda l: [x for x in l if x in legal_DRUG])
	data.REAC = data.REAC.apply(lambda l: [x for x in l if x in legal_REAC])

	#=====[ Step 4: get positives	]=====
	print '-----> Getting X, y positive'
	DRUGs_pos, REACs_pos = get_X_y_positive(data)

	#=====[ Step 5: get coocurrences	]=====
	print '-----> Getting coocurrences'
	co_occurrences = get_co_occurrences(data)

	#=====[ Step 6: get negative reactions	]=====
	print '-----> Getting X, y negative'
	DRUGs_neg, REACs_neg = get_X_y_negative(data, co_occurrences)

	#=====[ Step 7: save to disk	]=====
	print '-----> Saving to pickle'
	DRUGs = DRUGs_pos + DRUGs_neg 
	REACs = REACs_pos + REACs_neg
	pickle.dump(DRUGs, open('/data/aers/training/tmp/DRUGs.pkl', 'w'))
	pickle.dump(REACs, open('/data/aers/training/tmp/REACs.pkl', 'w'))




