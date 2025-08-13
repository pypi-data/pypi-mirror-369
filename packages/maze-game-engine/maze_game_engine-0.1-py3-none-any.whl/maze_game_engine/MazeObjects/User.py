from ..MazeObjects.Agent import Agent
from ..Utilities.Environment import Environment
from ..Markers import Markers
from ..Maze import Coordinate, Maze

class User(Agent):
	markers: Markers | None
	_shouldIntroduceNextRoom: bool
	def __init__(self, name: str, maze: Maze, location: Coordinate | None = None, markers: int | None = None, *, environment: Environment = Environment.ANY, seed: int | None = None, maxPlacementAttempts: int | None = None):
		super().__init__(name, maze, location, movement="User-controlled", environment=environment, seed=seed, maxPlacementAttempts=maxPlacementAttempts)
		self.markers = Markers(markers) if markers is not None else None
		self._shouldIntroduceNextRoom = True

	def move(self) -> None:
		if self._shouldIntroduceNextRoom: self._introduceRoom()
		userInput = ""
		while userInput.casefold() not in {d.casefold() for d in self.maze.getDirections(self.location) + (["mark", "unmark"] if self.markers is not None else [])}:
			userInput = str(input("> "))

		match userInput.casefold():
			case "mark":
				self._shouldIntroduceNextRoom = self.markers is not None and self.markers.mark(self.maze, self.location, verbose=True)
			case "unmark":
				self._shouldIntroduceNextRoom = self.markers is not None and self.markers.unmark(self.maze, self.location, verbose=True)
			case _:
				previousLocation = self.location
				self.location = tuple(
					(self.location[axis] + (userInput.casefold() == self.maze.ABSOLUTE_DIRECTIONS[axis][0].casefold()) - (userInput.casefold() == self.maze.ABSOLUTE_DIRECTIONS[axis][1].casefold())) % self.maze.edgeLengths[axis] for axis in range(self.maze.layout.ndim)
				)
				self._shouldIntroduceNextRoom = previousLocation != self.location

	def _introduceRoom(self):
		currentDirections = self.maze.getDirections(self.location)
		currentlyMarked = self.markers is not None and (self.maze, self.location) in self.markers
		print("")
		if currentlyMarked: print("The room you are in is marked.")
		# Prints valid directions
		print(f"In this room, you can travel {', '.join(currentDirections[:-1])}", end='', flush=True)
		if len(currentDirections) > 1:
			if len(currentDirections) > 2: print(",", end='', flush=True)
			print(" or ", end='', flush=True)
		print(f"{currentDirections[-1]}. ", end='', flush=True)
		# Prints marked/unmarked status
		if currentlyMarked:
			if self.markers.canUnmark(self.maze, self.location): print("You can also Unmark this room.", end="", flush=True) # type: ignore
		elif self.markers is not None and self.markers.canMark(self.maze, self.location): print("You can also Mark this room.", end="", flush=True)
		print("", flush=True)
