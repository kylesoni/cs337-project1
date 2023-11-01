import pandas as pd
import re
from ftfy import fix_text
from unidecode import unidecode
import json
import imdb
from nltk import edit_distance
import numpy as np
import spacy
import gzip
import urllib
from collections import Counter

# Set year of awards
master_year = 2013

# Import data from json file
json_file_path = 'data\\gg2013.json'
df = pd.read_json(json_file_path)

# Get IMDB data
answers_file = open('data\\gg2013answers.json')
answers = json.load(answers_file)

# Get syntactic parser
spacy_model = spacy.load("en_core_web_sm")

ia = imdb.Cinemagoer()

# Get subset of imdb data based on year of awards
#urllib.request.urlretrieve('https://datasets.imdbws.com/name.basics.tsv.gz', 'data\\name.basics.tsv.gz')
#urllib.request.urlretrieve('https://datasets.imdbws.com/title.basics.tsv.gz', 'data\\title.basics.tsv.gz')
imdb_names = gzip.open('data\\name.basics.tsv.gz')
content = str(imdb_names.read())
imdb_lines = content.split('\\n')
imdb_fields = []
for line in imdb_lines:
    imdb_fields.append(line.split('\\t'))

imdb_names = []

for name in imdb_fields[1:len(imdb_fields)-1]:
    # Determine if the person was active during the award show
    if (name[2] == '\\\\N'):
        continue
    if (name[3] == '\\\\N' and int(name[2]) < master_year - 5):
        imdb_names.append(name[1])
    elif (name[3] == '\\\\N'):
        continue
    else:
        if (int(name[3]) < int(name[2]) or int(name[3]) < master_year - 5 or int(name[2]) > master_year + 5):
            pass
        else:
            imdb_names.append(name[1])

imdb_titles = gzip.open('data\\title.basics.tsv.gz')
content = str(imdb_titles.read())
imdb_lines = content.split('\\n')
imdb_fields = []
for line in imdb_lines:
    imdb_fields.append(line.split('\\t'))

imdb_titles = []

for name in imdb_fields[1:len(imdb_fields)-1]:
    if (name[1] not in ["movie", "short", "tvseries"]):
        continue
    if (name[5] == '\\\\N'):
        continue
    if (name[6] == '\\\\N'):
        if (int(name[5]) > master_year - 5):
            imdb_titles.append(name[2])
    elif (int(name[6]) < master_year + 5 and int(name[5]) > master_year - 5):
        imdb_titles.append(name[2])   

# Keep track of tweets we've already parsed
parsed_tweets = {}

# Get only the body of the tweets (ignore username, etc.) and clean it up
text = df['text']
text = text.tolist()

for tweet in text:
    tweet = fix_text(tweet)
    tweet = unidecode(tweet)
    tweet = " ".join(tweet.split())

# Get "Gold" Award Names from the answer file
gold_award_names = answers['award_data'].keys()
gold_nominees = []
for val in answers['award_data'].values():
    gold_nominees.append(val['nominees'])

# Regular Expressiosn for hosts
host_exprs = ['(hosts?|Hosts?|HOSTS?|hosted by)[?!(will|should)]']

# Regular Expression for nominees
nom_exprs = ['[?!(pretend|fake|was not|is not)](nominees?|Nominees?|NOMINEES?|nominated?)']

presenter_exprs = ['(presenters?|Presenters?|PRESENTERS?|presented by|present(ed|s|ing))']

# Intialize Candidate Lists
win_candidates = []
win_count = -1


def get_hosts():
    hosts_candidates = [{}]
    host_pattern = '(hosts?|Hosts?|HOSTS?|hosted by)[?!(will|should)]'
    tweets_of_interest = df.text[df.text.str.contains(host_pattern)].values.tolist()
    for tweet in tweets_of_interest:
        if 'next year' in tweet:
            continue
        find_name(tweet, hosts_candidates[0])

    hosts_candidates[0] = Counter(hosts_candidates[0])
    hosts_ordered = hosts_candidates[0].most_common(len(hosts_candidates[0]))
    print(hosts_ordered)
    max_count = hosts_ordered[0][1]
    hosts_candidates = []
    for i in range(len(hosts_ordered)):
        if hosts_ordered[i][1] > max_count * 0.5:
            hosts_candidates.append(hosts_ordered[i][0])
        else:
            break
    print(hosts_candidates)

