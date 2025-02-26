from model.team import Team
from model.group import Group
from model.problem_solver import ProblemSolver

my_team = Team("My Team")
groups = [
    Group("Group A", [my_team] + Team.create_incrementing_teams(4, start_index=1)),
    Group("Group B", Team.create_incrementing_teams(5, start_index=5))
]
court_count = 3
start_time = (18, 30)
match_duration = (0, 10)
break_duration = (0, 5)

solver = ProblemSolver(groups, court_count, start_time, match_duration, break_duration)
tournament_plan = solver.solve(prioritized_solver_str="GUROBI", output=True)

print(tournament_plan.get_tournament_schedule())
print("")
print(tournament_plan.get_teams_schedule())
tournament_plan.write_latex_schedule("latex/schedule.tex")
