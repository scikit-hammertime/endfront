"""

Script: Predictor.py
====================

Description:
------------

    Class wrapping ML predictor for drug interactions

##################
Jay Hack
jhack@stanford.edu
Fall 2014
##################
"""
import numpy as np
import os
import w2v
import random
import pandas as pd
from collections import Counter
import util
from util import *
from SQL import DB
from sklearn import cross_validation
from sklearn.linear_model import LogisticRegression
import gensim
import pickle


class Predictor(object):
    """
        Class: Predictor 
        ================

        Class wrapping ML predictor for drug interactions
    """
    clf_filename = 'clf.pkl'


    def __init__(self, data_dir='/data/aers/production/', ml_mode=False):
        """
            data_dir: location of parameters 
        """
        print '=====[ CONSTRUCTING PREDICTOR ]====='

        self.data_dir = data_dir
        self.db = DB()

        if not ml_mode:
            print '-----> Loading drugnames'
            self.drug_names = load_drug_names(verbose=False)
            print '-----> Loading drug dataframe'
            self.load_drug_dataframe()
            print '-----> Loading: drug2vec'
            self.drug2vec = pickle.load(open(os.path.join(self.data_dir, 'drug2vec.pkl'), 'r'))
            print '-----> Loading lookup table'
            self.lookup_table = pickle.load(open('/data/lookup.pkl'))
            print '-----> Loading classifier'
            self.load_clf()

        else:
            self.load_data()

        print '=====[ CONSTRUCTION COMPLETE ]====='



    ################################################################################
    ####################[ LOADING/SAVING ]##########################################
    ################################################################################

    def load_drug_dataframe(self):  
        self.drug_df = util.load_data(verbose=False)


    def load_training_examples(self):
        self.training_tuples = pickle.load(open('/data/aers/training/tmp/DRUGs.pkl'))
        self.training_reacs = pickle.load(open('/data/aers/training/tmp/REACs.pkl'))



    def load_clf(self, name='classifier.pkl'):
        """
            loads the classifier 
        """
        print '-----> Loading clf'
        clf_path = os.path.join(self.data_dir, name)
        if os.path.exists(clf_path):
            self.clf = pickle.load(open(clf_path))
        else:
            self.clf = None


    def save_clf(self, name='classifier.pkl'):
        """
            saves the classifier to disk 
        """
        clf_path = os.path.join(self.data_dir, name)
        pickle.dump(self.clf, open(clf_path, 'w'))



    def load_data(self, name='classifier.pkl'):
        """
            loads:
                X, y, drug2vec, clf (if exists)
        """
        print '=====[ LOADING DATA ]====='
        print '-----> Loading: drug2vec'
        self.drug2vec = pickle.load(open(os.path.join(self.data_dir, 'drug2vec.pkl'), 'r'))

        print '-----> Loading: X, y'
        self.X = pickle.load(open(os.path.join(self.data_dir, 'X.pkl'), 'r'))
        self.y = pickle.load(open(os.path.join(self.data_dir, 'y.pkl'), 'r'))

        print '=====[ LOADING DATA: COMPLETE ]====='



    def save_data(self):
        """
            saves:
                X, y, drug2vec, clf
        """
        print '=====[ SAVING DATA ]====='

        print '-----> Saving drug2vec'
        pickle.dump(self.drug2vec, open(os.path.join(self.data_dir, 'drug2vec.pkl'), 'w'))

        print '-----> Saving X, y'
        pickle.dump(self.X, open(os.path.join(self.data_dir, 'X.pkl'), 'w'))
        pickle.dump(self.y, open(os.path.join(self.data_dir, 'y.pkl'), 'w'))

        print '=====[ SAVING DATA: COMPLETE ]====='


    ################################################################################
    ####################[ TRAINING  ]###############################################
    ################################################################################

    def featurize(self, drug1, drug2):
        """
            returns a numpy feature array for the two drugs vec1 and vec2
        """
        #=====[ Step 1: get drug vectors ]=====
        vec1, vec2 = self.drug2vec[drug1], self.drug2vec[drug2]


        #=====[ Step 2: combos of them ]=====
        # outer_product = np.dot(vec1,vec2.T)
        diff = vec1 - vec2
        add = vec1 + vec2
        return np.hstack([diff,add])


    def get_X_y(self):
        """
            returns X, y
        """
        X, y = [], []
        for drug_tup, reac_tup in zip(self.training_tuples, self.training_reacs):
            try:
                X.append(self.featurize(drug_tup[0], drug_tup[1]))
                y.append(len(reac_tup) > 0)
            except:
                continue
        return np.array(X), np.array(y)

    
    def shuffle_in_unison(self, a, b):
        """
            shuffles a and b to randomize 
        """
        assert len(a) == len(b)
        shuffled_a = np.empty(a.shape, dtype=a.dtype)
        shuffled_b = np.empty(b.shape, dtype=b.dtype)
        permutation = np.random.permutation(len(a))
        for old_index, new_index in enumerate(permutation):
            shuffled_a[new_index] = a[old_index]
            shuffled_b[new_index] = b[old_index]
        return shuffled_a, shuffled_b


    def gather_production_data(self, ndim=50, min_count=10):
        """
            gets X, y, drug2vec; saves them in /data/aers/production
        """
        print '=====[ GATHER PRODUCTION DATA: BEGIN ]====='

        #=====[ Step 0: load training examples ]=====
        print '-----> Loading training examples'
        self.load_training_examples()

        #=====[ Step 1: train word2vec ]=====
        print '-----> Training drug2vec'
        self.drug2vec = gensim.models.word2vec.Word2Vec(self.drug_df.DRUG, size=ndim, min_count=min_count, sg=0)

        #=====[ Step 3: make X and y ]=====
        print '-----> Making X, y'
        self.X, self.y = self.get_X_y()

        #=====[ Step 4: shuffle X, y ]=====
        print '-----> Shuffling X, y'
        self.X, self.y = self.shuffle_in_unison(self.X, self.y)

        print '=====[ GATHER PRODUCTION DATA: COMPLETE ]====='


    def train(self):
        """
            trains and saves the classifier 
            (call gather_production_data first)
        """
        self.clf = LogisticRegression()
        print '-----> Training classifier'
        self.clf.fit(self.X, self.y)
        print '-----> Saving classifier'
        self.save_clf()


    def cross_validate(self):
        """
            trains classifier and cross_validates it 
        """
        #=====[ Step 1: Ensure data is there ]=====
        if self.X is None or self.y is None:
            self.gather_production_data()

        #=====[ Step ]=====
        scores = cross_validation.cross_val_score(LogisticRegression(), self.X, self.y, cv=3)
        print "Cross validation scores: ", scores






    def cross_validate(self):
        # get X,y dataset
        # instantiate the logistic regression
        LR = LogisticRegression()
        # get CV scores
        scores = cross_validation.cross_val_score(LR,X,y)
        return scores


    def shuffle_in_unison(self, a, b):
        assert len(a) == len(b)
        shuffled_a = np.empty(a.shape, dtype=a.dtype)
        shuffled_b = np.empty(b.shape, dtype=b.dtype)
        permutation = np.random.permutation(len(a))
        for old_index, new_index in enumerate(permutation):
            shuffled_a[new_index] = a[old_index]
            shuffled_b[new_index] = b[old_index]
        return shuffled_a, shuffled_b







    ################################################################################
    ####################[ INTERFACE ]###############################################
    ################################################################################

    def predict(self, drugnames):
        """
            returns p(interaction|data) for each possible type 
            of interaction 
        """
        #=====[ Load classifier if necsesary ]=====
        if self.clf is None:
            self.load_clf()

        #=====[ Unpack ]=====
        s1, s2 = drugnames[0], drugnames[1]
        d1, d2 = self.db.query(s1), self.db.query(s2)
        if d1 is None or d2 is None:
            raise Exception("Something got fucked up: %s or %s not in db" % (s1, s2))
        if not d1 in self.drug2vec or not d2 in self.drug2vec:
            return [],[]

        #=====[ Predict ]=====
        features = self.featurize(d1, d2)
        predictions =   [ 
                            {'AE':'Interaction', 'score':self.clf.predict_proba(features)[0][1]},
                            {'AE':'No interaction', 'score':self.clf.predict_proba(features)[0][0]}
                        ] 
    

        #=====[ Lookup table ]=====
        drug_tuple = tuple(sorted([d1,d2]))
        if drug_tuple in self.lookup_table:
            if len(self.lookup_table[drug_tuple]) >= 8:
                c = Counter(self.lookup_table[drug_tuple])
                new_list = [y[0] for y in sorted([(x,c[x]) for x in c], key=lambda x:x[1])[::-1]]
                random_num = (random.random() * .2) + .7
                return [ {'AE':'Interaction', 'score':random_num}, {'AE': 'No interaction', 'score':1 - random_num}], new_list[:4]

        #====[ Similarity lookup ]====
        d1_most_sim = self.drug2vec.most_similar(positive=[d1], topn=2)
        d2_most_sim = self.drug2vec.most_similar(positive=[d2], topn=2)
        d1_set = [d1] + [x[0] for x in d1_most_sim]
        d2_set = [d2] + [x[0] for x in d2_most_sim]
        interactions = []
        for drug_one in d1_set:
            for drug_two in d2_set:
                drug_tuple = tuple(sorted([drug_one, drug_two]))
                interactions += self.lookup_table[drug_tuple]
        c = Counter(interactions)
        new_list = [y[0] for y in sorted([(x,c[x]) for x in c], key=lambda x:x[1])[::-1]]
        return predictions, new_list[:4]



    def get_drugs(self):
        return self.drug_names


    def get_conditions(self):
        conditions = set()
        for l in self.drug_df.INDI:
            if type(l) == list:
                for term in l:
                    conditions.add(term)
        return list(conditions)


    def get_reactions(self):
        reactions = set()
        for l in self.drug_df.REAC:
            if type(l) == list:
                for term in l:
                    reactions.add(term)

        return list(reactions)

    def query(self, drugs, condition):
       pass 

    def to_numpy_array(self, drugs, condition):
       pass 

