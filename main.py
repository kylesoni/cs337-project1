import pandas as pd
import re
from ftfy import fix_text
from unidecode import unidecode
import json
from nltk import edit_distance
import spacy
import gzip
import urllib
from collections import Counter

# Set year of awards
master_year = 2013

# Import data from json file
json_file_path = 'data\\gg2013.json'
df = pd.read_json(json_file_path)

# Get answers data
# Note that we don't use this for anything besides getting the gold award names which we're allowed to use (please no automatic 0!)
# Feel free to replace this or the corresponding "gold_award_names" with a file that's just the award names
answers_file = open('data\\gg2013answers.json')
answers = json.load(answers_file)

# Get "Gold" Award Names from the answer file
gold_award_names = answers['award_data'].keys()

# Get syntactic parser
spacy_model = spacy.load("en_core_web_sm")

# Get subset of imdb data based on year of awards
# After downloading once, you can comment out the urls to save time
urllib.request.urlretrieve('https://datasets.imdbws.com/name.basics.tsv.gz', 'data\\name.basics.tsv.gz')
urllib.request.urlretrieve('https://datasets.imdbws.com/title.basics.tsv.gz', 'data\\title.basics.tsv.gz')
imdb_names = gzip.open('data\\name.basics.tsv.gz')
content = str(imdb_names.read())
imdb_lines = content.split('\\n')
imdb_fields = []
for line in imdb_lines:
    imdb_fields.append(line.split('\\t'))

imdb_names = {}

for name in imdb_fields[1:len(imdb_fields)-1]:
    # Determine if the person was active during the award show
    if (name[2] == '\\\\N'):
        continue
    if (name[3] == '\\\\N' and int(name[2]) < master_year - 5):
        imdb_names[name[1]] = 1
    elif (name[3] == '\\\\N'):
        continue
    else:
        if (int(name[3]) < int(name[2]) or int(name[3]) < master_year - 5 or int(name[2]) > master_year + 5):
            pass
        else:
            imdb_names[name[1]] = 1

imdb_titles = gzip.open('data\\title.basics.tsv.gz')
content = str(imdb_titles.read())
imdb_lines = content.split('\\n')
imdb_fields = []
for line in imdb_lines:
    imdb_fields.append(line.split('\\t'))

imdb_titles = {}

for name in imdb_fields[1:len(imdb_fields)-1]:
    if (name[1] not in ["movie", "short", "tvseries"]):
        continue
    if (name[5] == '\\\\N'):
        continue
    if (name[6] == '\\\\N'):
        if (int(name[5]) > master_year - 5):
            imdb_titles[name[2]] = 1
    elif (int(name[6]) < master_year + 5 and int(name[5]) > master_year - 5):
        imdb_titles[name[2]] = 1  

# Keep track of tweets we've already parsed
parsed_tweets = {}

# Get only the body of the tweets (ignore username, etc.) and clean it up
text = df['text']
text = text.tolist()

for tweet in text:
    tweet = fix_text(tweet)
    tweet = unidecode(tweet)
    tweet = " ".join(tweet.split())

def get_best_dressed():
    best_dressed_candidates = {}
    best_dressed_pattern = '(Best Dressed|best dressed|gorgeous|beautiful|pretty|stunning|amazing|handsome|favorite)'
    fashion_dict = ['dress', 'skirt', 'tux', 'tuxedo', 'suit']
    tweets_of_interest = df.text[df.text.str.contains(best_dressed_pattern)].values.tolist()
    for tweet in tweets_of_interest:
        for fash in fashion_dict:
            if fash in tweet:
                find_name(tweet, best_dressed_candidates)
                break
    best_dressed_candidates = Counter(best_dressed_candidates)
    best_dressed_ordered = best_dressed_candidates.most_common(len(best_dressed_candidates))
    #print(hosts_ordered)
    max_count = best_dressed_ordered[0][1]
    best_dressed_candidates = []
    for i in range(len(best_dressed_ordered)):
        if best_dressed_ordered[i][1] > max_count * 0.33:
            best_dressed_candidates.append(best_dressed_ordered[i][0])
        else:
            break
    return best_dressed_candidates

