# cs337-project1

Group composed of Kyle Soni and Anges Vu

To run get the JSON and human readable output, simply run main.py. However, you will need to change a few things if you want to change the data set. They are all located at the top of main.py:
- master_year is the year of the award show
- json_file_path to the path of the input
- answers_file or gold_award_names to be the set of given gold_award_names (if the answer file is given, only the award names are scraped, the rest of the information is secure)
- you also may need to mess with the file paths of imdb data if your computer is set up differently

Sorry it's not better streamlined!

At the bottom of the file is what handles the output. The first output uses the gold award names directly to show what it looks like without cascading error, while the second output starts with only tweets for everything.

The corresponding json files append our_answersgold to the output that uses the gold award names and our_answers to the pure output without gold award names.

### Extra Notes:
- packages required are pandas, ftfy, unidecode, nltk, and spacy
- may need to run "python -m spacy download" en if spacy gets mad about not having the specific model
- feel free to comment out one of the outputs if only one of them should be accepted