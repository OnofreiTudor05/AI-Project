# AI-Project: Kriegspiel Agent
- This project contains an implementation of the Kriegspiel - Blind Chess - game along with an AI Agent that plays against the player
- The AI Agent was implemented using Monte Carlo Tree Search strategy; the code was latter on improved using a matrix of probabilities
- The code was written in Python; Pygame Module was used in order to create the graphical interface
- In order to play the game you have to run the following commands:
	* python main.py hc n - to play the game against the computer without seeeing the adversary pieces - classical Kriegspiel
	* python main.py hc y - to play the game against the computer seeeing the adversary pieces - the agent still plays Kriegspiel
	* python main.py cc n - to watch a simulation of a game from the perspective of an agent that moves random against a specialized AI Agent - Kriegspiel 
	* python main.py cc y - to watch a simulation of a game from the perspective of an agent that moves random against a specialized AI Agent seeing the entire board

- Video Demo: https://youtu.be/nEdsldafrXM