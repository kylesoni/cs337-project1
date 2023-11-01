import pandas as pd
import re
from ftfy import fix_text
from unidecode import unidecode
import json
import imdb
from nltk import edit_distance

file = open('data\\gg2013answers.json')
df = json.load(file)
awards = df['award_data'].keys()
nominees = []
for val in df['award_data'].values():
    nominees.append(val['winner'])
#print(nominees)

ia = imdb.Cinemagoer()

name = 'game Change'
person = ia.search_person(name)
#print(name)
#print(person[0]['name'])
#print(edit_distance(name, person[0]['name']))

candidate_loc = ["hi", "my", "name", "is"]
poss_wins = []

for i in range(len(candidate_loc)):
    candidate = candidate_loc[0]
    if i == 0:
        poss_wins.append(candidate_loc[0])
    else:
        for j in range(i):
            candidate =  candidate + " " + candidate_loc[1 + j]
        poss_wins.append(candidate)

print(poss_wins)