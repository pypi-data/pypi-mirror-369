from enum import IntEnum

class Environment(IntEnum):
	ANY = 0
	AIR = 1
	LAND = 2
	WATER = 3

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, Environment): return False
		return self.value == Environment.ANY.value or other.value == Environment.ANY.value or self.value == other.value