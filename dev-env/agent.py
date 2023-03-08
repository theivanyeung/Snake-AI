
import numpy as np
import torch
import pickle
import base64
import time
import math
import random

import firebase_admin
from firebase_admin import credentials, firestore

from game import SnakeGame, SnakeSimulation
from engine import GeneticNN, Population

cred = credentials.Certificate("snake-ai-9b1b7-firebase-adminsdk-scuwc-abe60b557f.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# The Agent class will be used to host training and simulation environments

class Agent:
    def __init__(self):

        # board dimensions
        self.board_width = None
        self.board_height = None

        # Population of models
        self.population_size = 1000
        self.generation = 0
        self.current_models = []
        self.breeders = []
        
        self.population = Population(self.population_size, 32, 20, 12, 4)

        # Seconds of pausing between each run
        self.pause = 1
        self.fps = 30
        
    # SIMULATION
    
    def handle_direction(self, game, model):
        direction = game.get_state()
        direction = self.tuple_to_tensor(direction)
        direction = model.forward(direction)
        direction = self.choose_direction(direction)
        game.handle_input(direction)
    
    def run_simulation(self):

        game = SnakeGame()

        model = GeneticNN(32, 24, 12, 4)

        while True:
            # Run the game loop
            board_width, board_height, game_over, has_pressed, score, steps = game.get_values()
            self.board_width = board_width
            self.board_height = board_height
            if not game_over:
                game.clear_direction_inputs()

                if not has_pressed:
                    # Clear the screen
                    game.clear_screen()

                    # Draw the snake, directions, and the apple
                    game.draw_snake()
                    game.draw_distances()
                    game.draw_apple()

                    # Display the score
                    game.display_score()

                    # Update the screen
                    game.update_screen()

                    # Set the game clock
                    game.set_clock()

                    self.handle_direction(game, model)
                else:

                    # Move the snake
                    game.move_snake()
                    game.set_tail_direction()

                    # Check for collisions
                    game.check_collisions()
                    game.check_apple_collision()

                    # Clear the screen
                    game.clear_screen()

                    # Draw the snake, directions, and the apple
                    game.draw_snake()
                    game.draw_distances()
                    game.draw_apple()

                    # Display the score
                    game.display_score()

                    # Update the screen
                    game.update_screen()

                    # Set the game clock
                    game.set_clock()

                    self.handle_direction(game, model)
            else:
                game.reset()

    # TRAINING ENVIRONMENT     

    def fitness_equation(self, steps, score):
        fitness = steps + ((2**score) + (score**2.1) * 500) - ((score**1.2) * ((0.25 * steps)**1.3))
        return max(fitness, .1)
    
    # Converting input data to tensor

    def tuple_to_tensor(self, tuple):
        distances, bool1, bool2, bool3, bool4 = tuple
        bools = bool1 + bool2 + bool3 + bool4
        return torch.tensor(distances + bools, dtype=torch.float32)

    # standardize continuous distance data
    def standardize(self, tensor):
        # Split the tensor into two parts
        first_8 = tensor[:8]
        rest_24 = tensor[8:]

        # Define the max values for each neuron
        max_values = torch.tensor([self.board_height, self.board_height, self.board_width, self.board_width] + [min(self.board_height, self.board_width)] * 4)

        # Normalize the first 8 neurons by dividing by max values
        normalized_8 = first_8 / max_values

        # Combine the normalized 8 neurons with the rest of the 24 neurons using torch.cat
        output = torch.cat((normalized_8, rest_24))

        return output
    
    def choose_direction(self, output):
        max_val, max_idx = torch.max(output, dim=0)
        return {
            0: "up",
            1: "down",
            2: "right",
            3: "left",
        }.get(max_idx.item(), 'Invalid case')
        
    # Firebase approach
        
    def get_models_weights_firebase(self, firstGeneration, generation, population):
        model = GeneticNN(32, 20, 12, 4)
        weight = None
        doc_id = None
        if firstGeneration == True:
            population.set_models()
            models = population.get_models()
            weights = population.get_weights()
            model = models[0]
            weight = weights[0]
        else:
            docs = db.collection(generation + "untrained").limit(1).stream()
            for doc in docs:
                doc_id = doc.id
                parameters = doc.to_dict()['parameters']
                parameters = base64.b64decode(parameters)
                parameters = pickle.loads(parameters)
                weight = parameters
                population.set_weights(model, parameters)
        
        return model, weight, doc_id
    
    def store_model_firebase(self, firstGeneration, parameters, steps, score, fitness, doc_id, generation):
        if firstGeneration == True:
            doc_ref = db.collection(generation).document()
            doc_ref.set({
                "parameters": parameters,
                "steps": steps,
                "score": score,
                "fitness": fitness
            })
        else:
            doc_ref = db.collection(generation).document(doc_id)
            doc_ref.set({
                "parameters": parameters,
                "steps": steps,
                "score": score,
                "fitness": fitness
            })
            db.collection(generation + "untrained").document(doc_id).delete()
            
    # Serverless approach
    
    def get_models_weights(self, population):
        
        if self.generation == 0:
            population.set_models()
            models = population.get_models()
        else:
            models = self.current_models
            
        return models

    def train_models(self):
        
        self.resume_training(0)

        while True:
            
            game = SnakeSimulation()
            population = Population(self.population_size, 32, 20, 12, 4)
        
            models = None
            if self.generation == 0:
                models = self.get_models_weights(population)
            else:
                models = self.current_models
                
            self.current_models = []
            
            index = 0
            
            while index < self.population_size:
                # Run the game loop
                board_width, board_height, game_over, has_pressed, score, steps = game.get_values()
                self.board_width = board_width
                self.board_height = board_height
                if not game_over:
                    game.clear_direction_inputs()
                    
                    game.move_snake()
                    game.set_tail_direction()

                    game.check_collisions()
                    game.check_apple_collision()
                    game.draw_distances()
                    
                    game.set_clock()
            
                    direction = game.get_state()
                    direction = self.tuple_to_tensor(direction)
                    direction = self.standardize(direction)
                    print(direction)
                    direction = models[index].forward(direction)
                    direction = self.choose_direction(direction)
                    game.handle_input(direction)

                else:
                    
                    fitness = self.fitness_equation(steps, score)
                    
                    self.current_models.append({
                        'model': models[index],
                        'fitness': fitness
                    })

                    game.reset()

                    index += 1
            
            # TODO: store in firebase
            
            highest_fitness = max(self.current_models, key=lambda x: x['fitness'])['fitness']
            model_with_highest_fitness = [x for x in self.current_models if x['fitness'] == highest_fitness]
            parameters = pickle.dumps(model_with_highest_fitness[0]['model'].state_dict())
            parameters = base64.b64encode(parameters).decode('utf-8')
            document_name = "GENERATION" + str(self.generation)
            doc_ref = db.collection("fittest").document(document_name)
            doc_ref.set({
                "parameters": parameters,
                "fitness": model_with_highest_fitness[0]['fitness']
            })
                
            # TODO: self.natural_selection()
            
            self.natural_selection()
            
            # TODO: self.repopulate
            
            self.repopulate(population)
            
            print("GENERATION" + str(self.generation))
            self.generation += 1
                
    # Database handling
    
    def check_generation_len(self, collection_path):
        collection_ref = db.collection(collection_path)
        print(len(collection_ref.get()))
        
    # Randomly selects 10% from the population (those with higher fitness value will have a higher chance at being selected)
    # returns: parameters
    def natural_selection_firebase(self, generation):
        # Retrieve all documents in the collection
        docs = db.collection("generation" + str(generation)).stream()
        
        # Calculate the total fitness score of all documents
        total_fitness = sum([doc.to_dict()['fitness'] for doc in docs])
        
        # Calculate the selection probability of each document based on its fitness score
        selection_probabilities = [(doc.id, doc.to_dict()['fitness'] / total_fitness) for doc in db.collection("generation" + str(generation)).stream()]
        
        # Sort the selection probabilities in descending order based on the fitness score
        selection_probabilities = sorted(selection_probabilities, key=lambda x: x[1], reverse=True)
        
        # Calculate the cumulative probability of each document
        cumulative_probabilities = []
        cumulative_prob = 0
        for doc_id, prob in selection_probabilities:
            cumulative_prob += prob
            cumulative_probabilities.append((doc_id, cumulative_prob))
        
        # Select 20 of the documents based on the roulette wheel algorithm
        selected_docs = []
        # while len(selected_docs) < int(len(selection_probabilities) * 0.02):
        while len(selected_docs) < 21:
            rand_num = random.random()
            for doc_id, cum_prob in cumulative_probabilities:
                if rand_num <= cum_prob:
                    parameters = db.collection("generation" + str(generation)).document(doc_id).get().to_dict()['parameters']
                    db.collection("generation" + str(generation) + "breeders").document(doc_id).set(db.collection("generation" + str(generation)).document(doc_id).get().to_dict())
                    parameters = base64.b64decode(parameters)
                    parameters = pickle.loads(parameters)
                    selected_docs.append(parameters)
                    break
                
        return selected_docs

    def repopulate_firebase(self, generation, population):
        
        collection_path = "generation" + str(generation - 1) + "breeders"
        new_collection_path = "generation" + str(generation) + "untrained"
        docs = db.collection(collection_path).stream()
        models = [GeneticNN(32, 20, 12, 4) for _ in range(20)]
        breeders = []
        count = 0
        
        for doc in docs:
            parameters = doc.to_dict()['parameters']
            parameters = base64.b64decode(parameters)
            parameters = pickle.loads(parameters)
            population.set_weights(models[count], parameters)
            breeders.append(models[count])
            count += 1

        generation = population.genetic_algorithm(breeders, 1000)
        
        for model in generation:
            parameters = pickle.dumps(model.state_dict())
            parameters = base64.b64encode(parameters).decode('utf-8')
            doc_ref = db.collection(new_collection_path).document()
            doc_ref.set({
                "parameters": parameters,
            })
            
    # Serverless handling
    
    def natural_selection(self):
        
        total_fitness = sum([model['fitness'] for model in self.current_models])
        
        selection_probabilties = [(model, model['fitness'] / total_fitness) for model in self.current_models]
        
        selection_probabilties = sorted(selection_probabilties, key=lambda x: x[1], reverse = True)
        
        cumulative_probabilities = []
        cumulative_prob = 0
        for model, prob in selection_probabilties:
            cumulative_prob =+ prob
            cumulative_probabilities.append((model, cumulative_prob))
            
        index = 0
        
        while index < 20:
            rand_num = random.random()
            for model, cum_prob in cumulative_probabilities:
                if rand_num <= cum_prob:
                    self.breeders.append(model['model'])
                    index += 1
                    break
    
    def repopulate(self, population):
        
        self.current_models = 0
        self.current_models = population.genetic_algorithm(self.breeders, self.population_size)
        self.breeders = []
        
    def resume_training(self, generation):
        collection_path = "generation" + str(generation)
        if generation != 0:
            self.generation = generation
            docs = db.collection(collection_path).steam()
            for doc in docs:
                model = GeneticNN(32, 20, 12, 4)
                parameters = doc.to_dict()['parameters']
                parameters = base64.b64decode(parameters)
                parameters = pickle.loads(parameters)
                self.population.set_weights(model, parameters)
                self.current_models.append(model)
                
if __name__ == '__main__':
    agent = Agent()
    agent.train_models()