def get_award_names():
    award_names_candidates = []
    return award_names_candidates

def get_presenters_gold():
    presenter_candidates = [[] for i in range(len(gold_award_names))]
    return presenter_candidates

def get_nominees_gold():
    nominees_candidates = [[] for i in range(len(gold_award_names))]
    return nominees_candidates

def get_winners_gold():
    win_candidates = [{} for i in range(len(gold_award_names))]
    # Filter tweets down to winners only
    win_pattern = '(wins|Wins|WINS|receiv(es|ed)|won)(?= best| Best| BEST)|(best(.+)|Best(.+)|BEST(.+))(?= goes to| Goes To| GOES TO)'
    tweets_of_interest = df.text[df.text.str.contains(win_pattern)].values.tolist()
    for tweet in tweets_of_interest:
        # Figure out if tweet is relevant to award category we are looking at
        max_count = 0
        best_i = -1
        best_award = ""
        for i, award in enumerate(gold_award_names):
            count = 0
            for match in key_award_words[award]:
                if match.lower() in tweet.lower():
                    count += 1
            # Move on to next category if not enough matches were found in the tweet
            if (count < 2):
                continue
            # Find the best match for the category, and prefer shorter categories if there's a tie
            if (count > max_count):
                max_count = count
                best_i = i
                best_award = award
            elif (count == max_count):
                if (len(award.split()) < len(best_award.split())):
                    max_count = count
                    best_i = i
                    best_award = award

        if best_i == -1:
            continue

        # Reset the names because I'm lazy
        i = best_i
        award = best_award
        # Determine if we should look for a person or movie titles:
        aw_type = ""
        name_types = ["director", "actor", "actress", "cecil", "demille"]
        for n_t in name_types:
            if n_t in award:
                aw_type = "person"
                break
        
        if (aw_type == "person"):
            find_name(tweet, win_candidates[i])

    for i in range(len(win_candidates)):
        win_candidates[i] = Counter(win_candidates[i])
        if len(win_candidates[i]) > 0:
            win_candidates[i] = win_candidates[i].most_common(1)[0][0]
        else:
            win_candidates[i] = "not found"
    print(win_candidates)


def find_name(tweet, current_dict):
    name_pattern = re.compile('[A-Z][a-z]*\s[\w]+')
    if tweet not in parsed_tweets:
        parsed_tweets[tweet] = spacy_model(tweet).ents
    for ent in parsed_tweets[tweet]:
        stripped_ent = ent.text.strip()
        if name_pattern.match(stripped_ent) is None:
            continue
        if ent.label_ == "PERSON" and stripped_ent in imdb_names:
            if stripped_ent in current_dict:
                current_dict[stripped_ent] += 1
            else:
                current_dict[stripped_ent] = 1

#find_name("Best Supporting Actor in a Movie goes to Christoph Waltz for Django Unchained. Haven't seen it yet. #GoldenGlobes")

def get_keywords_from_awards(award_names):
    global key_award_words
    key_award_words = {}
    for award in award_names:
        for tok in spacy_model(award):
            if tok.pos_ == "NOUN" or tok.pos_ == "ADJ" or tok.pos_ == "VERB":
                if award in key_award_words:
                    key_award_words[award].append(str(tok))
                else:
                    key_award_words[award] = [str(tok)]
        if award not in key_award_words:
            for tok in spacy_model(award):
                if award in key_award_words:
                    key_award_words[award].append(str(tok))
                else:
                    key_award_words[award] = [str(tok)]

get_hosts()
get_keywords_from_awards(gold_award_names)
get_winners_gold()
#print(key_award_words)

