from typing import List
from typing_extensions import Self


class Team:

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return self.name

    @classmethod
    def create_incrementing_teams(cls, number: int, start_index: int = 1, base_name: str = "Team") -> List[Self]:
        return [cls(f"{base_name} {i}") for i in range(start_index, start_index + number)]
