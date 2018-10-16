import numpy as np
import math

__data_file_path = '/Users/timoon/Projects/spbstu-is/simple-recommendation-system/data.csv'


def getUserMovieMarkData():
    return np.genfromtxt(__data_file_path, delimiter=',', dtype=int, skip_header=1, usecols=(np.arange(1, 31, 1)))


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

    print(np.round(processed_target_user_marks, 3))


def my_avg(lst):
    sumer = 0
    cnt = 0
    for val in lst:
        if val != -1:
            sumer += val
            cnt += 1

    return sumer / cnt


processUserRatings(1)
