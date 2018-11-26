from SPARQLWrapper import SPARQLWrapper, JSON
from requests import get
import numpy as np
import json

# My film 'id'
movie_id = 'Movie 7'

# I get film name by id from file
__data_file_path = 'movie_names.csv'
movie_names = np.genfromtxt(__data_file_path, delimiter=',', dtype=str, skip_header=0, usecols=(np.arange(1, 1, 1)))
movie_name = movie_names[np.where(movie_names[:,0]==movie_id)][0][1].strip()

# Ask api for Q by provided name
resp = get('https://www.wikidata.org/w/api.php', {
        'action': 'wbgetentities',
        'titles': movie_name,
        'sites': 'enwiki',
        'props': '',
        'format': 'json'
    }).json()

wikiMovieCode = list(resp['entities'])[0]


# Prepare request to wikidata
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setQuery(
"""
SELECT DISTINCT ?human ?humanLabel ?picture 

WHERE {
?human wdt:P31 wd:Q5. 
?human wdt:P106 wd:Q33999. 

?human wdt:P18 ?picture. 

wd:""" + wikiMovieCode + """ wdt:P161 ?human. 

?human wdt:P569 ?date. 
wd:""" + wikiMovieCode + """ wdt:P577 ?dateFilm. 

FILTER (YEAR(?dateFilm) - YEAR(?date) > 40) 

SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } 
}
"""
)

# Send it and get the response in json format
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

# My result data container
res = {}

# Put results into it
for res_id, result in enumerate(results['results']['bindings']):
    res[res_id] = {'name': result['humanLabel']['value'], 'picture':result['picture']['value'] }

# Then create file based on this data
# ?????
# PROFIT!
with open('results.json', 'w') as file:
    json.dump(res, file)
    file.close()
