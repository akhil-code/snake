from neural import NeuralNetwork
from numpy import random, copy, array, ceil, array, sum, ravel
from snake import Snake

class Individual:
    def __init__(self, layers=None, weights=None):
        self.snake = Snake()
        if weights is None:
            self.nn = NeuralNetwork(layers=layers)
        else:
            self.nn = NeuralNetwork(layers=layers, weights=weights)
    
    def find_fitness(self):
        return self.snake.score

class Population:
    def __init__(self, pop_size=20, mutate_prob=0.03, retain_unfit_prob=0.01, select=0.333, layers=None):
        self.pop_size = pop_size
        self.mutate_prob = mutate_prob
        self.retain_unfit_prob = retain_unfit_prob
        self.select = select
        self.layers = layers
        self.fitness_history = []

        self.generation = 1
        self.individuals = [Individual(layers=layers) for i in range(self.pop_size)]
    
    def grade(self):
        self.pop_fitness = max([i.find_fitness() for i in self.individuals])
        self.fitness_history.append(self.pop_fitness)
    
    def select_parents(self):
        self.individuals = sorted(self.individuals, key=lambda i: i.find_fitness(), reverse=True)
        # selecting fittest parents
        parents_selected = int(self.select * self.pop_size)
        self.parents = self.individuals[:parents_selected]
        # including some unfittest parents
        unfittest = self.individuals[parents_selected:]
        for i in unfittest:
            if self.retain_unfit_prob > random.rand():
                self.parents.append(i)
        
        # reset properties of parents
        for individual in self.parents:
            individual.snake.reset()

    
    def crossover(self, weights1, weights2):
        """ combines the genes of two parent to form genes of child """
        weights = []

        for w1, w2 in zip(weights1, weights2):
            w = []
            for column1, column2 in zip(w1, w2):
                column = []
                for theta1, theta2 in zip(column1, column2):
                    # selecting randomly from father or mother genes
                    choosen = random.choice((theta1, theta2))       
                    column.append(choosen)
                w.append(column)
            weights.append(array(w))
        return weights

    def breed(self):
        children_size = self.pop_size - len(self.parents)
        children = []
        if len(self.parents) > 0:
            while len(children) < children_size:
                father = random.choice(self.parents)
                mother = random.choice(self.parents)
                if father != mother:
                    child_weights = self.crossover(father.nn.weights, mother.nn.weights)
                    child = Individual(layers=self.layers, weights=child_weights)
                    children.append(child)
            
            self.individuals = self.parents + children

    def evolve(self):
        self.grade()
        self.select_parents()
        self.breed()

        if self.generation % 10 == 0:
            print(f'{self.generation}  --> {self.fitness_history[-1]/1000}') 
        self.generation += 1