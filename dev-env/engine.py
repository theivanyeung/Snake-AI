import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import random
import copy

class GeneticNN(torch.nn.Module):
    def __init__(self, input_size, hidden_size1, hidden_size2, output_size):
        super(GeneticNN, self).__init__()
        self.input_size = input_size
        self.hidden_size1 = hidden_size1
        self.hidden_size2 = hidden_size2
        self.output_size = output_size
        self.fc1 = nn.Linear(self.input_size, self.hidden_size1)
        self.fc2 = nn.Linear(self.hidden_size1, self.hidden_size2)
        self.fc3 = nn.Linear(self.hidden_size2, self.output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.sigmoid(self.fc3(x))
        return x
    
class Population:
    def __init__(self, size, input_size, hidden_size1, hidden_size2, output_size):
        self.size = size
        self.input_size = input_size
        self.hidden_size1 = hidden_size1
        self.hidden_size2 = hidden_size2
        self.output_size = output_size
        self.models = None
        self.mutation_rate = 0.05

    def get_models(self):
        return self.models
    
    def set_models(self):
        self.models = [GeneticNN(self.input_size, self.hidden_size1, self.hidden_size2, self.output_size) for _ in range(self.size)]  
    
    def get_weights(self):
        return [model.state_dict() for model in self.models]
    
    def set_weights(self, model, weights):
        model.fc1.weight.data = weights['fc1.weight'].clone().detach()
        model.fc1.bias.data = weights['fc1.bias'].clone().detach()
        model.fc2.weight.data = weights['fc2.weight'].clone().detach()
        model.fc2.bias.data = weights['fc2.bias'].clone().detach()
        model.fc3.weight.data = weights['fc3.weight'].clone().detach()
        model.fc3.bias.data = weights['fc3.bias'].clone().detach()

    # Uniform crossover technique
    def crossover(self, parent1, parent2):
        child = GeneticNN(self.input_size, self.hidden_size1, self.hidden_size2, self.output_size)
        for param1, param2, param_child in zip(parent1.parameters(), parent2.parameters(), child.parameters()):
            mask = torch.rand(param1.size()) > 0.5
            param_child.data.copy_(mask * param1.data + ~mask * param2.data)
        return child
    
    # Random mutation
    def mutate(self, model):
        for param in model.parameters():
            if random.random() < self.mutation_rate:
                param.data += torch.randn(param.size()) * 0.1
        return model
        
    def genetic_algorithm(self, parents, population_size):
        population = []
        for i in range(population_size):
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)
            child = self.crossover(parent1, parent2)
            child = self.mutate(child)
            population.append(child)
        return population