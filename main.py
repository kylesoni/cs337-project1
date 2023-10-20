import pandas as pd
import re
from ftfy import fix_text
from unidecode import unidecode

# Import data from json file
df = pd.read_json('data\\gg2013.json')

# Import list of actors and movies from IMDB (uncomment when actually used so it doesn't take forever to run)
# actor_df = pd.read_csv('data\\name.basics.tsv', sep='\t')
# movie_df = pd.read_csv('data\\title.basics.tsv', sep='\t')

# actors = actor_df['primaryName']
# print(actors)

# Get only the body of the tweets (ignore username, etc.) and clean it up
text = df['text']
text = text.tolist()

for tweet in text:
    tweet = fix_text(tweet)
    tweet = unidecode(tweet)
    tweet = " ".join(tweet.split())

# Regular Expressions for winners
win_exprs = ['(wins|Wins|WINS|receives|received|won)(?= best| Best| BEST)', '(best(.+)|Best(.+)|BEST(.+))(?= goes to| Goes To| GOES TO)']

# Regular Expressiosn for hosts
host_exprs = ['(hosts?|Hosts?|HOSTS?|hosted by)[?!(will|should)]']

# Regular Expression for nominees
nom_exprs = ['[?!(pretend|fake|was not|is not)](nominees?|Nominees?|NOMINEES?|nominated?)']

presenter_exprs = ['(presenters?|Presenters?|PRESENTERS?|presented by|present(ed|s|ing))']

# Intialize Candidate Lists
win_candidates = []
win_count = -1

category_candidates = []
category_count = -1

test = []

for tweet in text:
    for expr in win_exprs:
        # example regex use
        var = re.findall(r"(.+) " + expr + " (.+)", tweet)
        if var:
            win_candidates.append([])
            win_count += 1
            category_candidates.append([])
            category_count += 1
            test.append(var)
            before = var[0][0].rsplit(None, var[0][0].count(' '))
            for i in range(0, len(before)):
                new_candidate = before[-1]
                for j in range(0, i):
                    new_candidate = before[len(before) - j - 2] + " " + new_candidate
                win_candidates[win_count].append(new_candidate)
            after = var[0][2].rsplit(None, var[0][2].count(' '))
            for i in range(0, len(after)):
                new_candidate = after[0]
                for j in range(0, i):
                    new_candidate = new_candidate + " " + after[1 + j]
                category_candidates[category_count].append(new_candidate)
            
    for expr in host_exprs:
        pass

#print(win_candidates[1])
#print(category_candidates[1])
#print(test[1][0][0])