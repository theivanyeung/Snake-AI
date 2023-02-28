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
        self.mutation_rate = 0.1
        self.mean_deviation = 0
        self.standard_deviation = 0.1

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
    
    # Single-point crossover
    def crossover(self, parent1, parent2):
        child1 = GeneticNN(parent1.input_size, parent1.hidden_size1, parent1.hidden_size2, parent1.output_size)
        child2 = GeneticNN(parent2.input_size, parent2.hidden_size1, parent2.hidden_size2, parent2.output_size)
        point = random.randint(0, parent1.fc1.weight.data.size(1))
        child1.fc1.weight.data[:, :point] = parent1.fc1.weight.data[:, :point]
        child1.fc1.weight.data[:, point:] = parent2.fc1.weight.data[:, point:]
        child2.fc1.weight.data[:, :point] = parent2.fc1.weight.data[:, :point]
        child2.fc1.weight.data[:, point:] = parent1.fc1.weight.data[:, point:]

        point = random.randint(0, parent1.fc2.weight.data.size(1))
        child1.fc2.weight.data[:, :point] = parent1.fc2.weight.data[:, :point]
        child1.fc2.weight.data[:, point:] = parent2.fc2.weight.data[:, point:]
        child2.fc2.weight.data[:, :point] = parent2.fc2.weight.data[:, :point]
        child2.fc2.weight.data[:, point:] = parent1.fc2.weight.data[:, point:]

        point = random.randint(0, parent1.fc3.weight.data.size(1))
        child1.fc3.weight.data[:, :point] = parent1.fc3.weight.data[:, :point]
        child1.fc3.weight.data[:, point:] = parent2.fc3.weight.data[:, point:]
        child2.fc3.weight.data[:, :point] = parent2.fc3.weight.data[:, :point]
        child2.fc3.weight.data[:, point:] = parent1.fc3.weight.data[:, point:]

        return child1, child2
    
    # Gaussian mutation
    def mutate(self, model):
        for param in model.parameters():
            if random.uniform(0, 1) < self.mutation_rate:
                param.data.normal_(self.mean_deviation, self.standard_deviation)
                
    def genetic_algorithm(self, parents, population_size):
        children = []
        for i in range(int(population_size / 2)):
            parent1, parent2 = random.sample(parents, 2)
            child1, child2 = self.crossover(parent1, parent2)
            self.mutate(child1)
            self.mutate(child2)
            children.append(child1)
            children.append(child2)
            
        return children