def get_worst_dressed():
    worst_dressed_candidates = {}
    worst_dressed_pattern = '(Worst Dressed|worst dressed|ugly|hideous|terrible|bad|weird|awful|disappointing|least favorite|don\'t like)'
    fashion_dict = ['dress', 'skirt', 'tux', 'tuxedo', 'suit']
    tweets_of_interest = df.text[df.text.str.contains(worst_dressed_pattern)].values.tolist()
    for tweet in tweets_of_interest:
        for fash in fashion_dict:
            if fash in tweet:
                find_name(tweet, worst_dressed_candidates)
                break
    worst_dressed_candidates = Counter(worst_dressed_candidates)
    worst_dressed_ordered = worst_dressed_candidates.most_common(len(worst_dressed_candidates))
    #print(hosts_ordered)
    max_count = worst_dressed_ordered[0][1]
    worst_dressed_candidates = []
    for i in range(len(worst_dressed_ordered)):
        if worst_dressed_ordered[i][1] > max_count * 0.33:
            worst_dressed_candidates.append(worst_dressed_ordered[i][0])
        else:
            break
    return worst_dressed_candidates

def get_most_controversial():
    liked_candidates = {}
    disliked_candidates = {}
    liked_pattern = '(love|happy|excited|yay|yes)'
    disliked_pattern = '(hate|don\'t like|angry|no)'
    positive_tweets = df.text[df.text.str.contains(liked_pattern)].values.tolist()
    for tweet in positive_tweets:
        find_name(tweet, liked_candidates)
    negative_tweets = df.text[df.text.str.contains(disliked_pattern)].values.tolist()
    for tweet in negative_tweets:
        find_name(tweet, disliked_candidates)

    controversial_candidates = {x:liked_candidates[x]-disliked_candidates[x] for x in liked_candidates if x in disliked_candidates}
    #print(controversial_candidates)
    if len(controversial_candidates) == 0:
        ["no one was controversial"]
    most_controversial = {}
    for key, value in controversial_candidates.items():
        most_controversial[key] = abs(value)
    most_controversial = Counter(most_controversial)
    most_controversial_ordered = most_controversial.most_common(len(most_controversial))
    #print(most_controversial_ordered)
    most_controversial = []
    for i in range(4):
        most_controversial.append(most_controversial_ordered[-1 - i][0])
    return most_controversial            

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
    #print(hosts_ordered)
    max_count = hosts_ordered[0][1]
    hosts_candidates = []
    for i in range(len(hosts_ordered)):
        if hosts_ordered[i][1] > max_count * 0.5:
            hosts_candidates.append(hosts_ordered[i][0])
        else:
            break
    return hosts_candidates

def get_award_names():
    award_names_candidates = []
    current_index = -1
    before_exprs = ['(goes to| Goes To| GOES TO)', '(presenters?|Presenters?|PRESENTERS?|presented by|present(ed|s|ing))']
    after_exprs = ['(wins|Wins|WINS|receiv(es|ed)|won)(?= best| Best| BEST)|(best(.+)|Best(.+)|BEST(.+))', '(is nominated|nominees for|nominees of)']
    for expr in before_exprs:
        tweets_of_interest = df.text[df.text.str.contains(expr)].values.tolist()
        for tweet in tweets_of_interest:
            var = re.findall(r"(.+) " + expr + " (.+)", tweet)
            if var:
                before = var[0][0].rsplit(None, var[0][0].count(' '))
                for i in range(len(before)):
                    candidate = before[-1]
                    if i == 0:
                        award_names_candidates.append([before[-1]])
                        current_index += 1
                    else:
                        for j in range(i):
                            if "#" in before[-2 - j]:
                                break
                            candidate = before[-2 - j] + " " + candidate
                            if 'best' not in candidate and 'Best' not in candidate:
                                continue
                            award_names_candidates[current_index].append(candidate)
    for expr in after_exprs:
        tweets_of_interest = df.text[df.text.str.contains(expr)].values.tolist()
        for tweet in tweets_of_interest:
            var = re.findall(r"(.+) " + expr + " (.+)", tweet)
            if var and len(var[0]) > 3:
                after = var[0][2].rsplit(None, var[0][0].count(' '))
                for i in range(len(after)):
                    candidate = after[0]
                    if i == 0:
                        if 'best' not in after[0]:
                            break
                        award_names_candidates.append([after[0]])
                        current_index += 1
                    else:
                        for j in range(i):
                            if "#" in after[1 + j]:
                                break
                            candidate =  candidate + " " + after[1 + j]
                            if 'best' not in candidate and 'Best' not in candidate:
                                continue
                            award_names_candidates[current_index].append(candidate)
    merged_awards = {}
    final_award_candidates = []
    for award_list in award_names_candidates:
        for award in award_list:
            if ('best' in award.split(' ', 1)[0] or 'Best' in award.split(' ', 1)[0]):
                if award in merged_awards:
                    merged_awards[award] += 1
                else:
                    merged_awards[award] = 1
    merged_awards = Counter(merged_awards)
    sorted_merged_awards = merged_awards.most_common(len(merged_awards))
    too_far = 1
    max_count = sorted_merged_awards[0][1]
    for j in range(1, len(sorted_merged_awards)):
        if too_far < 20 and sorted_merged_awards[j][1] > max_count * 0.05 :
            final_award_candidates.append(sorted_merged_awards[j][0])
            too_far += 1
    return final_award_candidates

