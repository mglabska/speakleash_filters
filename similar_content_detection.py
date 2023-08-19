# This class takes project names and MinHash algorithm hyperparameters
# and returns indices of similar documents
import os
import pandas as pd

import gaoya  # the library with MinHash algorithm implemented

import progressbar  # progressbar2, version 4.2.0
from speakleash import Speakleash
from ttictoc import tic, toc


PROJECT = "forum_parenting_pl_corpus"  # the name of dataset

# MinHash() implementation: the bigger hash_size, the slower (but more accurate) the calculation is
INDEX = gaoya.minhash.MinHashStringIndex(
    hash_size=64,
    jaccard_threshold=0.7,  # to be adjusted according to user needs, 0 = no similarity at all, 1 = exact copy
    num_bands=42,
    band_size=5,
    num_hashes=42*5,
    analyzer='word',
    lowercase=False,
    ngram_range=(1, 1))


class MinHashDF:
    def __init__(self, ds):
        self.ds = ds
        self.df = self.get_data(ds)
        self.sim_list = str(self.get_similar(self.df))  # final result

    @staticmethod
    def get_data(ds):  # function wrapping the dataset into pandas dataframe
        lst1 = []
        for doc in ds:
            txt, _ = doc
            lst1.append(txt)
        frame = pd.DataFrame(lst1, columns=['text'])
        return frame

    @staticmethod
    def get_similar(df):
        sim_list = []
        with progressbar.ProgressBar(max_value=len(df['text'])) as bar:  # monitoring the progress
            corpus = df['text'].values
            for j, doc in zip(df.index, corpus):  # MinHash
                INDEX.insert_document(j, doc)
            for i, doc in enumerate(corpus):
                # sorting - to eliminate lists of the same values easily
                # removing the first entry, because we need to keep one entry for each (multi-)duplicated value
                if len(INDEX.query(doc)) > 1:
                    sim_list.extend(sorted(INDEX.query(doc)[1:]))
                bar.update(i)
            return set(sim_list)  # checking for unique values in the final list


if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(PROJECT))
    replicate_to = os.path.join(base_dir, PROJECT)
    sl = Speakleash(replicate_to)
    ds1 = sl.get(PROJECT).ext_data
    tic()
    similar = MinHashDF(ds1).sim_list
    with open('results.txt', 'w') as res:
        res.write(similar)
    elapsed = toc()
    print(f'time elapsed: {elapsed}')
