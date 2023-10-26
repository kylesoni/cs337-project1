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

gold_categories = ["Best Screenplay - Motion Picture", 
                   "Best Director - Motion Picture", 
                   "Best Performance by an Actress in a Television Series - Comedy or Musical", 
                   "Best Foreign Language Film",
                   "Best Performance by an Actor in a Supporting Role in a Motion Picture",
                   "Best Performance by an Actress in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television",
                   "Best Motion Picture - Comedy or Musical",
                   "Best Actress in a Motion Picture - Comedy or Musical",
                   "Best Actress in a Motion Picture - Drama"]
gold_nominees = [["Zero Dark Thirty", "Lincoln", "Silver Linings Playbook", "Argo", "Django Unchained"], 
                 ["Ben Affleck", "Kathryn Bigelow", "Ang Lee", "Steven Spielberg", "Quentin Tarantino"],
                 ["Zooey Deschanel", "Tina fey", "Julia Louis-Dreyfus", "Amy Poehler", "Lena Dunham"],
                 ["The Intouchables", "Kon Tiki", "A Royal Affair", "Rust and Bone", "Amour"],
                 ["Alan Arkin", "Leonardo Dicaprio", "Philip Seymour Hoffman", "Tommy Lee Jones", "Christoph Waltz"],
                 ["Hayden Panettiere", "Archie Panjabi", "Sarah Paulson", "Sofia Vergara", "Maggie Smith"],
                 ["The Best Exotic Marigold Hotel", "Moonrise Kingdom", "Salmon Fishing in the Yemen", "Silver Linings Playbook", "Les Miserables"],
                 ["Emily Blunt", "Judi Dench", "Maggie Smith", "Meryl Streep", "Jennifer Lawrence"],
                 ["Jessica Chastain"]]
win_candidates = [[] for i in range(len(gold_categories))]

def winners_from_cats_noms(categories, nominees, tweet, filt_expr):
    for cat_i, cat in enumerate(categories):
        if re.search(cat, tweet):
                before = filt_expr[0][0].rsplit(None, 0)
                for nom in nominees[cat_i]:
                     if re.search(nom, str(before[0])):
                          win_candidates[cat_i].append((nom, 10))
                after = filt_expr[0][0].rsplit(None, 0)
                for nom in nominees[cat_i]:
                     if re.search(nom, str(after[0])):
                          win_candidates[cat_i].append((nom, 10))

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