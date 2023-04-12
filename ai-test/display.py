import pygame
import random
import time

import torch
import torch.nn as nn

class Direction:
    def __init__(self, direction, distance, has_apple, has_snake):
        self.direction = direction
        self.distance = distance
        self.has_apple = has_apple
        self.has_snake = has_snake

class SnakeDisplay:
    def __init__(self):
        # Define some colors
        self.BOARDCOLOR = (21, 21, 21)
        self.SCORECOLOR = (255, 255, 255)
        self.SNAKECOLOR = (223, 238, 255)
        self.APPLECOLOR = (189, 0, 255)

        # Set the width and height of each snake segment
        self.segment_width = 11
        self.segment_height = 11

        # Set the margin between each segment
        self.segment_margin = 1

        # Set the width and height of each grid cell
        self.grid_cell_width = self.segment_width + self.segment_margin
        self.grid_cell_height = self.segment_height + self.segment_margin

        # Set the size of the game board
        self.board_width = 25
        self.board_height = 25

        # universial positions
        possible_positions = [(x, y) for x in range(self.board_width - 1) for y in range(self.board_height - 1)]
        snake_head_pos = random.choice(possible_positions)
        snake_directions = None
        if (snake_head_pos[0] < 2):
            snake_directions = ["up", "down", "left"]
        elif(snake_head_pos[0] > self.board_width - 4):
            snake_directions = ["up", "down", "right"]
        elif(snake_head_pos[1] < 2):
            snake_directions = ["up", "left", "right"]
        elif(snake_head_pos[1] > self.board_height - 4):
            snake_directions = ["down", "left", "right"]
        else:
            snake_directions = ["up", "down", "left", "right"]
        self.snake_direction = random.choice(snake_directions)
        
        # Set the initial position and direction of the snake
        self.snake_segments = None
        if self.snake_direction == "up":
            self.snake_segments = [snake_head_pos, (snake_head_pos[0], snake_head_pos[1] + 1), (snake_head_pos[0], snake_head_pos[1] + 2), (snake_head_pos[0], snake_head_pos[1] + 3)]
        elif self.snake_direction == "down":
            self.snake_segments = [snake_head_pos, (snake_head_pos[0], snake_head_pos[1] - 1), (snake_head_pos[0], snake_head_pos[1] - 2), (snake_head_pos[0], snake_head_pos[1] - 3)]
        elif self.snake_direction == "left":
            self.snake_segments = [snake_head_pos, (snake_head_pos[0] + 1, snake_head_pos[1]), (snake_head_pos[0] + 2, snake_head_pos[1]), (snake_head_pos[0] + 3, snake_head_pos[1])]
        else:
            self.snake_segments = [snake_head_pos, (snake_head_pos[0] - 1, snake_head_pos[1]), (snake_head_pos[0] - 2, snake_head_pos[1]), (snake_head_pos[0] - 3, snake_head_pos[1])]

        # Set the initial position of the apple
        apple_x = random.randint(0, self.board_width - 1)
        apple_y = random.randint(0, self.board_height - 1)
        while (apple_x, apple_y) in self.snake_segments:
            apple_x = random.randint(0, self.board_width - 1)
            apple_y = random.randint(0, self.board_height - 1)
                
        self.apple_position = (apple_x, apple_y)

        # Initialize Pygame
        pygame.init()

        # Set the size of the game window
        self.window_size = [self.board_width * self.grid_cell_width * 5.25, self.board_height * self.grid_cell_height * 3.5]
        self.screen = pygame.display.set_mode(self.window_size)

        # Set the caption of the game window
        pygame.display.set_caption("Snake")

        # Set the clock to control the game speed
        self.clock = pygame.time.Clock()

        # Set the initial score and game over status
        self.score = 0
        self.game_over = False
        self.has_pressed = False
        self.hunger = 300
        self.steps = 0

        self.fps = 300

        # Set the initial state

        self.direction_inputs = []
        self.snake_direction = "right"
        self.tail_direction = "left"

    def get_values(self):
        return self.board_width, self.board_height, self.game_over, self.has_pressed, self.score, self.steps
    
    def get_screen(self):
        return self.screen
    
    def clear_direction_inputs(self):
        self.direction_inputs = []
    
    def clear_screen(self):
        self.screen.fill(self.BOARDCOLOR)

    def update_screen(self):
        pygame.display.flip()

    def set_clock(self):
        self.clock.tick(self.fps)

    # Define a function to draw the snake
    def draw_snake(self):
        for segment in self.snake_segments:
            x = segment[0] * self.grid_cell_width
            y = segment[1] * self.grid_cell_height
            pygame.draw.rect(self.screen, self.SNAKECOLOR, [x, y, self.segment_width, self.segment_height])

    # Define a function to move the snake
    def move_snake(self):
        # Get the position of the head of the snake
        head_x = self.snake_segments[0][0]
        head_y = self.snake_segments[0][1]

        # Move the head of the snake in the current direction
        if self.snake_direction == "right":
            head_x += 1
        elif self.snake_direction == "left":
            head_x -= 1
        elif self.snake_direction == "up":
            head_y -= 1
        elif self.snake_direction == "down":
            head_y += 1

        # Add the new head of the snake to the front of the segments list
        self.snake_segments = [(head_x, head_y)] + self.snake_segments[:-1]

    def set_tail_direction(self):
        # Get the position of the tail of the snake
        tail_x = self.snake_segments[-1][0]
        tail_y = self.snake_segments[-1][1]

        # Get the position of the second last segment of the snake
        second_last_x = self.snake_segments[-2][0]
        second_last_y = self.snake_segments[-2][1]

        # Determine the direction of the tail
        if tail_x > second_last_x:
            self.tail_direction = "right"
        elif tail_x < second_last_x:
            self.tail_direction = "left"
        elif tail_y > second_last_y:
            self.tail_direction = "down"
        elif tail_y < second_last_y:
            self.tail_direction = "up"

    # Define a function to generate a new apple position
    def generate_apple_position(self):
        # Generate a random position for the apple
        apple_x = random.randint(0, self.board_width - 1)
        apple_y = random.randint(0, self.board_height - 1)

        # Make sure the apple is not generated on the snake
        while (apple_x, apple_y) in self.snake_segments:
            apple_x = random.randint(0, self.board_width - 1)
            apple_y = random.randint(0, self.board_height - 1)

        # Set the new apple position
        self.apple_position = (apple_x, apple_y)

    # Define a function to draw the apple
    def draw_apple(self):
        x = self.apple_position[0] * self.grid_cell_width
        y = self.apple_position[1] * self.grid_cell_height
        pygame.draw.rect(self.screen, self.APPLECOLOR, [x, y, self.segment_width, self.segment_height])

    def handle_step(self, direction = None):
        if (self.snake_direction != direction):
            self.hunger -= 1
            self.steps += 1
        self.snake_direction = direction
        self.has_pressed = True

    # Define a function to handle keyboard input
    def handle_input(self, direction):
        if direction == "right" and self.snake_direction != "left":
            self.handle_step("right")
        elif direction == "left" and self.snake_direction != "right":
            self.handle_step("left")
        elif direction == "up" and self.snake_direction != "down":
            self.handle_step("up")
        elif direction == "down" and self.snake_direction != "up":
            self.handle_step("down")

    # Define a function to check for collisions with the walls and the snake"s body
    def check_collisions(self):
        # Check for collision with the walls
        head_x = self.snake_segments[0][0]
        head_y = self.snake_segments[0][1]
        if head_x < 0 or head_x >= self.board_width or head_y < 0 or head_y >= self.board_height:
            self.game_over = True

        # Check for collision with the snake"s body
        for segment in self.snake_segments[1:]:
            if segment == self.snake_segments[0]:
                self.game_over = True

        # Check for hunger
        if self.hunger == 0:
            self.game_over = True

    # Define a function to check for collision with the apple
    def check_apple_collision(self):
        if self.snake_segments[0] == self.apple_position:
            self.score += 1
            self.hunger = 100
            self.generate_apple_position()
            self.snake_segments.append(self.snake_segments[-1])

    # Define a function to display the score
    def display_score(self):
        font = pygame.font.Font(None, 36)
        score_text = font.render("Score: " + str(self.score), True, self.SCORECOLOR)
        self.screen.blit(score_text, [500, 0])

    def draw_distances(self):
        # Define the directions
        directions = ["up", "upright", "right", "downright", "down", "downleft", "left", "upleft"]

        # Get the position of the head of the snake
        head_x = self.snake_segments[0][0]
        head_y = self.snake_segments[0][1]

        # Loop through the directions
        for direction in directions:
            # Set the initial distance
            distance = 0
            has_apple = False
            has_snake = False

            # Loop until the wall, snake, or apple is hit
            while True:
                # Increment the distance
                distance += 1

                # Calculate the new position
                if direction == "up":
                    new_x = head_x
                    new_y = head_y - distance
                elif direction == "upright":
                    new_x = head_x
                    new_y = head_y + distance
                elif direction == "right":
                    new_x = head_x + distance
                    new_y = head_y
                elif direction == "downright":
                    new_x = head_x - distance
                    new_y = head_y
                elif direction == "down":
                    new_x = head_x - distance
                    new_y = head_y - distance
                elif direction == "downleft":
                    new_x = head_x + distance
                    new_y = head_y - distance
                elif direction == "left":
                    new_x = head_x - distance
                    new_y = head_y + distance
                elif direction == "upleft":
                    new_x = head_x + distance
                    new_y = head_y + distance

                # Stop if the new position is out of bounds
                if new_x < 0 or new_x >= self.board_width or new_y < 0 or new_y >= self.board_height:
                    break

                # Stop if the new position is the apple
                if (new_x, new_y) == self.apple_position:
                    has_apple = True
            
                # Stop if the new position is the snake"s body
                if (new_x, new_y) in self.snake_segments:
                    has_snake = True

                # Draw the point
                x = new_x * self.grid_cell_width + (self.segment_width // 2)
                y = new_y * self.grid_cell_height + (self.segment_height // 2)
                pygame.draw.rect(self.screen, (255, 0, 0), [x, y, 1, 1])

            distanceBool = distance == 1

            self.direction_inputs.append(Direction(direction, distanceBool, has_apple, has_snake))
                    

    def get_state(self):
        direction = []

        for distanceObj in self.direction_inputs:
            direction.append(distanceObj.distance)
            direction.append(distanceObj.has_apple)
            direction.append(distanceObj.has_snake)

        snake_direction = {
            "up": [True, False, False, False],
            "right": [False, True, False, False],
            "down": [False, False, True, False],
            "left": [False, False, False, True],
        }.get(self.snake_direction, "Invalid case")

        tail_direction = {
            "up": [True, False, False, False],
            "right": [False, True, False, False],
            "down": [False, False, True, False],
            "left": [False, False, False, True],
        }.get(self.tail_direction, "Invalid case")

        return direction, snake_direction, tail_direction
    
    def draw_neural_network_visualization(self, net, x_offset, y_offset, layer_colors, input_activations, activations=[], neuron_radius=10, layer_spacing=175, neuron_spacing=45):
        def draw_neuron(x, y, color, activation):
            activation = max(0, min(1, activation))
            neuron_color = (
                int(color[0] * activation) + (21 if activation == 0 else 0),
                int(color[1] * activation) + (21 if activation == 0 else 0),
                int(color[2] * activation) + (21 if activation == 0 else 0),
            )
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), neuron_radius + 1)
            pygame.draw.circle(self.screen, neuron_color, (x, y), neuron_radius)

        def draw_weight_line(x1, y1, x2, y2, weight):
            normalized_weight = abs(weight) / 2
            color_intensity = int(normalized_weight * 255)
            color_intensity = max(0, min(255, color_intensity))
            color = (color_intensity, color_intensity, color_intensity)

            pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), 2)

        y = y_offset
        layers = [net.fc1, net.fc2, net.fc3]
        input_layer = nn.Linear(32, layers[0].in_features)
        layers.insert(0, input_layer)

        # Draw the weight lines first
        for idx, layer in enumerate(layers):
            weights = layer.weight.data if idx > 0 else None
            biases = layer.bias.data if idx > 0 else None

            num_neurons = layer.out_features if idx > 0 else layer.in_features
            total_width = (num_neurons - 1) * neuron_spacing
            layer_center_offset = total_width / 2

            x_positions = [(x_offset + i * neuron_spacing - layer_center_offset) for i in range(num_neurons)]

            if idx > 0:
                prev_x_positions = [(x_offset + i * neuron_spacing - (layers[idx - 1].out_features - 1) * neuron_spacing / 2) for i in range(layers[idx - 1].out_features)]

                for i, current_x in enumerate(x_positions):
                    for j, prev_x in enumerate(prev_x_positions):
                        weight = weights[j % len(weights)][i]
                        draw_weight_line(prev_x, y - layer_spacing, current_x, y, weight)
            elif idx == 0:
                next_x_positions = [(x_offset + i * neuron_spacing - (layers[idx + 1].out_features - 1) * neuron_spacing / 2) for i in range(layers[idx + 1].out_features)]

                # Create a dummy weight matrix for the connections between the input layer and the first hidden layer
                num_input_neurons = len(x_positions)
                num_next_neurons = len(next_x_positions)
                dummy_weights = torch.ones(num_next_neurons, num_input_neurons)

                for i, row in enumerate(dummy_weights):
                    for j, weight in enumerate(row):
                        draw_weight_line(x_positions[j], y, next_x_positions[i], y + layer_spacing, weight)

            y += layer_spacing

        # Draw the neurons on top of the weight lines
        y = y_offset
        for idx, layer in enumerate(layers):
            num_neurons = layer.out_features if idx > 0 else layer.in_features
            total_width = (num_neurons - 1) * neuron_spacing
            layer_center_offset = total_width / 2
            x_positions = [(x_offset + i * neuron_spacing - layer_center_offset) for i in range(num_neurons)]
            for i in range(num_neurons):
                layer_color = layer_colors[idx]
                if idx == 0:
                    activation = input_activations[i]
                else:
                    activation = activations[idx - 1][i] if idx - 1 < len(activations) and i < len(activations[idx - 1]) else 0.0

                draw_neuron(x_positions[i], y, layer_color, activation)

            y += layer_spacing
            
    def display_generation(self, generation):
        font = pygame.font.Font(None, 36)
        generation_text = font.render("Generation: " + str(generation), True, (255, 255, 255))
        self.screen.blit(generation_text, [750, 0])
        
    def display_fitness(self, fitness):
        font = pygame.font.Font(None, 36)
        fitness_text = font.render("Fitness: " + str(fitness), True, (255, 255, 255))
        self.screen.blit(fitness_text, [1000, 0])

    def reset(self):
        # universial positions
        possible_positions = [(x, y) for x in range(self.board_width - 1) for y in range(self.board_height - 1)]
        snake_head_pos = random.choice(possible_positions)
        snake_directions = None
        if (snake_head_pos[0] < 2):
            snake_directions = ["up", "down", "left"]
        elif(snake_head_pos[0] > self.board_width - 4):
            snake_directions = ["up", "down", "right"]
        elif(snake_head_pos[1] < 2):
            snake_directions = ["up", "left", "right"]
        elif(snake_head_pos[1] > self.board_height - 4):
            snake_directions = ["down", "left", "right"]
        else:
            snake_directions = ["up", "down", "left", "right"]
        self.snake_direction = random.choice(snake_directions)

        # Set the initial position and direction of the snake
        self.snake_segments = None
        if self.snake_direction == "up":
            self.snake_segments = [snake_head_pos, (snake_head_pos[0], snake_head_pos[1] + 1), (snake_head_pos[0], snake_head_pos[1] + 2), (snake_head_pos[0], snake_head_pos[1] + 3)]
        elif self.snake_direction == "down":
            self.snake_segments = [snake_head_pos, (snake_head_pos[0], snake_head_pos[1] - 1), (snake_head_pos[0], snake_head_pos[1] - 2), (snake_head_pos[0], snake_head_pos[1] - 3)]
        elif self.snake_direction == "left":
            self.snake_segments = [snake_head_pos, (snake_head_pos[0] + 1, snake_head_pos[1]), (snake_head_pos[0] + 2, snake_head_pos[1]), (snake_head_pos[0] + 3, snake_head_pos[1])]
        else:
            self.snake_segments = [snake_head_pos, (snake_head_pos[0] - 1, snake_head_pos[1]), (snake_head_pos[0] - 2, snake_head_pos[1]), (snake_head_pos[0] - 3, snake_head_pos[1])]

        # Set the initial position of the apple
        apple_x = random.randint(0, self.board_width - 1)
        apple_y = random.randint(0, self.board_height - 1)
        while (apple_x, apple_y) in self.snake_segments:
            apple_x = random.randint(0, self.board_width - 1)
            apple_y = random.randint(0, self.board_height - 1)
                
        self.apple_position = (apple_x, apple_y)

        # Set the initial score and game over status
        self.score = 0
        self.hunger = 100
        self.steps = 0
        self.game_over = False
        self.has_pressed = False

    def quit(self):
        pygame.quit()