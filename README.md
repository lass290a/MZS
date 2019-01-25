Description:
	MZS is a multiplayer PvP open world zombie game, written in Python. It is written by two senior highschool students as a passion project, and the aim is to build a multiplayer game from the ground up, only using libraries to help display images and get player input.

Technical details:
	MZS uses the Arcade python library for rendering graphics, as well getting player inputs. We originally used the PyGame library for this very purpose, but we quickly realized that it is very poorly optimized and barely uses the GPU for rendering. The game uses pythons standard library modules 'socket' and 'threading' to establish connections between players.