def output(hosts, award_names, presenters, nominees, winners):
    output = "Hosts:"
    for h in hosts:
        output += h + ", "
    output = output[:-2] + "\n\n"
    for i in range(len(award_names)):
        output += "Award " + award_names[i] + "\n"
        output += "Presenters: "
        for presenter in presenters[i]:
            output += presenter + ", "
        output = output[:-2] + "\nNominees: "
        for nominee in nominees[i]:
            output += nominee + ", "
        output = output[:-2] + "\nWinner: " + winners[i] + "\n\n"
    
    json_output = {}
    json_output['hosts'] = hosts
    json_output["award_data"] = {}
    for i in range(len(award_names)):
        json_output["award_data"][award_names[i]] = {"nominees": nominees[i], "presenters": presenters[i], "winner": winners[i]}
    with open(json_file_path.replace(".json","") + "our_answers.json", 'w') as data:
        json.dump(json_output, data)

    return output

"""
def old_get_winners():
    # Regular Expressions for winners
    before_win_exprs_search = ['(wins|Wins|WINS|receiv(es|ed)|won)(?= best| Best| BEST)'] 
    after_win_exprs_search = ['(best(.+)|Best(.+)|BEST(.+))(?= goes to| Goes To| GOES TO)']

    before_win_exprs = ['(wins|Wins|WINS|receiv(es|ed)|won)'] 
    after_win_exprs = ['(goes to| Goes To| GOES TO)']
    win_candidates = [[] for i in range(len(gold_categories))]
    before = filt_expr[0][0].rsplit(None, filt_expr[0][0].count(' '))
    after = filt_expr[0][2].rsplit(None, filt_expr[0][0].count(' '))
    poss_wins = []
    for tweet in text:
        for i, expr in enumerate(before_win_exprs_search):
            if re.search(expr, tweet):
                var = re.findall(r"(.+) " + before_win_exprs[i] + " (.+)", tweet)
                if var:
                    winners_from_cats_noms(gold_categories, var, "before")
        for i, expr in enumerate(after_win_exprs):
            if re.search(expr, tweet):
                var = re.findall(r"(.+) " + after_win_exprs[i] + " (.+)", tweet)
                if var:
                    winners_from_cats_noms(gold_categories, var, "after")
    if order == "before":
        candidate_loc = before
        award_name_loc = after
        # Construct list of possible names for before expressions
        for i in range(len(candidate_loc)):
            candidate = candidate_loc[-1]
            if i == 0:
                poss_wins.append(candidate_loc[-1])
            else:
                for j in range(i):
                    candidate = candidate_loc[-2 - j] + " " + candidate
                poss_wins.append(candidate)
    else:
        candidate_loc = after
        award_name_loc = before
        # Construct list of possible names for after expressions
        for i in range(len(candidate_loc)):
            candidate = candidate_loc[0]
            if i == 0:
                poss_wins.append(candidate_loc[0])
            else:
                for j in range(i):
                    candidate =  candidate + " " + candidate_loc[1 + j]
                poss_wins.append(candidate)

    #print(poss_wins)
    award_name_loc = [x.lower() for x in award_name_loc]

    # Try to best match category found to the gold standard list
    category_index = -1
    weights = [0 for x in range(len(gold_categories))]
    for i, gold_cat in enumerate(categories):
        for expr in award_name_loc:
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
                win_candidates[category_index].append(new)
                print(win_candidates)
            else:
                new_movie = imdb_check_title(can, win_candidates[category_index])
                if new_movie !=0:
                    win_candidates[category_index].append(new_movie)
                    #print(win_candidates)
    return win_candidates

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

def imdb_check_title(name, candidate_list):
    for i in range(len(candidate_list)):
        if edit_distance(name, candidate_list[i][0]) < 2:
            candidate_list[i] = (candidate_list[i][0], candidate_list[i][1] + 10)
            return 0
    try:
            title = ia.search_movie(name)
    except:
        pass
    else:
        if len(title) > 0 and edit_distance(name, title[0]['title']) < 4:
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

print(total_votes(win_candidates, 1))"""