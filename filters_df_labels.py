import numpy as np
import os
import pandas as pd
import pickle


from speakleash import Speakleash

PROJECT = "biblioteka_nauki_pl_corpus"
def get_data(ds):
    lst1 = []
    for doc in ds:
        txt, meta = doc
        meta['text'] = txt
        lst1.append(meta)
    df = pd.DataFrame(lst1)
    cols = ['punctuations', 'symbols', 'stopwords', 'oovs', 'pos_num', 'pos_x', 'capitalized_words']
    for col in cols:
        df[f'{col}_ratio'] = df[col] / df['words']
    return df

def get_filtered(df):
    mask_cc = {'LOW': df['camel_case'] > 10, 'HIGH': df['camel_case'] < 3}
    mask_cw = {'LOW': df['capitalized_words_ratio'] > 0.4, 'HIGH': df['capitalized_words_ratio'] < 0.1}
    mask_punct = {
        'LOW': (df['punctuations_ratio'] > 0.4) | (df['punctuations_ratio'] < 0.15),
        'HIGH': (df['punctuations_ratio'] > 0.1) & (df['punctuations_ratio'] < 0.3)
    }
    mask_symb = {'LOW': df['symbols_ratio'] > 0.02,'HIGH': df['symbols_ratio'] < 0.01}
    mask_word = {
        'LOW': (df['avg_word_length'] > 8) | (df['avg_word_length'] < 3),
        'HIGH': (df['avg_word_length'] > 4) & (df['avg_word_length'] < 7)
    }


    mask_num = {'LOW': df['pos_num_ratio'] > 0.1, 'HIGH': df['pos_num_ratio'] < 0.05}
    mask_oovs = {'LOW': df['oovs_ratio'] > 0.1,  'HIGH': df['oovs_ratio'] < 0.05}
    mask_stop = {
        'LOW': (df['stopwords_ratio'] > 0.5) | (df['stopwords_ratio'] < 0.1),
        'HIGH': (df['stopwords_ratio'] > 0.2) & (df['stopwords_ratio'] < 0.4)
    }
    mask_x = {'LOW': df['pos_x_ratio'] > 0.05, 'HIGH': df['pos_x_ratio'] < 0.01}


    mask_dens = {
        'LOW': (df['lexical_density'] > 0.8) | (df['lexical_density'] < 0.3),
        'HIGH': (df['lexical_density'] < 0.7) & (df['lexical_density'] > 0.4)
    }
    mask_fog = {'LOW': df['gunning_fog'] > 12, 'HIGH': df['gunning_fog'] < 9}
    mask_sent = {
        'LOW': (df['avg_sentence_length'] > 25) | (df['avg_sentence_length'] < 3),
        'HIGH': (df['avg_sentence_length'] > 5) & (df['avg_sentence_length'] < 20)
    }
    scores = {
    "LOW": df.index[
        (mask_symb['LOW'] | mask_punct['LOW'] | mask_cc['LOW'] | mask_cw['LOW'] | mask_word['LOW'
        ]) & ((mask_stop['LOW'] | mask_x['LOW'] | mask_oovs['LOW'] | mask_num['LOW'
        ]) & (mask_sent['LOW'] | mask_fog['LOW'] | mask_dens['LOW']))].tolist(),

    "HIGH": df.index[
        (mask_symb['HIGH'] & mask_punct['HIGH'] & mask_cc['HIGH'] & mask_cw['HIGH'] & mask_word['HIGH'
    ]) | (mask_stop['HIGH'] & mask_x['HIGH'] & mask_oovs['HIGH'] & mask_num['HIGH'
    ]) | (mask_sent['HIGH'] & mask_fog['HIGH'] & mask_dens['HIGH'])].tolist()
    }

    return scores


def get_score(x, scores):
    if x in scores["LOW"]:
        return "LOW"
    elif x in scores["HIGH"]:
        return "HIGH"
    else:
        return "MEDIUM"


if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(PROJECT))
    replicate_to = os.path.join(base_dir, PROJECT)
    sl = Speakleash(replicate_to)
    ds = sl.get(PROJECT).ext_data
    df = pd.DataFrame(get_data(ds))
    scores = get_filtered(df)
    df['score'] = df.index.tolist()
    df['score'] = df['score'].apply(lambda x: get_score(x, scores))
    with open(f"{PROJECT}.pkl", "wb") as f:
        pickle.dump(df, f)
