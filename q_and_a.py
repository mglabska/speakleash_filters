import numpy as np
import os
import pandas as pd
import stylo_metrix as sm
import torch

from langdetect import detect
from speakleash import Speakleash
from transformers import AutoTokenizer, AutoModelForSequenceClassification

PROJECTS = [
    "forum_symfonika"
]
LIMIT = 10
TOKENIZER = AutoTokenizer.from_pretrained("cross-encoder/ms-marco-MiniLM-L-6-v2")
MODEL = AutoModelForSequenceClassification.from_pretrained("cross-encoder/ms-marco-MiniLM-L-6-v2")


def get_frame():
    texts = []
    for p in PROJECTS:
        for d in sl.datasets:
            if d.name == p:
                counter = 0
                for doc in d.data:
                    if detect(doc) == "pl":
                        counter = counter + 1
                        texts.append(doc)
                        if counter > LIMIT:
                            break
    return pd.DataFrame({'text': texts})


def get_stylo(df):
    df.text = df.text.apply(lambda x: x.split('\n'))
    metrics = sm.get_all_metrics('pl')
    to_analyse = [metrics[155], metrics[157]]
    stylo = sm.StyloMetrix('pl', metrics=to_analyse)
    metrics_list = []
    for t in df.text.values:
        metrics_list.append(stylo.transform(t))
    return metrics_list


def get_qa(metrics_list):
    questions = dict()
    answers = dict()
    for mi, m in enumerate(metrics_list):
        a = m['text'].loc[m['SY_S_DE'] > 0.5].index.tolist()
        q = m['text'].loc[m['SY_S_IN'] > 0.5].index.tolist()
        if len(m.text.iloc[q].values) > 0 and len(m.text.iloc[a].values) > 0:
            questions[mi] = m.text.iloc[q].values.tolist()
            answers[mi] = m.text.iloc[a].values.tolist()
        else:
            continue
    qa_df = pd.DataFrame(columns=['question', 'answer'])
    qa_df['question'] = questions.values()
    qa_df['answer'] = answers.values()
    return qa_df


def get_pairs(qa_df):
    pair_list = []
    for qr, an in qa_df[['question', 'answer']].values:
        for q in range(len(qr)):
            features = TOKENIZER(
                [qr[q]] * len(an),
                an,
                padding=True,
                truncation=True,
                return_tensors="pt"
            )
            MODEL.eval()
            with torch.no_grad():
                scores = MODEL(**features).logits
                pair_list.append([qr[q], an[np.argmax(scores)]])
    return pair_list


if __name__ == '__main__':
    base_dir = "./"
    replicate_to = os.path.join(base_dir, "datasets")
    sl = Speakleash(replicate_to)
    df1 = get_frame()
    metrics_list1 = get_stylo(df1)
    qa_df1 = get_qa(metrics_list1)
    pairs = get_pairs(qa_df1)
    print(pairs)
