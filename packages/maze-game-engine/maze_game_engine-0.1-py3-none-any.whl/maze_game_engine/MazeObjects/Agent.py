from typing import Literal, TypeAlias

from ..Utilities.Environment import Environment
from ..Maze import Coordinate, Maze
from ..MazeObjects.PointOfInterest import PointOfInterest

MovementType: TypeAlias = Literal["Static", 'Follower', 'Curious', 'Wanderer', 'Wary', 'User-controlled']

class Agent(PointOfInterest):
	movement: MovementType
	def __init__(self, name: str, maze: Maze, location: Coordinate | None = None, *, movement: MovementType = "Static", environment: Environment = Environment.ANY, seed: int | None = None, maxPlacementAttempts: int | None = None):
		super().__init__(name, maze, location, environment=environment, seed=seed, maxPlacementAttempts=maxPlacementAttempts)
		self.movement = movement

	def move(self) -> None:
		match self.movement:
			case "Static": return
			case _: raise NotImplementedError()