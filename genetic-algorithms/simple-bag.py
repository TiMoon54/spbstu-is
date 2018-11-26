from pyeasyga import pyeasyga
import json
import numpy as np

# my test data
__data_file_path = '/Users/timoon/Projects/spbstu-is/genetic-algorithms/1.txt'

# how to get data, as always
def getData():
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
bagData = getData()

# put data and set settings
ga = pyeasyga.GeneticAlgorithm(bagData['i'])
ga.population_size = 200

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
with open('/Users/timoon/Projects/spbstu-is/genetic-algorithms/results.json', 'w') as file:
    json.dump(res, file)
