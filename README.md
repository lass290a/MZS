Description:
	MZS is a multiplayer open world zombie game, written in Python. It is written by to senior highschool students, as a passion project. The aim was to build a multiplayer game from the ground up, using only libraries to help display images and get user input.

Techical details:
	Graphics and player input is from the Arcade library. We originally used the PyGame library for this very purpose, but we quickly realized that it is very poorly optimized, as well as barely using the GPU for rendering. The Arcade module also showed to be particularly more convinient to write in. The game uses pythons standard library modules 'socket' and 'threading' for establishing connections between players.
