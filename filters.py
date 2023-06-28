import os


from speakleash import Speakleash

PROJECT = "project_gutenberg_pl_corpus"

def get_meta(PROJECT):
    base_dir = os.path.join(os.path.dirname(PROJECT))
    replicate_to = os.path.join(base_dir, PROJECT)
    sl = Speakleash(replicate_to)
    ds = sl.get(PROJECT).ext_data
    meta_list = []
    for doc in ds:
        _, meta = doc
        meta_list.append(meta)
    return meta_list

def sanity_check(meta_list):
    for meta in meta_list:
        return all(
            key in meta.keys() for key in [
            'camel_case',
            'punctuations',
            'symbols',
            'oovs',
            'pos_x',
            'lexical_density',
            'gunning_fog',
            'avg_sentence_length'
        ]
        )

def get_data(meta_list):
    for meta in meta_list:
        keys = ['punctuations', 'symbols', 'oovs', 'pos_x']
        for key in keys:
            meta[f'{key}_ratio'] = meta[f'{key}'] / meta['words']
    return meta_list


def get_filtered(meta_list):
    quality_format_low_list = []
    quality_text_low_list = []
    readability_low_list = []
    quality_text_high_list = []
    quality_format_high_list = []
    readability_high_list = []

    for meta in meta_list:
        mask_cc = {'LOW': meta['camel_case'] > 10, 'HIGH': meta['camel_case'] < 3}
        mask_punct = {
            'LOW': (meta['punctuations_ratio'] > 0.4) | (meta['punctuations_ratio'] < 0.1),
            'HIGH': (meta['punctuations_ratio'] > 0.1) & (meta['punctuations_ratio'] <= 0.35)
        }
        mask_symb = {'LOW': meta['symbols_ratio'] > 0.01, 'HIGH': meta['symbols_ratio'] == 0}

        mask_oovs = {'LOW': meta['oovs_ratio'] > 0.15, 'HIGH': meta['oovs_ratio'] < 0.05}
        mask_x = {'LOW': meta['pos_x_ratio'] > 0.07, 'HIGH': meta['pos_x_ratio'] < 0.01}

        mask_dens = {
            'LOW': (meta['lexical_density'] > 0.8) | (meta['lexical_density'] < 0.2),
            'HIGH': (meta['lexical_density'] < 0.6) & (meta['lexical_density'] > 0.4)
        }
        mask_fog = {'LOW': meta['gunning_fog'] > 14, 'HIGH': meta['gunning_fog'] < 10}
        mask_sent = {
            'LOW': (meta['avg_sentence_length'] > 35) | (meta['avg_sentence_length'] < 5),
            'HIGH': (meta['avg_sentence_length'] > 10) & (meta['avg_sentence_length'] < 26)
        }

        quality_format_low = mask_symb['LOW'] | mask_punct['LOW'] | mask_cc['LOW']
        quality_text_low = mask_x['LOW'] | mask_oovs['LOW']
        readability_low = mask_sent['LOW'] | mask_fog['LOW'] | mask_dens['LOW']

        quality_format_high = mask_symb['HIGH'] & mask_punct['HIGH'] & mask_cc['HIGH']
        quality_text_high = mask_x['HIGH'] & mask_oovs['HIGH']
        readability_high = mask_sent['HIGH'] & mask_fog['HIGH'] & mask_dens['HIGH']


        if quality_format_low:
            quality_format_low_list.append(meta['title'])
        if quality_text_low:
            quality_text_low_list.append(meta['title'])
        if readability_low:
            readability_low_list.append(meta['title'])
        if quality_format_high:
            quality_format_high_list.append(meta['title'])
        if quality_text_high:
            quality_text_high_list.append(meta['title'])
        if readability_high:
            readability_high_list.append(meta['title'])

    print(
        f"quality_format_low: {quality_format_low_list}\n",
        f"quality_text_low: {quality_text_low_list}\n",
        f"readability_low: {readability_low_list}\n",
        "---------------------------------------------\n"
        f"quality_format_high: {quality_format_high_list}\n",
        f"quality_text_high: {quality_text_high_list}\n",
        f"readability_high: {readability_high_list}\n",
        "---------------------------------------------\n"
        "---------------------------------------------\n"
        )


if __name__ == "__main__":
    meta_list = get_meta(PROJECT)
    sanity_check(meta_list)
    temp_meta_list = get_data(meta_list)
    get_filtered(temp_meta_list)





