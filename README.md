# speakleash_filters

First filters for SpeakLeash files quality assessment. 


**filters.py** — accepts dataset name, contains filters classified against three categories: *format_quality*, *text_quality* and *readability*. For each error category a list of indices of *LOW* and *HIGH*-quality documents is printed.

**filters_df_labels.py** — accepts dataset name, contains filters for final quality score (*LOW*, *MEDIUM*, *HIGH*) for each document, returns a dataframe with one final label per document assigned.

**quality.py** (*to be implemented in SpeakLeash environment*) — accepts dataset name, contains filters for final quality score (*LOW*, *MEDIUM*, *HIGH*) for each document, returns a final label for each document (to be included in speakleash file manifest).

**quality_format.py** (*to be implemented in SpeakLeash environment, for internal use only*) — accepts dataset name, contains filters for format quality score for each document, returns a Boolean value for *format_correct* metric (to be included in speakleash file manifest). To be used with OCR-ed documents.
