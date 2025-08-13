from random import Random

from ..Utilities.Environment import Environment
from ..Maze import Coordinate, Maze

class PointOfInterest:
	name: str
	maze: Maze
	location: Coordinate
	environment: Environment
	_prng: Random
	_maxPlacementAttempts: int
	def __init__(self, name: str, maze: Maze, location: Coordinate | None = None, *, environment: Environment = Environment.ANY, seed: int | None = None, maxPlacementAttempts: int | None = None, requireEdge: bool=False):
		self.name = name
		self.maze = maze
		self.environment = environment
		self._maxPlacementAttempts = maxPlacementAttempts if maxPlacementAttempts is not None else 3000000
		
		self._prng = Random(seed)
		if location is not None: self.location = location
		else: self.placeRandomly(requireEdge=requireEdge)

	def placeRandomly(self, *, requireEdge: bool = False) -> None:
		for _ in range(self._maxPlacementAttempts):
			self.location = tuple(self._prng.randrange(edgeLength) for edgeLength in self.maze.edgeLengths)
			if requireEdge:
				edgeIndex = self._prng.randint(0, min(self.maze.layout.ndim - 1, 1))
				self.location = self.location[:edgeIndex] + (self._prng.randint(0, 1)*(self.maze.edgeLengths[edgeIndex] - 1),) + self.location[edgeIndex + 1:]
			if self.environment == self.maze.getEnvironment(self.location): break