def get_presenters_gold(award_names):
    presenter_candidates = [{} for i in range(len(award_names))]
    presenter_pattern = '(presenters?|Presenters?|PRESENTERS?|presented by|present(ed|s|ing))'
    tweets_of_interest = df.text[df.text.str.contains(presenter_pattern)].values.tolist()
    for tweet in tweets_of_interest:
        max_count = 0
        best_i = -1
        best_award = ""
        for i, award in enumerate(award_names):
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

        find_name(tweet, presenter_candidates[i])
    
    #print(presenter_candidates)
    for i in range(len(presenter_candidates)):
        presenter_candidates[i] = Counter(presenter_candidates[i])
        pres_ordered = presenter_candidates[i].most_common(len(presenter_candidates[i]))
        if len(presenter_candidates[i]) > 0:
            presenter_candidates[i] = [pres_ordered[0][0]]
            too_far = 1
            max_count = pres_ordered[0][1]
            for j in range(1, len(pres_ordered)):
                if too_far < 4 and pres_ordered[j][1] > max_count * 0.1:
                    presenter_candidates[i].append(pres_ordered[j][0])
                    too_far += 1
        else:
            presenter_candidates[i] = ["not found"]
    #print(presenter_candidates)
    return presenter_candidates

def get_nominees_gold(award_names):
    nominees_candidates = [{} for i in range(len(award_names))]
    nominee_pattern = '[?!(pretend|fake|was not|is not)](nominees?|Nominees?|NOMINEES?|nominated?)|(wins|Wins|WINS|receiv(es|ed)|won)(?= best| Best| BEST)|(best(.+)|Best(.+)|BEST(.+))(?= goes to| Goes To| GOES TO)'
    tweets_of_interest = df.text[df.text.str.contains(nominee_pattern)].values.tolist()
    for tweet in tweets_of_interest:
        # Figure out if tweet is relevant to award category we are looking at
        max_count = 0
        best_i = -1
        best_award = ""
        for i, award in enumerate(award_names):
            count = 0
            for match in key_award_words[award]:
                if match.lower() in tweet.lower():
                    count += 1
            # Move on to next category if not enough matches were found in the tweet
            if (count < 1):
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
            find_name(tweet, nominees_candidates[i])
        else:
            find_title(tweet, nominees_candidates[i], 'is nominated', "before")
            find_title(tweet, nominees_candidates[i], '(nominees for|nominees of)', "before")

    #print(nominees_candidates)
    for i in range(len(nominees_candidates)):
        nominees_candidates[i] = Counter(nominees_candidates[i])
        noms_ordered = nominees_candidates[i].most_common(len(nominees_candidates[i]))
        if len(nominees_candidates[i]) > 0:
            nominees_candidates[i] = [noms_ordered[0][0]]
            too_far = 1
            if len(noms_ordered) > 1:
                max_count = noms_ordered[1][1]
            else:
                max_count = noms_ordered[0][1]
            for j in range(1, len(noms_ordered)):
                if too_far < 4 or (too_far < 5 and noms_ordered[j][1] > max_count * 0.1):
                    nominees_candidates[i].append(noms_ordered[j][0])
                    too_far += 1
        else:
            nominees_candidates[i] = ["not found"]
    #print(nominees_candidates)
    return nominees_candidates

