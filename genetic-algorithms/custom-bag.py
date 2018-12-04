import json
import numpy as np
import random as rnd

# my test data
__data_file_path = '/Users/timoon/Projects/spbstu-is/genetic-algorithms/1.txt'


# how to get data, as always
def get_data():
    with open(__data_file_path) as f:
        first_line = f.readline()
        maxWeight = first_line.split(' ')[0]
        maxVolume = first_line.split(' ')[1]

    items = np.loadtxt(__data_file_path, skiprows=1, dtype={
        'names': (
            'weight', 'volume', 'price'
        ),
        'formats': (
            np.int, np.float, np.int
        )
    })

    return {'w': int(maxWeight), 'v': float(maxVolume), 'i': items.tolist()}

# so, get data
bagData = get_data()

items = bagData['i']
exit(0)

# put data and set settings
# ga = pyeasyga.GeneticAlgorithm(bagData['i'])
# ga.population_size = 200


# declare the function, that decides, who will live, who won't :)
def fitness(individual, data):
    weight, volume, price = 0, 0, 0
    for (selected, item) in zip(individual, data):
        if selected:
            weight += item[0]
            volume += item[1]
            price += item[2]

    if weight > bagData['w'] or volume > bagData['v']:
        price = 0

    return price


# set the function
ga.fitness_function = fitness


# 1.1 random generation
def create_individual(data):
    return [rnd.randint(0, 1) for i in range(len(data))]


# 2.1 roulette
def choose_to_crossover(pop_list, data):
    choosens = []
    candidates = []

    # fitness value calculation
    for i in range(len(pop_list)):
        candidates[i] = fitness(pop_list[i], data)

    # find max fitness value
    max_fitness = candidates[0]
    for j in range(len(candidates)):
        max_fitness = candidates[j] if candidates[j] > max_fitness else max_fitness

    # solve if candidate should be choosen to crossover
    for q in range(len(candidates)):
        candidates[q] = candidates[q] / max_fitness
        if rnd.random() < candidates[q]:
            choosens.append(pop_list[q])

    return choosens


# 3.1 (now it done as 3.2)
def crossover(parent_1, parent_2):
    child_1 = list.copy(parent_1)
    child_2 = list.copy(parent_1)

    for i in range(len(parent_1)):
        r1 = rnd.randint(0, 1)
        r2 = rnd.randint(0, 1)
        if r1 > 0:
            child_1[i] = parent_2[i]
        if r2 > 0:
            child_2[i] = parent_2[i]

    return child_1, child_2


# 4.1 invert all for one
def mutation(pop_list):
    # choose one to revert all its bites
    i = rnd.randint(0, len(pop_list) - 1)
    choosen = pop_list[i]

    # revert them
    for j in range(len(choosen)):
        choosen[j] = 0 if choosen[j] == 1 else 1

    pop_list[i] = choosen

    return pop_list

# 5.2 set new population
def update_population(old_pop, new_pop, data):
    merged_pop = []

    # fitness value calculation for old population
    for i in range(len(old_pop)):
        merged_pop[i] = (i, fitness(old_pop[i], data) * .8)

    # fitness value calculation for new population
    for j in range(len(new_pop)):
        merged_pop[len(old_pop) + j] = (len(old_pop) + j, fitness(new_pop[j], data))

    #  arrange by fitness value
    merged_pop = sorted(merged_pop, key=lambda x: x[1])

    better_pop = merged_pop[0:len(old_pop)]
    choosen = []
    for q in range(len(better_pop)):
        choosen[q] = new_pop[better_pop[q][0] - len(old_pop)] if better_pop[q][0] > len(old_pop) else old_pop[better_pop[q][0]]

    return choosen





# simply clever
ga.run()

# as a results here
result = ga.best_individual()

resultWeight = 0
resultVolume = 0
resultPrice = 0
resultSum = []

for i in range(len(result[1])):
    if result[1][i] > 0:
        resultWeight += bagData['i'][i][0]
        resultVolume += bagData['i'][i][1]
        resultPrice += bagData['i'][i][2]
        resultSum.append(i)

res = {
    'weight': resultWeight,
    'volume': resultVolume,
    'price': resultPrice,
    'items': resultSum
}

# look results.json file data
with open('/Users/timoon/Projects/spbstu-is/genetic-algorithms/custom-results.json', 'w') as file:
    json.dump(res, file)
