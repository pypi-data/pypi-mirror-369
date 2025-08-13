from numpy import uint8, uint16, uint32, uint64, zeros
from numpy.typing import NDArray
from random import Random
from typing import Literal, TypeAlias

from .Utilities.Environment import Environment

Coordinate: TypeAlias = tuple[int, ...]

class Maze:
	layout: NDArray[uint8 | uint16 | uint32 | uint64]
	edgeLengths: tuple[int, ...]
	_prng: Random

	ABSOLUTE_DIRECTIONS = (
		('North', 'South'),
		('East', 'West'),
		('Up', 'Down'),
		('Forwards in Time', 'Backwards in Time'),
		('North Across the Multiverse', 'South Across the Multiverse'),
		('East Across the Multiverse', 'West Across the Multiverse'),
		('Up Across the Multiverse', 'Down Across the Multiverse'),
		('Forwards in Time Across the Multiverse', 'Backwards in Time Across the Multiverse')
	)
	RELATIVE_DIRECTIONS = (
		('Forward', 'Backward'),
		('Right', 'Left'),
		('Upward', 'Downward'),
		('Forwards in Time', 'Backwards in Time'),
		('Forward Across the Multiverse', 'Forward Across the Multiverse'),
		('Left Across the Multiverse', 'Right Across the Multiverse'),
		('Upward Across the Multiverse', 'Downward Across the Multiverse'),
		('Forwards in Time Across the Multiverse', 'Backwards in Time Across the Multiverse')
	)

	def __init__(self, dimension: Literal[1, 2, 3, 4, 5, 6, 7, 8], edgeLengthsRange: int | tuple[int, int], *, seed: int | None = None) -> None:
		if dimension > len(self.ABSOLUTE_DIRECTIONS): raise ValueError(f"Dimension is larger than largest-supported dimension ({len(self.ABSOLUTE_DIRECTIONS)}).")

		self._prng = Random(seed)
		minEdgeLength, maxEdgeLength = (edgeLengthsRange, edgeLengthsRange) if isinstance(edgeLengthsRange, int) else edgeLengthsRange
		self.edgeLengths = tuple(self._prng.randint(minEdgeLength, maxEdgeLength) for _ in range(dimension))

		self.layout = zeros(self.edgeLengths, dtype=self._getSmallestDtypeNeeded(dimension))
		mazeFrontier = [tuple([self._prng.randrange(edgeLength) for edgeLength in self.layout.shape])]
		while mazeFrontier:
			coordinate = mazeFrontier.pop(self._prng.randrange(len(mazeFrontier)))
			for axis in range(dimension):
				mazeFrontier += self._tryToConnectCells(coordinate, axis, -1) + self._tryToConnectCells(coordinate, axis, 1)

	def __contains__(self, coordinate: Coordinate) -> bool:
		return len(coordinate) == self.layout.ndim and all(0 <= axis1 <= axis2 for axis1, axis2 in zip(coordinate, self.layout.shape, strict=True))
	
	# Validates and connects two cells, thus expanding the maze.
	def _tryToConnectCells(self, cellCoords: tuple[int, ...], changedCoordinateIndex: int, change: Literal[-1, 1]) -> list[Coordinate]: # Should probably change to addAdjacentCell(cellCoords, newCellCoords) at some point
		if self.layout.shape[changedCoordinateIndex] <= 1: return []
		if changedCoordinateIndex < 0 or changedCoordinateIndex >= len(cellCoords): return []
		newCellCoords = cellCoords[:changedCoordinateIndex] + (
			(cellCoords[changedCoordinateIndex] + change) % self.layout.shape[changedCoordinateIndex],
		) + cellCoords[changedCoordinateIndex + 1:]
		if self.layout[newCellCoords]: return []
		
		self.layout[cellCoords] |= 1 << (2*changedCoordinateIndex + (change == -1))
		self.layout[newCellCoords] |= 1 << (2*changedCoordinateIndex + (change == 1))
		return [newCellCoords]
	
	def getDirections(self, coordinate: Coordinate, facing: str | None = None) -> list[str]:
		if coordinate not in self: return []

		directions: tuple[tuple[str, str], ...] = tuple()
		match facing:
			case None:
				directions = self.ABSOLUTE_DIRECTIONS
			case _: raise NotImplementedError("Relative directions have not been implemented yet.")
		
		return sorted(direction for i, directionPair in enumerate(directions[:self.layout.ndim]) for j, direction in enumerate(directionPair) if self.layout[coordinate] & (1 << (2*i + j)))
	
	def getEnvironment(self, coordinate: Coordinate) -> Environment:
		"""Environments are not implemented yet."""
		return Environment.ANY
	
	@staticmethod
	def _getSmallestDtypeNeeded(dimension: int) -> uint8 | uint16 | uint32 | uint64:
		ENVIRONMENT_BITS = 2
		DIRECTION_BITS = 2*dimension
		TOTAL_BITS = ENVIRONMENT_BITS + DIRECTION_BITS
		if TOTAL_BITS <= 8: return uint8 # type: ignore
		elif TOTAL_BITS <= 16: return uint16 # type: ignore
		elif TOTAL_BITS <= 32: return uint32 # type: ignore
		elif TOTAL_BITS <= 64: return uint64 # type: ignore
		raise RuntimeError("More bits required than provided by NumPy.")