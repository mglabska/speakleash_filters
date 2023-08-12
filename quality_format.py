# This function takes the dataset name and returns a boolean value: True or False for a single document

# - True = document format correct (mostly)
# - False = document format incorrect

# The results are added to the meta dictionary in a file manifest
import os
from speakleash import Speakleash

PROJECT: str = "thesis"


# Checking, if the manifest contains all required keys
# meta is the very first dictionary, downloaded from the SpeakLeash file manifest
def sanity_check(meta: dict):
    return all(
        key in meta.keys() for key in [
            'camel_case',  # camelWords or CamelWords in the document
            'punctuations',  # number of punctuation marks
            'symbols',  # number of symbols
            'oovs',  # number of words out of vocabulary
            'pos_x',  # number of words of unidentified part-of-speech
        ]
    )


# Creating temporary variable: values to ratios (as more interpretable than quantity values).
# We don't need ratios for CamelCase though, because CC words are mostly incorrect according to Polish spelling rules
def get_data(meta: dict):
    keys = ['punctuations', 'symbols', 'oovs', 'pos_x']
    for key in keys:
        meta[f'{key}_ratio'] = meta[f'{key}'] / meta['words']
    return meta  # meta dict for further processing


# Filters for True/False value:
# Mask variables contain filters for specific values of meta parameters in a dictionary
def get_filtered(meta: dict):
    mask_cc = {'LOW': meta['camel_case'] > 10, 'HIGH': meta['camel_case'] < 3}
    mask_punct = {
        'LOW': (meta['punctuations_ratio'] > 0.4) | (meta['punctuations_ratio'] < 0.1),
        'HIGH': (meta['punctuations_ratio'] > 0.1) & (meta['punctuations_ratio'] <= 0.35)
    }
    mask_symb = {'LOW': meta['symbols_ratio'] > 0.01, 'HIGH': meta['symbols_ratio'] == 0}

    mask_oovs = {'LOW': meta['oovs_ratio'] > 0.15, 'HIGH': meta['oovs_ratio'] < 0.05}
    mask_x = {'LOW': meta['pos_x_ratio'] > 0.07, 'HIGH': meta['pos_x_ratio'] < 0.01}

    if (
                mask_symb['LOW'] | mask_punct['LOW'] | mask_cc['LOW']  # checking for non-alphanumeric values and typos
    ):
        return 'format_correct: False'  # 'LOW' means that the format is incorrect, hence False
    elif (
                mask_x['LOW'] & mask_oovs['LOW']  # checking for unknown part-of-speech or words out of vocabulary
    ):
        return 'format_correct: False'  # 'LOW' means that there is something wrong with the text, hence False
    else:
        return 'format_correct: True'


# Final function, combining all above:
# Adding another key-value pair ('quality': -> boolean) to the meta dictionary in a file manifest
def get_quality(meta):
    temp_meta = meta  # Creating a temporary variable for calculation
    temp_meta = get_data(temp_meta)
    temp_meta['quality'] = get_filtered(temp_meta)
    meta['quality'] = temp_meta['quality']  # Returning results to the original meta dictionary

    print(meta)
    return meta


if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(PROJECT))  # standard dataset downloading
    replicate_to = os.path.join(base_dir, PROJECT)
    sl = Speakleash(replicate_to)
    ds = sl.get(PROJECT).ext_data
    for doc in ds:  # iteration through all documents in a given dataset
        _, meta1 = doc
        sanity_check(meta1)
        get_quality(meta1)
