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
    
    def clone(self):
        new_model = GeneticNN(self.input_size, self.hidden_size1, self.hidden_size2, self.output_size)
        new_model.load_state_dict(self.state_dict())
        return new_model
    
    def __len__(self):
        return sum(p.numel() for p in self.parameters())
    
class Population:
    def __init__(self, size, input_size, hidden_size1, hidden_size2, output_size):
        self.size = size
        self.input_size = input_size
        self.hidden_size1 = hidden_size1
        self.hidden_size2 = hidden_size2
        self.output_size = output_size
        self.models = None
        self.mutation_rate = 0.01
        self.mean_deviation = 0
        self.standard_deviation = 0.1
        self.crossover_scalar = 0.5
        self.eta = 15

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
    
    # Simulated binary crossover
    def simulated_binary_crossover(self, parent1, parent2):
        child1, child2 = parent1.clone(), parent2.clone()

        # Generate random numbers
        u = random.random()
        if u <= 0.5:
            beta = (2*u)**(1/(self.eta+1))
        else:
            beta = (1/(2*(1-u)))**(1/(self.eta+1))

        # Calculate children weights
        w1, w2 = child1.state_dict(), child2.state_dict()
        for k in w1.keys():
            w1[k] = beta * w1[k] + (1 - beta) * w2[k]
            w2[k] = beta * w2[k] + (1 - beta) * w1[k]

        # Update children weights
        child1.load_state_dict(w1)
        child2.load_state_dict(w2)

        return child1, child2

    # Single-point binary crossover
    def single_point_binary_crossover(self, parent1, parent2):
        child1, child2 = parent1.clone(), parent2.clone()

        # Generate random crossover point
        crossover_point = random.randint(1, len(parent1)-1)

        # Swap weights from the crossover point
        w1, w2 = child1.state_dict(), child2.state_dict()
        for k in w1.keys():
            if k.startswith('fc'):
                w1[k][:crossover_point] = w2[k][:crossover_point].clone()
                w2[k][:crossover_point] = w1[k][:crossover_point].clone()

        # Update children weights
        child1.load_state_dict(w1)
        child2.load_state_dict(w2)

        return child1, child2
    
    # Gaussian mutation
    def mutate(self, model):
        new_model = model.clone()

        # Apply mutation to weights
        for param in new_model.parameters():
            if random.random() < self.mutation_rate:
                param.data += torch.randn(param.shape) * self.standard_deviation

        return new_model
                
    def genetic_algorithm(self, parents, population_size):
        
        population = []
        
        for _ in range(int(population_size / 2)):
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)
            
            if random.random() > 0.5:
                child1, child2 = self.single_point_binary_crossover(parent1, parent2)
            else:
                child1, child2 = self.simulated_binary_crossover(parent1, parent2)
                
            mutated_child1 = self.mutate(child1)
            mutated_child2 = self.mutate(child2)
            
            population.append(mutated_child1)
            population.append(mutated_child2)

        return population