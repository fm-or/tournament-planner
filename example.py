from model.team import Team
from model.group import Group
from model.problem_solver import ProblemSolver

tournament_name = "Hochschulmeisterschaft WS 25/26"
my_team = Team("My Team")
groups = [
    #Group("Group A", [Team("Alle Angaben ohne Gewähr"), Team("Yamos"), Team("Die Jugend von heute"), Team ("Harzer Baller")]),
    #Group("Group B", [Team("Only Best Intentions"), Team("ASV Barbara"), Team("TU Defenders"),  Team("Baggerbande")]),
    #Group("Group C", [Team("Die jungen Wilden und die Alten"), Team ("Ball busters"), Team("Die Jugend von gestern"),  Team ("Potential Team")])

    Group("Group 1", [Team("1-1"), Team("1-2"), Team("1-3"), Team ("1-4")]),
    Group("Group 2", [Team("2-1"), Team("2-2"), Team("2-3"),  Team("2-4")]),
    Group("Group 3", [Team("3-1"), Team ("3-2"), Team("3-3"),  Team ("3-4")])
]
court_count = 3
start_time = (14, 00)
match_duration = (0, 30)
break_duration = (0, 0)

<<<<<<< Updated upstream
solver = ProblemSolver(groups, court_count, start_time, match_duration, break_duration)
=======
solver = ProblemSolver(groups, court_count, start_time, match_duration, break_duration, referee_own_group=True, distribute_team_games_across_fields = False)
>>>>>>> Stashed changes
tournament_plan = solver.solve(prioritized_solver_str="GUROBI", output=True)

print(tournament_plan.get_tournament_schedule())
#print("")
#print(tournament_plan.analyse_schedule())
print("")
print(tournament_plan.get_teams_schedule())
tournament_plan.write_latex_style(tournament_name,court_count)
tournament_plan.write_csv_schedule()
tournament_plan.write_csv_groups()
