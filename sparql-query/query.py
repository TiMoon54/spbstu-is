from SPARQLWrapper import SPARQLWrapper, JSON
from requests import get
import numpy as np
import math
import json


__data_file_path = '/Users/timoon/Projects/spbstu-is/simple-recommendation-system/data.csv'
__day_context_file_path = '/Users/timoon/Projects/spbstu-is/simple-recommendation-system/context_day.csv'
__place_context_file_path = '/Users/timoon/Projects/spbstu-is/simple-recommendation-system/context_place.csv'


def getUserMovieMarkData():
    return np.genfromtxt(__data_file_path, delimiter=',', dtype=int, skip_header=1, usecols=(np.arange(1, 31, 1)))

def getUserMovieDayContextData():
    return np.genfromtxt(__day_context_file_path, delimiter=',', dtype=str, skip_header=1, usecols=(np.arange(1, 31, 1)))

def getUserMoviePlaceContextData():
    return np.genfromtxt(__place_context_file_path, delimiter=',', dtype=str, skip_header=1, usecols=(np.arange(1, 31, 1)))

def findCompareapleUsers(target_user_id):
    data = getUserMovieMarkData()

    target_user_marks = data[target_user_id]
    similarity = []

    for user_id, user_marks in enumerate(data):
        if user_id != target_user_id:
            target_user_sqr_sum = 0
            current_user_sqr_sum = 0
            compared_users_sum = 0

            for mark_id, mark in enumerate(user_marks):
                if target_user_marks[mark_id] != -1 and mark != -1:
                    target_user_sqr_sum += target_user_marks[mark_id] * target_user_marks[mark_id]
                    current_user_sqr_sum += mark * mark
                    compared_users_sum += target_user_marks[mark_id] * mark

            similarity_value = compared_users_sum / (math.sqrt(current_user_sqr_sum) * math.sqrt(target_user_sqr_sum))
            similarity.append((user_id, similarity_value))

    dtype = [('user_id', int), ('similarity_value', float)]
    arr_sim = np.array(similarity, dtype=dtype)
    sorted_sim = np.sort(arr_sim, order='similarity_value')
    return sorted_sim[-7:]


def processUserRatings(target_user_id):
    real_target_id = target_user_id - 1
    relevant_users = findCompareapleUsers(real_target_id)
    data = getUserMovieMarkData()

    target_user_avg_mark = my_avg(data[real_target_id])

    relevant_users_avg_mark = []

    for user in relevant_users:
        relevant_users_avg_mark.append(my_avg(data[user[0]]))

    processed_target_user_marks = []

    for movie_id in np.arange(0, 30, 1):
        if data[real_target_id][movie_id] == -1:
            sim_sum = 0
            pure_sim_sum = 0

            for relevant_id, user in enumerate(relevant_users):
                if data[user[0]][movie_id] != -1:
                    sim_sum += user[1] * (data[user[0]][movie_id] - relevant_users_avg_mark[relevant_id])
                    pure_sim_sum += user[1]

            processed_target_user_marks.append((movie_id + 1, target_user_avg_mark + (sim_sum / pure_sim_sum)))

    return np.round(processed_target_user_marks, 3)


def dayContextValue(movie_ids):
    mark_data = getUserMovieMarkData()
    day_context_data = getUserMovieDayContextData()

    movie_day_param = []

    for movie in movie_ids:
        movie_marks = np.array([], dtype=int)
        movie_holiday_marks = np.array([], dtype=int)

        for user_id, user_marks in enumerate(mark_data):
            if user_marks[int(movie[0]) - 1] != -1:
                movie_marks = np.append(movie_marks, user_marks[int(movie[0]) - 1])
                if day_context_data[user_id][int(movie[0]) - 1].lstrip() == 'Sat' or day_context_data[user_id][int(movie[0]) - 1].lstrip() == 'Sun':
                    movie_holiday_marks = np.append(movie_holiday_marks, user_marks[int(movie[0]) - 1])

        movie_day_param.append((int(movie[0]), np.divide(np.average(movie_marks), np.average(movie_holiday_marks))))

    return movie_day_param


def placeContextValue(movie_ids):
    mark_data = getUserMovieMarkData()
    place_context_data = getUserMoviePlaceContextData()

    movie_place_param = []

    for movie in movie_ids:
        movie_marks = np.array([], dtype=int)
        movie_home_marks = np.array([], dtype=int)

        for user_id, user_marks in enumerate(mark_data):
            if user_marks[int(movie[0]) - 1] != -1:
                movie_marks = np.append(movie_marks, user_marks[int(movie[0]) - 1])
                if place_context_data[user_id][int(movie[0]) - 1].lstrip() == 'h' or place_context_data[user_id][int(movie[0]) - 1].lstrip() == 'v':
                    movie_home_marks = np.append(movie_home_marks, user_marks[int(movie[0]) - 1])

        movie_place_param.append((int(movie[0]), np.divide(np.average(movie_marks), np.average(movie_home_marks))))

    return movie_place_param


def my_avg(lst):
    sumer = 0
    cnt = 0
    for val in lst:
        if val != -1:
            sumer += val
            cnt += 1

    return sumer / cnt


def personalRecommendation(target_user):
    unseen_movie_processed_ratings = processUserRatings(target_user)
    movie_place_val = placeContextValue(unseen_movie_processed_ratings)
    movie_holiday_val = dayContextValue(unseen_movie_processed_ratings)

    recommendation_ratings = []
    for rating_id, val in enumerate(unseen_movie_processed_ratings):
        recommendation_ratings.append((int(val[0]), val[1] * movie_place_val[rating_id][1] * movie_holiday_val[rating_id][1]))

    recommendations = np.array(recommendation_ratings, dtype=[('movie_id', int), ('similarity_value', float)])
    sorted = np.sort(recommendations, order='similarity_value')

    return sorted[-1]

def saveAnsvers(target_user):
    user_id = target_user
    recommendation = personalRecommendation(target_user)

    res_obj = {
        'user': target_user,
        '1': {

        }
    }

    for val in processUserRatings(target_user):
        res_obj['1']['movie ' + str(int(val[0]))] = val[1]

    res_obj['2'] = {
        'movie ' + str(recommendation[0]): np.round(recommendation[1], 3)
    }


    with open('/Users/timoon/Projects/spbstu-is/simple-recommendation-system/results.json', 'w') as file:
        json.dump(res_obj, file)
        file.close()

# My film 'id'
movie_id = 'Movie ' + str(personalRecommendation(1)[0])

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
