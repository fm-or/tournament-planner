# Tournament planner
This tournament planner creates an optimized schedule for single-day round-robin tournaments with potential group divisions. The aim is to ensure fairness, for example by limiting the number of refereeing duties for each team. Besides the overall tournament schedule, the planner generates supporting documents such as team-specific schedules and group overviews.

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

## Input parameters
- tournament name
- groups of teams
- number of available courts
- start time of tournament
- match duration
- break time between games

## How to
As the tournament planner used mixed-integer linear models ...

## Further releases

## Further technical details

#### Task list:
- [x] working example including latex
- [ ] review the solving performance
- [ ] more comments
- [ ] documentation
- [ ] readme
