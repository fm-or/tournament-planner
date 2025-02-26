from typing import List, Optional, Tuple
from math import floor

from model.team import Team
from model.group import Group


class TournamentPlan:

    symb = {
        "side1": '\u25E7',
        "side2": '\u25E8',
        "referee": '\u25EB',
        "none": '\u00D7'
    }

    role = [
        "side1", "side2", "referee", "none"
    ]

    def __init__(self, plan: List[List[Tuple[Team, Team, Team]]],
                 groups: List[Group],
                 start_time: Tuple[int, int],
                 match_duration: Tuple[int, int],
                 break_duration: Tuple[int, int]):
        self._plan = plan
        self._groups = groups
        self._start_time = start_time
        self._match_duration = match_duration
        self._break_duration = break_duration
        self._teams = [team for group in groups for team in group.teams]
        self.team_plan = {team: [] for team in self.teams}
        for block in plan:
            for team in self.teams:
                field_side = None, 3
                for field in block:
                    for r, team_r in enumerate(field):
                        if team == team_r:
                            field_side = field, r
                            break
                    if field_side[0] is not None:
                        break
                self.team_plan[team].append(field_side)

    @property
    def blocks(self) -> int:
        return len(self._plan)

    @property
    def fields(self) -> int:
        return len(self._plan[0])
    
    @property
    def groups(self) -> List[Group]:
        return self._groups
    
    @property
    def teams(self) -> List[Team]:
        return self._teams
    
    def get_tournament_schedule(self) -> str:
        return_str = ''
        current_time = self._start_time
        for block in self._plan:
            for f, (team1, team2, referee) in enumerate(block):
                return_str += f"Field {f+1}, {current_time[0]:2n}:{current_time[1]:02n}: {team1.name} vs {team2.name} [{referee.name}]"
                return_str += '\n'
            current_time_minutes = (current_time[0] + self._match_duration[0] + self._break_duration[0]) * 60 + (current_time[1] + self._match_duration[1] + self._break_duration[1])
            current_time = (floor(current_time_minutes / 60), current_time_minutes % 60)
        return return_str
    
    def get_team_schedule(self, team: Team, name_str_length: Optional[str] = None) -> str:
        return_str = ''
        name_str = team.name + ':'
        if name_str_length is None:
            return_str += f"{name_str} "
        else:
            return_str += f"{name_str:<{name_str_length+1}} "
        return_str += ' '.join(self.symb[self.role[r]] for field, r in self.team_plan[team])
        return_str += '\n'
        return return_str
    
    def get_teams_schedule(self) -> str:
        return_str = ''
        name_str_length = max(len(team.name) for team in self.teams)
        for group in self.groups:
            for team in group.teams:
                return_str += self.get_team_schedule(team, name_str_length)
        return return_str
    
    def write_latex_schedule(self, filename: str) -> None:
        with open(filename, 'w', encoding="utf-8") as file:
            current_time = self._start_time
            for b, block in enumerate(self._plan):
                for f, (team1, team2, referee) in enumerate(block):
                    match_nr = b * self.fields + f
                    if match_nr == 0:
                        pos_ref = "\\mediumgap of GNr"
                    elif f == 0:
                        pos_ref = f"\\smallgap of G{match_nr}"
                    else:
                        pos_ref = f"0mm of G{match_nr}"
                    file.write(f"\\createGame{{below={pos_ref}}}{{{match_nr+1}}}{{{team1.name}}}{{{team2.name}}}{{{f+1}}}{{{referee.name}}}{{{current_time[0]:2n}:{current_time[1]:02n}}}{{:}}\n")
                    if f == 2:
                        file.write("\n")
                current_time_minutes = (current_time[0] + self._match_duration[0] + self._break_duration[0]) * 60 + (current_time[1] + self._match_duration[1] + self._break_duration[1])
                current_time = (floor(current_time_minutes / 60), current_time_minutes % 60)
    
    def __str__(self) -> str:
        return self.get_teams_schedule()