def get_winners_gold(award_names):
    win_candidates = [{} for i in range(len(award_names))]
    # Filter tweets down to winners only
    win_pattern = '(wins|Wins|WINS|receiv(es|ed)|won)(?= best| Best| BEST)|(best(.+)|Best(.+)|BEST(.+))(?= goes to| Goes To| GOES TO)'
    tweets_of_interest = df.text[df.text.str.contains(win_pattern)].values.tolist()
    for tweet in tweets_of_interest:
        # Figure out if tweet is relevant to award category we are looking at
        max_count = 0
        best_i = -1
        best_award = ""
        for i, award in enumerate(award_names):
            count = 0
            for match in key_award_words[award]:
                if match.lower() in tweet.lower():
                    count += 1
            # Move on to next category if not enough matches were found in the tweet
            if (count < 1):
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

        before_win_expr = '(wins|Wins|WINS|receiv(es|ed)|won)'
        after_win_expr = '(goes to| Goes To| GOES TO)'
        if (aw_type == "person"):
            find_name(tweet, win_candidates[i])
        else:
            find_title(tweet, win_candidates[i], before_win_expr, "before")
            find_title(tweet, win_candidates[i], after_win_expr, "after")

    #print(win_candidates)
    for i in range(len(win_candidates)):
        win_candidates[i] = Counter(win_candidates[i])
        if len(win_candidates[i]) > 0:
            win_candidates[i] = win_candidates[i].most_common(1)[0][0]
        else:
            win_candidates[i] = "not found"
    #print(win_candidates)
    return win_candidates


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

def find_title(tweet, current_dict, split_expr, tag):
    poss_matches = []
    if tag == "before":
        var = re.findall(r"(.+) " + split_expr + " (.+)", tweet)
        if var:
            before = var[0][0].rsplit(None, var[0][0].count(' '))
            for i in range(len(before)):
                candidate = before[-1]
                if i == 0:
                    poss_matches.append(before[-1])
                else:
                    for j in range(i):
                        if "#" in before[-2 - j]:
                            break
                        candidate = before[-2 - j] + " " + candidate
                        poss_matches.append(candidate)
        for match in poss_matches:
            if match in imdb_titles:
                if match in current_dict:
                    current_dict[match] += 1
                else:
                    current_dict[match] = 1
    if tag == "after":
        var = re.findall(r"(.+) " + split_expr + " (.+)", tweet)
        if var and len(var[0]) > 3:
            after = var[0][2].rsplit(None, var[0][0].count(' '))
            for i in range(len(after)):
                candidate = after[0]
                if i == 0:
                    poss_matches.append(after[0])
                else:
                    for j in range(i):
                        candidate =  candidate + " " + after[1 + j]
                    poss_matches.append(candidate)
        for match in poss_matches:
            if match in imdb_titles:
                if match in current_dict:
                    current_dict[match] += 1
                else:
                    current_dict[match] = 1


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

def record_data(hosts, award_names, presenters, nominees, winners, modification, best_dressed, worst_dressed, most_controversial):
    output = "Hosts: "
    for h in hosts:
        output += h + ", "
    output = output[:-2] + "\n\n"
    for i in range(len(award_names)):
        output += "Award: " + award_names[i] + "\n"
        output += "Presenters: "
        for presenter in presenters[i]:
            output += presenter + ", "
        output = output[:-2] + "\nNominees: "
        for nominee in nominees[i]:
            output += nominee + ", "
        output = output[:-2] + "\nWinner: " + winners[i] + "\n\n"
    
    output += "Extras: \n"
    output += "Best Dressed: "
    for i in best_dressed:
        output += i + ", "
    output = output[:-2] + "\n\n"

    output += "Worst Dressed: "
    for i in worst_dressed:
        output += i + ", "
    output = output[:-2] + "\n\n"

    output += "Most Controversial: "
    for i in most_controversial:
        output += i + ", "
    output = output[:-2] + "\n\n"
    
    json_output = {}
    json_output['hosts'] = hosts
    json_output["award_data"] = {}
    for i in range(len(award_names)):
        json_output["award_data"][award_names[i]] = {"nominees": nominees[i], "presenters": presenters[i], "winner": winners[i]}
    with open(json_file_path.replace(".json","") + "our_answers" + modification + ".json", 'w') as data:
        json.dump(json_output, data)

    return output

get_keywords_from_awards(gold_award_names)
print(record_data(get_hosts(), list(gold_award_names), get_presenters_gold(list(gold_award_names)), get_nominees_gold(list(gold_award_names)), get_winners_gold(list(gold_award_names)), "gold", get_best_dressed(), get_worst_dressed(), get_most_controversial()))

our_awards = get_award_names()
get_keywords_from_awards(our_awards)
print(record_data(get_hosts(), our_awards, get_presenters_gold(our_awards), get_nominees_gold(our_awards), get_winners_gold(our_awards), "", get_best_dressed(), get_worst_dressed(), get_most_controversial()))