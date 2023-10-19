import pandas as pd
import re
from ftfy import fix_text
from unidecode import unidecode

# Import data from json file
df = pd.read_json('data\\gg2013.json')

# Get only the body of the tweets (ignore username, etc.) and clean it up
text = df['text']
text = text.tolist()

for tweet in text:
    tweet = fix_text(tweet)
    tweet = unidecode(tweet)
    tweet = " ".join(tweet.split())

# Regular Expressions for winners
win_exprs = ['(wins|Wins|WINS|receives|received|won)(?= best| Best| BEST)']

# Regular Expressiosn for hosts
host_exprs = []

for tweet in text:
    for expr in win_exprs:
        # example regex use
        var = re.findall(r"(.+) " + expr + " (.+)", tweet)
        if var:
            print(var)
    for expr in host_exprs:
        pass