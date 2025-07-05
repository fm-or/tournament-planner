## Tournament planner
This tournament planner creates an optimized schedule for single-day round-robin tournaments with potential group divisions. The aim is to ensure fairness, for example by limiting the number of refereeing duties for each team. Besides the overall tournament schedule, the planner generates supporting documents such as team-specific schedules and group overviews.

### Fairness aspects considered
- The matches of a team are distributed to the different courts.
- The teams should be named first approximately the same number of times to ensure fair distribution of service or kick-off rights.
- Maximum number of consecutive games*
- Maximum number of consecutive pauses*
- Maximum number of referee games*
* this is realized by iteratively reducing the maximum amount ...

#### Input parameters
- tournament name
- groups of teams
- number of available courts
- start time of tournament
- match duration
- break time between games

#### Task list:
- [x] working example including latex
- [ ] review the solving performance
- [ ] more comments
- [ ] documentation
- [ ] readme
