import pandas as pd
import re
from ftfy import fix_text
from unidecode import unidecode
import json
import imdb
from nltk import edit_distance
import numpy as np

# Import data from json file
df = pd.read_json('data\\gg2013.json')

ia = imdb.Cinemagoer()
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

# for tweet in text:
#     for expr in win_exprs:
#         # example regex use
#         var = re.findall(r"(.+) " + expr + " (.+)", tweet)
#         if var:
#             win_candidates.append([])
#             win_count += 1
#             category_candidates.append([])
#             category_count += 1
#             test.append(var)
#             before = var[0][0].rsplit(None, var[0][0].count(' '))
#             for i in range(0, len(before)):
#                 new_candidate = before[-1]
#                 for j in range(0, i):
#                     new_candidate = before[len(before) - j - 2] + " " + new_candidate
#                 win_candidates[win_count].append(new_candidate)
#             after = var[0][2].rsplit(None, var[0][2].count(' '))
#             for i in range(0, len(after)):
#                 new_candidate = after[0]
#                 for j in range(0, i):
#                     new_candidate = new_candidate + " " + after[1 + j]
#                 category_candidates[category_count].append(new_candidate)
            
    # for expr in host_exprs:
    #     pass

#print(win_candidates[1])
#print(category_candidates[1])
#print(test[1][0][0])

answers_file = open('data\\gg2013answers.json')
answers = json.load(answers_file)
gold_categories = answers['award_data'].keys()
gold_nominees = []
for val in answers['award_data'].values():
    gold_nominees.append(val['nominees'])
win_candidates = [[] for i in range(len(gold_categories))]

def winners_from_cats_noms(categories, nominees, tweet, filt_expr):
    before = filt_expr[0][0].rsplit(None, filt_expr[0][0].count(' '))
    after = filt_expr[0][2].rsplit(None, filt_expr[0][0].count(' '))
    after = [x.lower() for x in after]
    poss_wins = []

    # Construct list of possible names
    if len(before) > 3:
        poss_wins.append(before[-2] + " " + before[-1])
        poss_wins.append(before[-3] + " " + before[-2] + " " + before[-1])
    elif len(before) > 2:
        poss_wins.append(before[-2] + " " + before[-1])

    # Try to best match category found to the gold standard list
    category_index = -1
    weights = [0 for x in range(len(gold_categories))]
    for i, gold_cat in enumerate(categories):
        for expr in after:
            if expr in gold_cat:
                weights[i] += 1
    if max(weights) > 1:
        category_index = np.argmax(weights)
        if type(category_index) is list:
            category_index = category_index[0]

    if category_index >= 0:
        for can in poss_wins:
            new = imdb_check_name(can, win_candidates[category_index])
            if new != 0:
                print("made it this far")
                win_candidates[category_index].append(new)
    #print(win_candidates)

def imdb_check_name(name, candidate_list):
    for i in range(len(candidate_list)):
        if edit_distance(name, candidate_list[i][0]) < 2:
            candidate_list[i] = (candidate_list[i][0], candidate_list[i][1] + 10)
            return 0
    try:
            person = ia.search_person(name)
    except:
        pass
    else:
        if len(person) > 0 and edit_distance(name, person[0]['name']) < 4:
            return (name, 10)
    return 0    

def total_votes(candidate_list, max_winner):
    actual_candidates = [[] for x in range(len(candidate_list))]
    weights = [[] for x in range(len(candidate_list))]
    for i, category in enumerate(candidate_list):
        for thing in category:
            if thing[0] not in actual_candidates[i]:
                actual_candidates[i].append(thing[0])
                weights[i].append(thing[1])
            else:
                weights[i][actual_candidates[i].index(thing[0])] += thing[1]
        actual_candidates[i] = [x for _, x in sorted(zip(weights[i], actual_candidates[i]), key=lambda pair: pair[0], reverse=True)]
    for i in range(len(actual_candidates)):
        if len(actual_candidates[i]) > 0:
            actual_candidates[i] = actual_candidates[i][0]
    return actual_candidates

for tweet in text:
    for expr in win_exprs:
        var = re.findall(r"(.+) " + expr + " (.+)", tweet)
        if var:
            winners_from_cats_noms(gold_categories, gold_nominees, tweet, var)

print(total_votes(win_candidates, 1))