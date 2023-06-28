import os


from speakleash import Speakleash

PROJECT = "thesis"

def sanity_check(meta):
    return all(
        key in meta.keys() for key in [
        'camel_case',
        'punctuations',
        'symbols',
        'oovs',
        'pos_x',
    ]
    )

def get_data(temp_meta):
    keys = ['punctuations', 'symbols', 'oovs', 'pos_x']
    for key in keys:
        temp_meta[f'{key}_ratio'] = temp_meta[f'{key}'] / temp_meta['words']
    return temp_meta

def get_filtered(meta):
    mask_cc = {'LOW': meta['camel_case'] > 10, 'HIGH': meta['camel_case'] < 3}
    mask_punct = {
        'LOW': (meta['punctuations_ratio'] > 0.4) | (meta['punctuations_ratio'] < 0.1),
        'HIGH': (meta['punctuations_ratio'] > 0.1) & (meta['punctuations_ratio'] <= 0.35)
    }
    mask_symb = {'LOW': meta['symbols_ratio'] > 0.01, 'HIGH': meta['symbols_ratio'] == 0}

    mask_oovs = {'LOW': meta['oovs_ratio'] > 0.15, 'HIGH': meta['oovs_ratio'] < 0.05}
    mask_x = {'LOW': meta['pos_x_ratio'] > 0.07, 'HIGH': meta['pos_x_ratio'] < 0.01}

    if (
                mask_symb['LOW'] | mask_punct['LOW'] | mask_cc['LOW']
        ):
        return 'format_correct: False'
    elif (
                mask_x['LOW'] & mask_oovs['LOW']
        ):
        return 'format_correct: False'
    else:
        return 'format_correct: True'
    
def get_quality(meta):
    temp_meta = meta
    temp_meta = get_data(temp_meta)
    temp_meta['quality'] = get_filtered(temp_meta)
    meta['quality'] = temp_meta['quality']
    return meta


if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(PROJECT))
    replicate_to = os.path.join(base_dir, PROJECT)
    sl = Speakleash(replicate_to)
    ds = sl.get(PROJECT).ext_data
    for doc in ds:
        _, meta = doc
        sanity_check(meta)
        get_quality(meta)
