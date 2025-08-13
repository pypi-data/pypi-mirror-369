from .Maze import Coordinate, Maze

class Markers:
	count: int
	capacity: int
	_currentlyMarkedCoordinates: dict[Maze, set[Coordinate]]
	def __init__(self, count: int) -> None:
		self.count = self.capacity = count
		self._currentlyMarkedCoordinates = {}

	def __contains__(self, MazeAndCoordinate: tuple[Maze, Coordinate]) -> bool:
		maze, coordinate = MazeAndCoordinate
		return coordinate in self._currentlyMarkedCoordinates.get(maze, set())

	def canMark(self, maze: Maze, coordinate: Coordinate, *, verbose: bool=False) -> bool:
		if coordinate not in maze:
			if verbose: print("The room does not exist in the current maze.")
			return False
		if coordinate in self._currentlyMarkedCoordinates.get(maze, set()):
			if verbose: print("The room is already marked.")
			return False
		if self.count <= 0:
			if verbose: print(f"{self.capacity} rooms are already marked, so you can't mark any more.")
			return False
		return True
	
	def canUnmark(self, maze: Maze, coordinate: Coordinate, *, verbose: bool=False) -> bool:
		if coordinate not in maze:
			if verbose: print("The room does not exist in the current maze.")
			return False
		if maze not in self._currentlyMarkedCoordinates:
			if verbose: print("The room is already unmarked.")
			return False
		if coordinate not in self._currentlyMarkedCoordinates[maze]:
			if verbose: print("The room is already unmarked.")
			return False
		if self.count >= self.capacity:
			if verbose: print("No rooms have ever been marked.")
			return False
		return True

	def mark(self, maze: Maze, coordinate: Coordinate, *, verbose: bool=False) -> bool:
		if not self.canMark(maze, coordinate, verbose=verbose): return False
		self._currentlyMarkedCoordinates.setdefault(maze, set()).add(coordinate)
		self.count -= 1
		if verbose: print("The room has been marked.")
		return True
	
	def unmark(self, maze: Maze, coordinate: Coordinate, *, verbose: bool=False) -> bool:
		if not self.canUnmark(maze, coordinate, verbose=verbose): return False
		self._currentlyMarkedCoordinates[maze].remove(coordinate)
		self.count += 1
		if verbose: print("The room has been unmarked.")
		return True