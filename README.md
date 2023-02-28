# snake-ai
## A deep neural network capable of winning the game "Snake".

##### Using the genetic algorithm, hundreds of DNNs (deep neural networks) were created and initialized each generation with thousands of generations being trained.

##### In this repository, the development/training environment have been included where the models were trained, a testing environment where you can test out different models and how their compare on the gameboard, and also a game environment in which is playable for anyone to try.

### How the model and training environment were developed.
  1. Neural network class was initialized with pytorch. Followed a layer (32, 20, 12, 4)
  2. Population class was created to initialized the hundreds of neural networks each generation.
        + Includes crossover function to spawn new and improved neural networks created from crossing the parameters of choosen elite models from the previous generation.
        + Includes mutate function to introduce mutations for exploration. (Mutation rate defaulted at 0.05 for a desired exploration/exploitation ratio)
    
  3. Agent class was created to establish a training environment for the models and generations.
        + Weaves together the game environment, DNN populations, and generations to train with genetic algorithm
        + Includes natural selection class to choose the top 20 models from each generation to be elite models.

### How the entire operation was ran.
  1. Created a VM using google cloud computing.
  2. Used tmux to create a virtual console to run the program on the cloud.
  3. Ran agent class which automated the process.
  4. Each generation, the top elite model was chosen to be stored in the firebase for archiving.
  
### To test the model
  1. Clone the repo
  2. `cd` into the ai-test folder
  3. run `python model.py`
  4. Enter the text from `parameter.txt`
