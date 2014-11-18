import gensim
import pickle as pkl
from util import *
def train(df, ndim=50, min_count=10):
    '''
    trains and dumps a word2vec model with ndim dimensions, counting only drug names that occur more than min_count times
    '''
    # laod the dataframes
    df = load_data()
    # assumes that df.DRUG is a series of lists of words, all lowercased and split to the first word.
    w2v = gensim.models.word2vec.Word2Vec(df.DRUG, size=ndim, min_count=min_count, sg=0)
    return w2v


