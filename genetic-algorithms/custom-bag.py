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


def get_best_pop_fitness(pop_list, data):
    candidates = []

    # fitness value calculation
    for i in range(len(pop_list)):
        candidates.append(fitness(pop_list[i], data))

    # find max fitness value
    max_fitness = candidates[0]
    for j in range(len(candidates)):
        max_fitness = candidates[j] if candidates[j] > max_fitness else max_fitness

    return max_fitness


def get_best_individual(pop_list, data):
    candidates = []

    # fitness value calculation
    for i in range(len(pop_list)):
        candidates.append((fitness(pop_list[i], data), pop_list[i]))

    # find max fitness value
    max_fitness = candidates[0]
    for j in range(len(candidates)):
        max_fitness = candidates[j] if candidates[j][0] > max_fitness[0] else max_fitness

    return max_fitness


# 1.1 random generation
def create_individual(data):
    return [rnd.randint(0, 1) for i in range(len(data))]


# 2.1 roulette
def choose_to_crossover(pop_list, data):
    choosens = []
    candidates = []

    # fitness value calculation
    for i in range(len(pop_list)):
        candidates.append(fitness(pop_list[i], data))

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


# 3.1 multipoint crossover (with 3 dots)
def crossover(parent_1, parent_2):
    dots = []
    for i in range(0, 3):
        dots.append(rnd.randint(1, len(parent_1)))

    dots.sort()

    child_1 = parent_1[:dots[0]] + parent_2[dots[0]:dots[1]] + parent_1[dots[1]:dots[2]] + parent_2[dots[2]:]
    child_2 = parent_2[:dots[0]] + parent_1[dots[0]:dots[1]] + parent_2[dots[1]:dots[2]] + parent_1[dots[2]:]

    return child_1, child_2


# 4.1 invert all for one
def mutation(pop_list):
    if len(pop_list) == 0:
        return pop_list

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
        merged_pop.append((fitness(old_pop[i], data) * .8, old_pop[i]))

    # fitness value calculation for new population
    for j in range(len(new_pop)):
        merged_pop.append((fitness(new_pop[j], data), new_pop[j]))

    #  arrange by fitness value
    merged_pop = sorted(merged_pop, key=lambda x: x[0], reverse=True)

    better_pop = merged_pop[0:len(old_pop)]
    choosen = []
    for q in range(len(better_pop)):
        choosen.append(better_pop[q][1])

    return choosen


def ga(data):
    # generate first population 1.1
    first_pop = []
    for i in range(200):
        first_pop.append(create_individual(data))

    # find max fitness to compare with next populations
    pop_with_fitness = []

    # fitness value calculation
    for i in range(len(first_pop)):
        pop_with_fitness.append(fitness(first_pop[i], data))

    # find max fitness value
    max_fitness = pop_with_fitness[0]
    for j in range(len(pop_with_fitness)):
        max_fitness = pop_with_fitness[j] if pop_with_fitness[j] > max_fitness else max_fitness

    # current marked fitness
    current_fitness = max_fitness

    # first population also has a mutation
    next_pop = mutation(first_pop)

    # mark if there is no updates for a lot of populations
    stagnation_counter = 0

    # first population life cycle
    for g in range(500):
        # 2.1 (choose to crossover)
        future_parents = choose_to_crossover(next_pop, data)

        # 3.1 (crossover)
        children_pop = []
        for x in range(len(future_parents) - 1):
            children = crossover(future_parents[x], future_parents[x + 1])
            children_pop.append(children[0])
            children_pop.append(children[1])

        # 4.1 (children pop mutation)
        children_pop = mutation(children_pop)

        # 5.1 (next population generation)
        old_pop = next_pop
        next_pop = update_population(next_pop, children_pop, data)

        # 6
        next_fitness = get_best_pop_fitness(next_pop, data)

        # if there is no huge changes in fitness function result for about 10 populations - we quit
        if abs((current_fitness - next_fitness) / ((current_fitness + next_fitness) / 2)) * 100 < .1:
            if stagnation_counter > 10:
                if current_fitness > next_fitness:
                    return get_best_individual(old_pop, data)
                else:
                    return get_best_individual(next_pop, data)
            else:
                stagnation_counter += 1
        else:
            stagnation_counter = 0
            current_fitness = next_fitness

    return get_best_individual(next_pop, data)


# as a results here
result = ga(items)


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
