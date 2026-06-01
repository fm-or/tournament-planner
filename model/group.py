from typing import List
from typing import Optional

from model.team import Team


class Group:

    def __init__(self, name: str, teams: List[Team], courts: Optional[List[int]] = None):
        self._name = name
        self._teams = teams
        self._courts = courts or []

    @property
    def courts(self) -> List[int]:
        return self._courts
    
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
