import numpy as np
import os
import pandas as pd
import pickle


from speakleash import Speakleash

PROJECT = "forum_symfonika"
def get_data(ds):
    lst1 = []
    for doc in ds:
        txt, meta = doc
        meta['text'] = txt
        lst1.append(meta)
    df = pd.DataFrame(lst1)
    cols = ['punctuations', 'symbols', 'oovs', 'pos_x']
    for col in cols:
        df[f'{col}_ratio'] = df[col] / df['words']
    return df

def get_filtered(df):
    mask_cc = {'LOW': df['camel_case'] > 10, 'HIGH': df['camel_case'] < 3}
    mask_punct = {
        'LOW': (df['punctuations_ratio'] > 0.4) | (df['punctuations_ratio'] < 0.1),
        'HIGH': (df['punctuations_ratio'] > 0.1) & (df['punctuations_ratio'] <= 0.35)
    }
    mask_symb = {'LOW': df['symbols_ratio'] > 0.01,'HIGH': df['symbols_ratio'] == 0}

    mask_oovs = {'LOW': df['oovs_ratio'] > 0.15,  'HIGH': df['oovs_ratio'] < 0.05}
    mask_x = {'LOW': df['pos_x_ratio'] > 0.07, 'HIGH': df['pos_x_ratio'] < 0.01}

    mask_dens = {
        'LOW': (df['lexical_density'] > 0.8) | (df['lexical_density'] < 0.2),
        'HIGH': (df['lexical_density'] < 0.6) & (df['lexical_density'] > 0.4)
    }
    mask_fog = {'LOW': df['gunning_fog'] > 14, 'HIGH': df['gunning_fog'] < 10}
    mask_sent = {
        'LOW': (df['avg_sentence_length'] > 35) | (df['avg_sentence_length'] < 5),
        'HIGH': (df['avg_sentence_length'] > 10) & (df['avg_sentence_length'] < 26)
    }
    scores = {
    "LOW": df.index[
        (
                mask_symb['LOW'] | mask_punct['LOW'] | mask_cc['LOW']
        ) & (
                mask_x['LOW'] | mask_oovs['LOW']
        ) & (
                mask_sent['LOW'] | mask_fog['LOW'] | mask_dens['LOW']
        )].tolist(),

    "HIGH": df.index[
        (
                mask_symb['HIGH'] & mask_punct['HIGH'] & mask_cc['HIGH']
        ) & (
                mask_x['HIGH'] & mask_oovs['HIGH']
        ) & (
                mask_sent['HIGH'] & mask_fog['HIGH'] & mask_dens['HIGH']
        )].tolist()
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
