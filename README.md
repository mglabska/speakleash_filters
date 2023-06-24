# speakleash_filters

First filters for SpeakLeash datasets quality assessment. 


**filters.py** — contains filters classified against three categories: *format_quality*, *text_quality* and *readability*. For **each error category** a list of indices of *LOW* and *HIGH*-quality documents is printed.


**filters_df_labels.py** — contains filters for **final score** (*LOW*, *MEDIUM*, *HIGH*) for each document, returns a dataframe with one final label per document assigned.
