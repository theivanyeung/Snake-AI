# snake-ai
## A deep neural network capable of winning the game "Snake".
*Snake AI is still in training phase. [`parameters.txt`](ai-test/parameters.txt) represents lastest model.*

#### Using the genetic algorithm, hundreds of DNNs (deep neural networks) were created and initialized each generation with thousands of generations being trained.

#### In this repository, the development/training environment have been included where the models were trained, a testing environment where you can test out different models and how their compare on the gameboard, and also a game environment in which is playable for anyone to try.

---

### How the model and training environment were developed.
  1. Neural network class was initialized with pytorch. Followed a layer pattern (32, 20, 12, 4)
  2. Population class was created to initialized the hundreds of neural networks each generation.
        + Includes crossover function to spawn new and improved neural networks created from crossing the parameters of choosen elite models from the previous generation.
        + Includes mutate function to introduce mutations for exploration. (Mutation rate defaulted at 0.05 for a desired exploration/exploitation ratio)
    
  3. Agent class was created to establish a training environment for the models and generations.
        + Weaves together the game environment, DNN populations, and generations to train with genetic algorithm
        + Includes natural selection class to choose the top 20 models from each generation to be elite models.

---

### How the entire operation was ran.
  1. Created a VM using google cloud computing.
  2. Used tmux to create a virtual console to run the program on the cloud.
  3. Ran agent class which automated the process.
  4. Each generation, the top elite model was chosen to be stored in the firebase for archiving.
  
---
  
### To test the model
  1. Clone the repo
  2. `cd` into the ai-test folder
  3. run `python model.py` or `python3 model.py`
  4. Enter the text from `parameter.txt`
  
---

### Technicalities
![Frame 9](https://user-images.githubusercontent.com/58407773/221779128-80c004b3-2c95-48c9-9fc4-401dadd2cd2a.png)
```
Genetic Algorithm
 - 500 models per generation
 - 20 models are choosen randomly each generation for repopulating 
   (Those with higher fitness scores have higher chances)
 - 50/50 Simulated binary crossover, Single-point binary crossover
  + Variation (SBC): 15
 - Gaussian mutation
  + Mutation rate: 0.1
  + Mean deviation of distribution: 0
  + Standard deviation of distribution: 0.1
  
Training board:
 - Width: 75 blocks
 - Height: 75 blocks
 - Initial length: 4 blocks
 
Testing board:
 - Width: 75 blocks
 - Height: 75 blocks
 - Initial length: 4 blocks
 
DNN Architecture
 - 32 inputs
 - hidden layer 1: 20 neurons
 - hidden layer 2: 12 neurons
 - 4 outputs
 
 Inputs:
  - Directions
   - Up
   - Down
   - Right
   - Left
   - Up-right
   - Up-left
   - Down-right
   - Down-left
   For each direction
    - Distance to wall
    - Is there part of snake
    - Is there an apple
  - Direction of snake
   - Up
   - Down
   - Right
   - Left
  - Direction of snake tail
   - Up
   - Down
   - Right
   - Left
   
 Ouputs:
  + Up
  + Down
  + Right
  + Left
```
**Fitness function**
```python
f(steps, score) = steps + (2**score + score**2.1 * 500) - (score**1.2 * (0.25 * steps)**1.3)
```

---

You can also play the [game](playable-game/game.py) by `cd`'ing into the playable-game folder and running either `python game.py` or `python3 game.py`.   
Edit the game using these self variables:
```python
self.board_width = 11
self.board_height = 11
self.y = 6
self.apple_x = 8
self.snake_head_x = 4
self.fps = 30
```
