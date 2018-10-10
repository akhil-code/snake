from neural import NeuralNetwork
from numpy import random, copy
from objects import Snake

class Individual:
    def __init__(self, layers=None, weights=None):
        self.snake = Snake()
        self.nn = NeuralNetwork(layers=layers) if weights == None else NeuralNetwork(layers=layers, weights=weights)
    
    def find_fitness(self):
        return self.snake.score


class Population:
    def __init__(self, pop_size=10, mutate_prob=0.03, retain_unfit_prob=0.01, select=0.25, layers=None):
        self.pop_size = pop_size
        self.mutate_prob = mutate_prob
        self.retain_unfit_prob = retain_unfit_prob
        self.select = select
        self.layers = layers

        self.generation = 1
        self.individuals = [Individual(layers=layers) for i in range(self.pop_size)]
    
    def grade(self):
        self.pop_fitness = max([i.find_fitness() for i in self.individuals])
    
    def select_parents(self):
        self.individuals = sorted(self.individuals, key=lambda i: i.find_fitness(), reverse=True)
        # selecting fittest parents
        parents_selected = self.select * self.pop_size
        self.parents = self.individuals[:parents_selected]
        # including some unfittest parents
        unfittest = self.individuals[parents_selected:]
        for i in unfittest:
            if self.retain_unfit_prob > random.rand():
                self.parents.append(i)
        
    def crossover(self, w1, w2):
        number_of_layers = len(w1) + 1
        weights = []
        for l in range(number_of_layers - 1):
            w = copy(w1[l])
            r,c = w.shape
            for i in range(r):
                for j in range(c):
                    if random.rand() < 0.5:
                        w[i][j] = w2[l][i][j]
            weights.append(w)

        return weights

    def breed(self):
        children_size = self.pop_size - len(self.parents)
        children = []
        while len(children) < children_size:
            father = random.choice(self.parents)
            mother = random.choice(self.parents)
            while father != mother:
                child_weights = self.crossover(father.nn.weights, mother.nn.weights)
                child = Individual(layers=self.layers, weights=child_weights)
                children.append(child)
        
        self.individuals = self.parents + children

    def evolve(self):
        self.grade()
        self.select_parents()
        self.breed()

        self.generation += 1