from typing import List, Optional, Tuple
from math import floor, ceil
from pulp import LpVariable, LpBinary, LpInteger, LpProblem, LpMinimize, lpSum, LpStatus, PULP_CBC_CMD, listSolvers, getSolver

from model.group import Group
from model.tournament_plan import TournamentPlan


class ProblemSolver:

    def __init__(self,
                 groups: List[Group],
                 court_count: int,
                 start_time: Tuple[int, int],
                 match_duration: Tuple[int, int],
                 break_duration: Tuple[int, int]):
        self._groups = groups
        self._court_count = court_count
        self._start_time = start_time
        self._match_duration = match_duration
        self._break_duration = break_duration
        self._game_count = sum(int(group.size*(group.size-1)/2) for group in groups)
        self._block_count = ceil(self._game_count/court_count)

    @property
    def group_count(self) -> int:
        return len(self._groups)
    
    @property
    def groups(self) -> List[Group]:
        return self._groups
    
    @property
    def max_group_size(self) -> int:
        return max(group.size for group in self._groups)
    
    @property
    def game_count(self) -> int:
        return self._game_count
    
    @property
    def block_count(self) -> int:
        return self._block_count
    
    @property
    def court_count(self) -> int:
        return self._court_count
    
    @property
    def team_count(self) -> int:
        return sum(group.size for group in self._groups)
    
    def _solve(self, max_consecutive_games: int, max_consecutive_pauses: int, max_court_deviation: int, prioritized_solver_str: Optional[str], output: bool) -> Optional[TournamentPlan]:
        # variable definition
        x = dict() # matchups
        z = dict() # referees

        for b in range(self.block_count):
            for f in range(self.court_count):
                for g, group in enumerate(self.groups):
                    for t1 in range(group.size):
                        for t2 in range(group.size):
                            if t1 != t2:
                                # does team t1 play vs team t2 from group g in block b on court f on side 0
                                x[b, f, g, t1, t2] = LpVariable(f"x[{b},{f},{g},{t1},{t2}]", 0, 1, LpBinary)

        for b in range(self.block_count):
            for f in range(self.court_count):
                for g, group in enumerate(self.groups):
                    for t in range(group.size):
                        # is team t the referee in block b on court f?
                        z[b, f, g, t] = LpVariable(f"z[{b},{f},{g},{t}]", 0, 1, LpBinary)   # variable for soft constraint
        max_side_deviation = LpVariable("z1", 0, self.max_group_size-1, LpInteger)
        max_referee_games = LpVariable("z2", ceil(self.game_count/self.team_count), self.block_count-self.max_group_size+1, LpInteger) # todo

        prob = LpProblem("GamePlan", LpMinimize)
        prob += max_side_deviation + max_referee_games

        for g, group in enumerate(self.groups):
            for t in range(group.size):
                # each team t plays any other team t2 from the same group g
                for t2 in range(group.size):
                    if t != t2:
                        # team t plays against t2 exactly once
                        prob += lpSum(x[b, f, g, t, t2] + x[b, f, g, t2, t] for b in range(self.block_count) for f in range(self.court_count)) == 1
                        for b in range(self.block_count):
                            for f in range(self.court_count):
                                # order does matter
                                prob += x[b, f, g, t, t2] + x[b, f, g, t2, t] <= 1
                # optional: each team plays groups[g]-1 games
                prob += lpSum(x[b, f, g, t, t2] + x[b, f, g, t2, t] for b in range(self.block_count) for f in range(self.court_count) for t2 in range(group.size) if t != t2) == group.size - 1
                # each team plays at least floor((max(groups)-1)/courts) on each court: todo
                for f in range(self.court_count):
                    prob += lpSum(x[b, f, g, t, t2] + x[b, f, g, t2, t] for b in range(self.block_count) for t2 in range(group.size) if t != t2) >= floor((self.max_group_size-1)/self.court_count) - max_court_deviation
                # each team plays at most once per block
                for b in range(self.block_count):
                    prob += lpSum(x[b, f, g, t, t2] + x[b, f, g, t2, t] for f in range(self.court_count) for t2 in range(group.size) if t != t2) <= 1
                # each team plays half the time on each side (approximately)
                prob += lpSum(x[b, f, g, t, t2] - x[b, f, g, t2, t] for b in range(self.block_count) for f in range(self.court_count) for t2 in range(group.size) if t != t2) <= max_side_deviation
                prob += lpSum(x[b, f, g, t2, t] - x[b, f, g, t, t2] for b in range(self.block_count) for f in range(self.court_count) for t2 in range(group.size) if t != t2) <= max_side_deviation
                # maximum number of consecutive games
                for b_first in range(self.block_count - max_consecutive_games):
                    prob += lpSum(x[b, f, g, t, t2] + x[b, f, g, t2, t] for b in range(b_first, b_first + max_consecutive_games + 1) for f in range(self.court_count) for t2 in range(group.size) if t != t2) <= max_consecutive_games
                # maximum number of consecutive pauses
                for b_first in range(self.block_count - max_consecutive_pauses):
                    prob += lpSum(x[b, f, g, t, t2] + x[b, f, g, t2, t] for b in range(b_first, b_first + max_consecutive_pauses + 1) for f in range(self.court_count) for t2 in range(group.size) if t != t2) >= 1
                # maximum number of referee games
                prob += lpSum(z[b, f, g, t] for b in range(self.block_count) for f in range(self.court_count)) <= max_referee_games
                # a team can not play and be a referee in the same block
                for b in range(self.block_count):
                    prob += lpSum(x[b, f, g, t, t2] + x[b, f, g, t2, t] for f in range(self.court_count) for t2 in range(group.size) if t != t2) <= 1 - lpSum(z[b, f, g, t] for f in range(self.court_count))

        for b in range(self.block_count):
            if b <= self.block_count-2:
                # every block but the last one is full
                prob += lpSum(x[b, f, g, t, t2] for f in range(self.court_count) for g, group in enumerate(self.groups) for t in range(group.size) for t2 in range(group.size) if t != t2) == self.court_count
                for f in range(self.court_count):
                    # at most one game per court
                    prob += lpSum(x[b, f, g, t, t2] for g, group in enumerate(self.groups) for t in range(group.size) for t2 in range(group.size) if t != t2) <= 1
            for f in range(self.court_count):
                # exactly one team is a referee
                prob += lpSum(z[b, f, g, t] for g, group in enumerate(self.groups) for t in range(group.size)) == 1
                for g, group in enumerate(self.groups):
                    for t in range(group.size):
                        # a team can not play and be a referee in the same game
                        prob += lpSum(x[b, f, g, t, t2] + x[b, f, g, t2, t] for t2 in range(group.size) if t != t2) <= 1 - z[b, f, g, t]
                        # optional: a team can not be a referee in games of their own group
                        if self.group_count >= 2:
                            prob += lpSum(x[b, f, g, t2, t3] + x[b, f, g, t3, t2] for t2 in range(group.size) for t3 in range(group.size) if t2 != t3) <= 2*(1 - z[b, f, g, t])

        # solve
        if output:
            print(f"Solving problem configuration ({max_consecutive_games},{max_consecutive_pauses},{max_court_deviation}).  ", end='\r')
        # check for solvers
        selected_solver = PULP_CBC_CMD(msg=0)
        if prioritized_solver_str is not None and prioritized_solver_str in listSolvers():
            prioritized_solver = getSolver(prioritized_solver_str, msg=0)
            if prioritized_solver.available:
                selected_solver = prioritized_solver
        # solve the model
        status = prob.solve(selected_solver)
        if LpStatus[status] == "Optimal":
            plan = []
            for b in range(self.block_count):
                block = []
                for f in range(self.court_count):
                    side1, side2, referee = None, None, None
                    for g, group in enumerate(self.groups):
                        for t, team in enumerate(group.teams):
                            if sum(x[b, f, g, t, t2].value() for t2 in range(group.size) if t != t2) > 0.99:
                                side1 = team
                            if sum(x[b, f, g, t2, t].value() for t2 in range(group.size) if t != t2) > 0.99:
                                side2 = team
                            if z[b, f, g, t].value() > 0.99:
                                referee = team
                    if side1 is not None:
                        block.append((side1, side2, referee))
                plan.append(block)
            return TournamentPlan(plan, self.groups, self._start_time, self._match_duration, self._break_duration)
        return None

    def solve(self,
              max_consecutive_games_fixed: Optional[int] = None,
              max_consecutive_pauses_fixed: Optional[int] = None,
              max_court_deviation_fixed: Optional[int] = None,
              prioritized_solver_str: Optional[str] = None,
              output: bool = False) -> TournamentPlan:
        max_consecutive_games_intervall = (1, self.max_group_size-1)  # maximum number of consecutive games any team plays {1, ..., teams-1}
        max_consecutive_pauses_intervall = (1, self.block_count-self.max_group_size+1)  # maximum number of consecutive pauses any team has {1, ... blocks-teams+1}
        max_court_deviation_intervall = (0, floor((self.max_group_size-1)/self.court_count)) # maximum deviation from the average court attendance {0, ..., floor((teams-1)/courts)}

        # initialize parameters
        if max_consecutive_games_fixed is None:
            max_consecutive_games = max_consecutive_games_intervall[0]
            max_consecutive_pauses = max_consecutive_pauses_intervall[1] if max_consecutive_pauses_fixed is None else max_consecutive_pauses_fixed
            max_court_deviation = max_court_deviation_intervall[1] if max_court_deviation_fixed is None else max_court_deviation_fixed
        elif max_consecutive_pauses_fixed is None:
            max_consecutive_games = max_consecutive_games_fixed
            max_consecutive_pauses = max_consecutive_pauses_intervall[0]
            max_court_deviation = max_court_deviation_intervall[1] if max_court_deviation_fixed is None else max_court_deviation_fixed
        else:# elif max_court_deviation_fixed is None:
            max_consecutive_games = max_consecutive_games_fixed
            max_consecutive_pauses = max_consecutive_pauses_fixed
            max_court_deviation = max_court_deviation_intervall[0]

        plan = None
        while max_consecutive_games_fixed is None or max_consecutive_pauses_fixed is None or max_court_deviation_fixed is None:
            # solve problem
            plan = self._solve(max_consecutive_games, max_consecutive_pauses, max_court_deviation, prioritized_solver_str, output)

            if plan is None:
                if max_consecutive_games_fixed is None:
                    if max_consecutive_games > max_consecutive_games_intervall[1]:
                        break
                    max_consecutive_games += 1
                elif max_consecutive_pauses_fixed is None:
                    if max_consecutive_pauses > max_consecutive_pauses_intervall[1]:
                        break
                    max_consecutive_pauses += 1
                elif max_court_deviation_fixed is None:
                    if max_court_deviation > max_court_deviation_intervall[1]:
                        break
                    max_court_deviation += 1
            else:
                if max_consecutive_games_fixed is None:
                    max_consecutive_games_fixed = max_consecutive_games
                    max_consecutive_pauses = max_consecutive_pauses_intervall[0] if max_consecutive_pauses_fixed is None else max_consecutive_pauses_fixed
                    max_court_deviation = max_court_deviation_intervall[1] if max_consecutive_pauses_fixed is None else max_court_deviation_intervall[0] 
                elif max_consecutive_pauses_fixed is None:
                    max_consecutive_pauses_fixed = max_consecutive_pauses
                    max_court_deviation = max_court_deviation_intervall[0] if max_court_deviation_fixed is None else max_court_deviation_fixed
                elif max_court_deviation_fixed is None:
                    max_court_deviation_fixed = max_court_deviation
        if plan is None:
            raise ValueError("No solution found")
        if output:
            print("")
        return plan
