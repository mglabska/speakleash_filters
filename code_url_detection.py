# This function takes dataset name and returns a dictionary with
# - document indices as keys
# -  list of code samples and urls as values

# The results are printed out


import os
import regex as re

from speakleash import Speakleash


PROJECT: str = "forum_parenting_pl_corpus"  # the name of dataset

PATTERN = re.compile(r"(<.*?>) | (https?://\S+|www\.\S+)")


# Creating a list of dataset text content
def get_data(ds):
    lst = []
    for doc in ds:  # iteration through all documents in a given dataset
        text, _ = doc
        lst.append(text)
    return lst


# Searching for code samples
def find_code(lst: list):
    code_dict = {}
    for tid, text in enumerate(lst):  # iterating through the list
        result = ["".join(x) for x in re.findall(PATTERN, str(text))]  # finding all code and url instances
        if len(result) > 0:  # filtering documents without code/url samples
            code_dict[tid] = result  # adding the result to a final dictionary (to be printed)
    return code_dict


if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(PROJECT))  # standard dataset downloading
    replicate_to = os.path.join(base_dir, PROJECT)
    sl = Speakleash(replicate_to)
    ds1 = sl.get(PROJECT).ext_data

    # Running functions
    lst1 = get_data(ds1)
    print(find_code(lst1))
