# Tournament planner
This tournament planner is a tool for organizing single-day round-robin tournaments with potential group divisions. It optimizes the tournament schedule to ensure fairness, for example by limiting the number of referee assignments for each team. Besides the overall tournament schedule, the planner generates supporting documents such as team-specific schedules and group overviews.

## Fairness aspects considered
### Game play
- Teams have a limit on the number of consecutive games they can play. <sup> 1 </sup>
- Matches for each team are spread across different courts.
- The teams are named first approximately the same number of times to ensure fair distribution of service or kick-off rights.
### Other activities
- Teams have a limit on consecutive pauses between games. <sup> 1 </sup>
- There is a maximum number of games a team can referee. <sup> 1 </sup>

<sup> 1 </sup> this is realized by iteratively reducing the limit until no feasible schedule can be found.

## Output files
- Overall tournament schedule
- Group overview
- Team schedules
- Match score sheets: one is created for each match with the field, the playing teams and the referee team
- Evaluation sheet

## How to use
As the tournament planner used mixed-integer linear models ...
The problem is formulated as a mixed-integer programming problem to be solved later by calling a solver from Python through [PuLP](https://github.com/coin-or/pulp).

### Insert parameters in exampe.py
- tournament name
- groups of teams
- number of available courts
- start time of tournament
- match duration
- break time between games


## Further releases
In future releases, we plan to enhance the tournament planner by introducing options for example external referes.

## Further technical details
Notation | Description
---: | :---
$g \in G$ | group in set of groups
$t \in T_G$ | team in set of teams in group $g$
$b \in B$ | time block in set of time blocks
$f \in F$ | court in set of courts


Variable | Description
---: | :---
$x_{b, f, g, t_1, t_2} \in \lbrace 0, 1\rbrace$ | Does team $t_1 \in T_g$ play against team $t_2 \in T_g$ on court $f$ in block $b$?
$z_{b, f, g, t} \in \lbrace 0, 1\rbrace$ | Is team $t \in T_g$ the referee on court $f$ in block $b$?
max\_side\_deviation $\in Z_{\geq 0}$ | Maximum deviation in games played on different sides for any team.
max\_referee\_games $\in Z_{\geq 0}$ | Maximum number of referee games assigned to any team.

### Objective
```math
 Min. \text{max\_side\_deviation}+\text{max\_referee\_games}
```

### Constraints
Each team $t_1$ plays any other team $t_2$ from the same group $g$
```math
\sum_{b \in B} \sum_{f \in F} (x_{b,f,g,t_1,t_2} + x_{b,f,g,t_2,t_1}) = 1, \quad \forall g \in G, \forall t_1, t_2 \in T_g, t_1 \neq t_2
```

UB for max_consecutive_games: group size-1
UB for max_consecutive_pauses: nr of time blocks - group size +1
UB for max_court_deviation
