# Tournament Planner
This tournament planner is a tool for organizing single-day round-robin tournaments with potential group divisions. It optimizes the tournament schedule to ensure fairness, for example by limiting the number of referee assignments for each team. Besides the overall tournament schedule, the planner generates supporting documents such as team-specific schedules and group overviews.

## Fairness aspects considered
### Game play
- Teams have a limit on the number of consecutive games they can play. <sup> 1 </sup>
- Matches for each team are spread across different courts.
- The teams are named first approximately the same number of times to ensure fair distribution of service or kick-off rights.
### Other activities
- Teams have a limit on consecutive pauses between games. <sup> 1 </sup>
- There is a maximum number of games a team can referee. <sup> 1 </sup>
- If there is more than one group, it is possible to decide to have only referees from other groups.

<sup> 1 </sup> this is realized by iteratively reducing the limit until no feasible schedule can be found.

## Output Files
- Overall tournament schedule ([Example here](latex/schedule.pdf))
- Group overview ([Example here](latex/groups.pdf))
- Team schedules
- Match score sheets: one is created for each match with the field, the playing teams and the referee team
- Evaluation sheet


## How to use
The problem is formulated as a mixed-integer programming problem to be solved later by calling a solver from Python through [PuLP](https://github.com/coin-or/pulp).

### Insert parameters in exampe.py
- tournament name
- groups of teams
- number of available courts
- start time of tournament
- match duration
- break time between games


## Further Releases
In the next release, we plan to enhance the tournament planner by introducing options such as external referees instead of referees from other teams.  Following this, we intend to include other tournament phases besides the round-robin system, such as placement games.

## Used Mixed-Integer Programming Problem
Notation | Description
---: | :---
$g \in G$ | group in set of groups
$t \in T_G$ | team in set of teams in group $g$
$b \in B$ | time block in set of time blocks with $B = \{1, 2, \ldots,  \mid B \mid \} $
$f \in F$ | court in set of courts

Parameters | Description
---: | :---
$\overline{C}_{games}$ | maximum number of consecutive games allowed for each team
$\overline{C}_{pauses}$ | maximum number of consecutive pauses allowed for each team


Variable | Description
---: | :---
$x_{b, f, g, t_1, t_2} \in \lbrace 0, 1\rbrace$ | Does team $t_1 \in T_g$ play against team $t_2 \in T_g$ on court $f$ in block $b$?
$z_{b, f, g, t} \in \lbrace 0, 1\rbrace$ | Is team $t \in T_g$ the referee on court $f$ in block $b$?
$SD^{max}$ $\in Z_{\geq 0}$ | Maximum deviation in games played on different sides for any team.
$R^{max}$ $\in Z_{\geq 0}$ | Maximum number of referee games assigned to any team.


#### Implementation of fairness considerations

UB for max_consecutive_games: group size-1
UB for max_consecutive_pauses: nr of time blocks - group size +1
UB for max_court_deviation

### Objective
```math
 \text{Min. } SD^{max}+R^{max}
```

### Constraints
#### Basic tournament structure
Each team $t_1$ plays any other team $t_2$ from the same group $g$.
```math
\sum_{b \in B} \sum_{f \in F} (x_{b,f,g,t_1,t_2} + x_{b,f,g,t_2,t_1}) = 1, \quad \forall g \in G, \forall t_1, t_2 \in T_g, t_1 \neq t_2
```

Valid inequality: Each team $t \in T_g$ plays at maximum $\mid T_g \mid - 1$ games.
```math
\sum_{b \in B} \sum_{f \in F} \sum_{t2 \neq t} (x_{b, f, g, t, t2} + x_{b, f, g, t2, t}) = \mid T_g \mid - 1 \quad \forall g \in G, \forall t \in T_g
```

Each team $t$ plays in any block $b$ at maximum once.
```math
\sum_{f \in F} \sum_{\substack{t_2 \in T_g \\ t \neq t_2}} \left( x_{b,f,g,t,t_2} + x_{b,f,g,t_2,t} \right) \leq 1 \quad \forall b \in B, \forall t \in T_g
```

For each block $b$ and each court $f$ there is at maximum one game planned.
```math
\sum_{g \in G} \sum_{t \in T_g} \sum_{\substack{t' \in T_g \\ t' \neq t}} x_{b,f,g,t,t'} \leq 1 \quad  \forall b \in B, \forall f \in F
```


For every block except the last all courts are in use.
```math
\sum_{f \in F} \sum_{g \in G} \sum_{t \in T_g} \sum_{\substack{t' \in T_g \\ t' \neq t}} x_{b,f,g,t,t'} = |F| \quad \forall b \in \{1, \ldots, \mid B \mid-1\} 
```

#### Refereeing
A team $t$ cannot play and referee in the same block $b$.
```math
\sum_{f \in F} \sum_{\substack{t_2 \in T_g \\ t \neq t_2}} \left( x_{b, f, g, t, t_2} + x_{b, f, g, t_2, t} \right) \leq 1 - \sum_{f \in F} z_{b, f, g, t} \quad  \forall b \in B, \forall t \in T_g
```

There is exactly one referee per court $f$ and block $f$.
```math
\sum_{g \in G} \sum_{t \in T_g} z_{b, f, g, t} = 1  \quad  \forall b \in B, \forall f \in F
```

#### Fairness considerations

For each team $t$ the difference between the number of games played on each side is bounded by $SD^{max}$.

```math
\sum_{b \in B} \sum_{f \in F} \sum_{\substack{t' \in T\\ t' \neq t}} \left( x_{b,f,g,t,t'} - x_{b,f,g,t',t} \right) \leq SD^{max} \quad \forall g \in G, \forall t \in T_g
```

```math
\sum_{b \in B} \sum_{f \in F} \sum_{\substack{t' \in T\\ t' \neq t}} \left( x_{b,f,g,t',t} - x_{b,f,g,t,t'} \right) \leq SD^{max} \quad \forall g \in G, \forall t \in T_g
```

The total referee assignments for each team $t$ across all blocks $B$ and courts $F$ are limited by the decision variable $R^{max}$.
```math
\sum_{b \in B} \sum_{f \in F}  z_{b,f,g,t} \leq R^{max} \quad \forall g \in G, \forall t \in T_g
```

Limit the number of maximum of consecutive games for each team to $\overline{C}_{games}$.
```math
\sum_{b=1}^{\mid B \mid - \overline{C}_{games}} \sum_{f \in F} \sum_{\substack{t_2 \in T_g \\ t_2 \neq t }} (x_{b, f, g, t, t2}+ x_{b, f, g, t2, t}) \leq \overline{C}_{games} \quad \forall g \in G, \forall t \in T_g
```

Limit the number of maximum of consecutive games for each team to $\overline{C}_{pauses}$.

```math
\sum_{1}^{\mid B \mid - \overline{C}_{pauses}} \sum_{f \in F} \sum_{\substack{t' \in T \\ t' \neq t}} \left( x_{b,f,g,t,t'} + x_{b,f,g,t',t} \right) \geq 1 \quad \forall g \in G, \forall t \in T_g
```

TODO: # each team plays at least floor((max(groups)-1)/courts) on each court: todo
                for f in range(self.court_count):
                    prob += lpSum(x[b, f, g, t, t2] + x[b, f, g, t2, t] for b in range(self.block_count) for t2 in range(group.size) if t != t2) >= floor((self.max_group_size-1)/self.court_count) - max_court_deviation

Optional: A team $t \in T_g$ only does refereeing duties for teams of other groups.
```math
\sum_{\substack{t_2,t_3 \in T_g  \\ t_2 \neq t_3}} (x_{b, f, g, t_2, t_3} + x_{b, f, g, t_3, t_2}) \leq 2(1 - z_{b, f, g, t}) \quad  \forall b \in B, \forall f \in F, \forall g \in G, \forall t \in T_g
```
