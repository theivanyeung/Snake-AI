import pygame
import random
import time
class Direction:
    def __init__(self, direction, distance, has_apple, has_snake):
        self.direction = direction
        self.distance = distance
        self.has_apple = has_apple
        self.has_snake = has_snake

class SnakeGame:
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
        self.board_width = 75
        self.board_height = 75

        # universial positions
        self.y = 38
        self.apple_x = 65
        self.snake_head_x = 10

        # Set the initial position and direction of the snake
        self.snake_segments = [(self.snake_head_x, self.y), (self.snake_head_x - 1, self.y), (self.snake_head_x - 2, self.y), (self.snake_head_x - 3, self.y)]

        # Set the initial position of the apple
        self.apple_position = (self.apple_x, self.y)

        # Initialize Pygame
        pygame.init()

        # Set the size of the game window
        self.window_size = [self.board_width * self.grid_cell_width, self.board_height * self.grid_cell_height]
        self.screen = pygame.display.set_mode(self.window_size)

        # Set the caption of the game window
        pygame.display.set_caption("Snake")

        # Set the clock to control the game speed
        self.clock = pygame.time.Clock()

        # Set the initial score and game over status
        self.score = 0
        self.game_over = False
        self.has_pressed = False
        self.hunger = 100
        self.steps = 0

        self.fps = 30

        # Set the initial state

        self.direction_inputs = []
        self.snake_direction = "right"
        self.tail_direction = "left"
    
    def clear_direction_inputs(self):
        self.direction_inputs = []
    
    def clear_screen(self):
        self.screen.fill(self.BOARDCOLOR)

    def update_screen(self):
        pygame.display.update()

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

    # Define a function to handle keyboard input
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT and self.snake_direction != "left":
                    self.snake_direction = "right"
                    self.has_pressed = True
                elif event.key == pygame.K_LEFT and self.snake_direction != "right":
                    self.snake_direction = "left"
                    self.has_pressed = True
                elif event.key == pygame.K_UP and self.snake_direction != "down":
                    self.snake_direction = "up"
                    self.has_pressed = True
                elif event.key == pygame.K_DOWN and self.snake_direction != "up":
                    self.snake_direction = "down"
                    self.has_pressed = True

    # Define a function to check for collisions with the walls and the snake's body
    def check_collisions(self):
        # Check for collision with the walls
        head_x = self.snake_segments[0][0]
        head_y = self.snake_segments[0][1]
        if head_x < 0 or head_x >= self.board_width or head_y < 0 or head_y >= self.board_height:
            self.game_over = True

        # Check for collision with the snake's body
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
        self.screen.blit(score_text, [0, 0])

    def get_state(self):
        distances = []
        is_apple = []
        is_snake = []

        for distanceObj in self.direction_inputs:
            distances.append(distanceObj.distance)
            is_apple.append(distanceObj.has_apple)
            is_snake.append(distanceObj.has_snake)

        snake_direction = {
            'up': [True, False, False, False],
            'down': [False, True, False, False],
            'right': [False, False, True, False],
            'left': [False, False, False, True],
        }.get(self.snake_direction, 'Invalid case')

        tail_direction = {
            'up': [True, False, False, False],
            'down': [False, True, False, False],
            'right': [False, False, True, False],
            'left': [False, False, False, True],
        }.get(self.tail_direction, 'Invalid case')

        return distances, is_apple, is_snake, snake_direction, tail_direction

    def reset(self):
        # Set the initial position and direction of the snake
        self.snake_segments = [(self.snake_head_x, self.y), (self.snake_head_x - 1, self.y), (self.snake_head_x - 2, self.y), (self.snake_head_x - 3, self.y)]
        
        self.snake_direction = "right"

        # Set the initial position of the apple
        self.apple_position = (self.apple_x, self.y)

        # Set the initial score and game over status
        self.score = 0
        self.hunger = 100
        self.steps = 0
        self.game_over = False
        self.has_pressed = False

    def quit(self):
        pygame.quit()
        
    def run(self):

        while True:
            # Run the game loop
            if not self.game_over:
                self.clear_direction_inputs()

                if not self.has_pressed:
                    self.handle_input()
                    
                    # Clear the screen
                    self.clear_screen()

                    # Draw the snake, and the apple
                    self.draw_snake()
                    self.draw_apple()

                    # Display the score
                    self.display_score()

                    # Update the screen
                    self.update_screen()

                    # Set the game clock
                    self.set_clock()
                else:
                    self.handle_input()

                    # Move the snake
                    self.move_snake()
                    self.set_tail_direction()

                    # Check for collisions
                    self.check_collisions()
                    self.check_apple_collision()

                    # Clear the screen
                    self.clear_screen()

                    # Draw the snake, and the apple
                    self.draw_snake()
                    self.draw_apple()

                    # Display the score
                    self.display_score()

                    # Update the screen
                    self.update_screen()

                    # Set the game clock
                    self.set_clock()
            else:
                self.reset()
                
if __name__ == '__main__':
    game = SnakeGame()
    game.run()