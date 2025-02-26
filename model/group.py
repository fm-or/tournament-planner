from typing import List

from model.team import Team


class Group:

    def __init__(self, name: str, teams: List[Team]):
        self._name = name
        self._teams = teams
    
    @property
    def name(self) -> str:
        return self._name

    @property
    def teams(self) -> List[Team]:
        return self._teams
    
    @property
    def size(self) -> int:
        return len(self._teams)

    def __str__(self) -> str:
        return f"{self._name} ({len(self._teams)} teams)"
