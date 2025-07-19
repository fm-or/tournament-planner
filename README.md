# Tournament Planner
This tournament planner is a tool for organizing single-day round-robin tournaments with potential group divisions. It optimizes the tournament schedule to ensure fairness, for example by limiting the number of referee assignments for each team. Besides the overall tournament schedule, the planner generates supporting documents such as team-specific schedules and group overviews.

## Fairness aspects considered
### Game play
- Teams have a limit on the number of consecutive games they can play. 
- Matches for each team are spread across different courts. 
- The teams are named first approximately the same number of times to ensure fair distribution of service or kick-off rights.
### Other activities
- Teams have a limit on consecutive pauses between games. 
- There is a maximum number of games a team can referee. 
- If there is more than one group, it is possible to decide to have only referees from other groups.


## How to use
The example file (example.py) consists of a problem instance with two groups consisting each of five teams. There are three courts available and the start of tournament is set to 18:30 (6:30 p.m). Each match lasts 0 hours and 10 minuten and inbetween games is a break of 0 hours and 5 minutes.

Then, the following output files are created:
- Overall tournament schedule ([Example here](latex/schedule.pdf))
- Group overview ([Example here](latex/groups.pdf))
- Team schedules
- Match score sheets: one is created for each match with the field, the playing teams and the referee team
- Evaluation sheet


## Further Releases
In the next release, we plan to enhance the tournament planner by introducing options such as external referees instead of referees from other teams.  Following this, we intend to include other tournament phases besides the round-robin system, such as placement games.

## Used Mixed-Integer Programming Problem
An optimal tournament schedule is generated using a mixed-integer programming approach that ensures fairness through a two-stage process. 

First, the maximum number of consecutive games and breaks, as well as the maximum deviation from an even court deviation per team, are determined. Then, these bounds are used to create a schedule that minimizes the maximum deviation in games played on different sides for each team, as well as the referee assignments per team. If there is more than one group, constraints can ensure that only teams from other groups take over referee duties.

The process repeatedly reduces the number of consecutive games and breaks (to minimize the deviations between the teams) and maximum deviation from an even court deviation until no feasible schedule results.

A problem instance is characterized by the following sets: groups, which then include a set of teams, time blocks for games, and available courts.

Notation | Description
---: | :---
$g \in G$ | group in set of groups
$t \in T_G$ | team in set of teams in group $g$
$b \in B$ | time block in set of time blocks with $B = \{1, 2, \ldots,  \mid B \mid \} $
$f \in F$ | court in set of courts


The following parameters define restrictions for planning beyond organizational bounds e.g.  the maximum number of consecutive games and breaks for each team.
Parameters | Description
---: | :---
$\overline{C}_{games}$ | maximum number of consecutive games allowed for each team
$\overline{C}_{pauses}$ | maximum number of consecutive pauses allowed for each team
$\overline{C}_{court}$ | maximum court deviation allowed for each team


The decision variables represent team assignments to games and refereeing duties on specific courts and time blocks. The integer variables $SD^{max}$ and $R^{max}$ record the maximum deviation in the field-side (or first-serve) allocations and the maximum number of referee games assigned to each team.
Variable | Description
---: | :---
$x_{b, f, g, t_1, t_2} \in \lbrace 0, 1\rbrace$ | Does team $t_1 \in T_g$ play against team $t_2 \in T_g$ on court $f$ in block $b$?
$z_{b, f, g, t} \in \lbrace 0, 1\rbrace$ | Is team $t \in T_g$ the referee on court $f$ in block $b$?
$SD^{max}$ $\in Z_{\geq 0}$ | Maximum deviation in games played on different sides for any team.
$R^{max}$ $\in Z_{\geq 0}$ | Maximum number of referee games assigned to any team.



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

Valid inequality: Each team $t_1 \in T_g$ plays at maximum $\mid T_g \mid - 1$ games.
```math
\sum_{b \in B} \sum_{f \in F} \sum_{\substack{t_2 \in T_g \\ t \neq t_2}} (x_{b, f, g, t_1, t_2} + x_{b, f, g, t_2, t_1}) = \mid T_g \mid - 1 \quad \forall g \in G, \forall t_1 \in T_g
```

Each team $t_1$ plays in any block $b$ at maximum once.
```math
\sum_{f \in F} \sum_{\substack{t_2 \in T_g \\ t \neq t_2}} \left( x_{b,f,g,t_1,t_2} + x_{b,f,g,t_2,t_1} \right) \leq 1 \quad \forall b \in B, \forall g \in G, \forall t_1 \in T_g
```

