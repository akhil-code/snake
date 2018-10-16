from numpy import random, dot, exp

class NeuralNetwork:
    def __init__(self, layers=None, weights=None):
        if weights is None:
            self.weights = []
            self.number_of_layers = len(layers)
            for i in range(len(layers) - 1):
                w = random.rand(layers[i], layers[i+1])
                self.weights.append(w)
        else:
            self.weights = weights
    
    def sigmoid(self, X):
        return 1 / (1 + exp(-X))
    
    def feed_forward(self, X):
        l = X
        for i in range(self.number_of_layers - 1):
            w = self.weights[i]
            l = self.sigmoid(dot(w.T, l))
            print(l)
        self.y = l
        return self.y
