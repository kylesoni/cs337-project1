import pandas as pd
import re

# Import data from json file
df = pd.read_json('data\\gg2013.json')

# Get only the body of the tweets (ignore username, etc.) and clean it up
text = df['text']
clean_text = text.str.replace(r'[^a-zA-Z0-9 ]+', '').str.replace(r'\s+', ' ').str.strip()

# Regular Expressions for winners
win_exprs = ['wins']

for expr in win_exprs:
    matched_tweets = df.text[df.text.str.match(expr)].to_list()
    print(matched_tweets[0])
    for tweet in matched_tweets:
        pass