For each block $b$ and each court $f$ there is at maximum one game planned.
```math
\sum_{g \in G} \sum_{t_1 \in T_g} \sum_{\substack{t_2 \in T_g \\ t_2 \neq t_1}} x_{b,f,g,t_1,t_2} \leq 1 \quad  \forall b \in B, \forall f \in F
```


For every block $b$ except the last all courts are in use.
```math
\sum_{f \in F} \sum_{g \in G} \sum_{t_1 \in T_g} \sum_{\substack{t_2 \in T_g \\ t_2 \neq t_1}} x_{b,f,g,t_1,t_2} = |F| \quad \forall b \in \{1, \ldots, \mid B \mid-1\} 
```

#### Refereeing
A team $t_1$ cannot play and referee in the same block $b$.
```math
\sum_{f \in F} \sum_{\substack{t_2 \in T_g \\ t_1 \neq t_2}} \left( x_{b, f, g, t_1, t_2} + x_{b, f, g, t_2, t_1} \right) \leq 1 - \sum_{f \in F} z_{b, f, g, t_1} \quad  \forall b \in B, \forall g \in G, \forall t_1 \in T_g
```

There is exactly one referee per court $f$ and block $b$.
```math
\sum_{g \in G} \sum_{t \in T_g} z_{b, f, g, t} = 1  \quad  \forall b \in B, \forall f \in F
```

#### Fairness considerations

For each team $t_1$ the difference between the number of games played on each side is bounded by $SD^{max}$.

```math
\sum_{b \in B} \sum_{f \in F} \sum_{\substack{t_2 \in T\\ t_2 \neq t_1}} \left( x_{b,f,g,t_1,t_2} - x_{b,f,g,t_2,t_1} \right) \leq SD^{max} \quad \forall g \in G, \forall t_1 \in T_g
```

```math
\sum_{b \in B} \sum_{f \in F} \sum_{\substack{t_2 \in T\\ t_1 \neq t}} \left( x_{b,f,g,t_2,t_1} - x_{b,f,g,t_1,t_2} \right) \leq SD^{max} \quad \forall g \in G, \forall t_1 \in T_g
```

The total referee assignments for each team $t$ across all blocks $B$ and courts $F$ are limited by the decision variable $R^{max}$.
```math
\sum_{b \in B} \sum_{f \in F}  z_{b,f,g,t} \leq R^{max} \quad \forall g \in G, \forall t \in T_g
```

The upper limit on the maximum of consecutive games for each team $t_1$ to $\overline{C}_{games}$  is adhered to.
```math
\sum_{b=1}^{\mid B \mid - \overline{C}_{games}} \sum_{f \in F} \sum_{\substack{t_2 \in T_g \\ t_2 \neq t }} (x_{b, f, g, t_1, t_2}+ x_{b, f, g, t_2, t_1}) \leq \overline{C}_{games} \quad \forall g \in G, \forall t_1 \in T_g
```

The upper bound for the number of maximum of consecutive games for each team $t_1$ to $\overline{C}_{pauses}$ is respected.

```math
\sum_{1}^{\mid B \mid - \overline{C}_{pauses}} \sum_{f \in F} \sum_{\substack{t_2 \in T_g \\ t_2 \neq t}} \left( x_{b,f,g,t_1,t_2} + x_{b,f,g,t_2,t_1} \right) \geq 1 \quad \forall g \in G, \forall t_1 \in T_g
```

Each team plays at least a minimum number of games on each court. This is calculated as the largest group size minus one, divided evenly across all courts, reduced by an allowed court deviation.

```math
\sum_{b \in B} \sum_{\substack{t_2 \in T_g \\ t_2 \neq t_1}} \left( x_{b,f,g,t_1,t_2} + x_{b,f,g,t_2,t_1} \right) \geq \left\lfloor \frac{\max_{g \in G} ⁡∣T_g∣  - 1}{|F|} \right\rfloor - \overline{C}_{court} \quad \forall f \in F, \forall g \in G, \forall t_1 \in T_g
```

Optional: A team $t_1 \in T_g$ only does refereeing duties for teams of other groups (so not for teams $t_2,t_3 \in T_g$).
```math
\sum_{\substack{t_2,t_3 \in T_g  \\ t_2 \neq t_3}} (x_{b, f, g, t_2, t_3} + x_{b, f, g, t_3, t_2}) \leq 2(1 - z_{b, f, g, t}) \quad  \forall b \in B, \forall f \in F, \forall g \in G, \forall t \in T_g
```
