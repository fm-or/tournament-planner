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

## How to Use
As the tournament planner used mixed-integer linear models ...

### Insert parameters in exampe.py
- tournament name
- groups of teams
- number of available courts
- start time of tournament
- match duration
- break time between games


## Further releases

## Further technical details
$ Min. max_side_deviation+max_referee_games $
UB for max_consecutive_games: group size-1
UB for max_consecutive_pauses: nr of time blocks - group size +1
UB for max_court_deviation
