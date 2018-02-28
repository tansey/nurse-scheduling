# Nurse scheduling
This is a simple proof-of-concept project to help mental health nurses schedule their day.

## Given:

    Time is divided into blocks of 30 minutes.

    List of staff, each with different available blocks of time

    Each employee has a designation as RMN (Registered Mental health Nurse) or HCA (Health Care Assistant).

    Each employee has a designation as Male or Female (necessary for some male-only patients)

    List of 1:1 patients that must have 1 staffer assigned at all times; optional male staffers only flag for each patient.

    List of 2:1 patients that must have 2 staffers assigned at all times; optional male staffers only flag for each patient.

    List of medication times that must each have 1 RMN assigned.

## Constraints:
Some constraints are absolutely required (hard) and others are merely preferences (soft). For each soft constraint, we place a certain weight on satisfying them. All weights can be adjusted.

    Hard: one RMN assigned to each medication block

    Hard: one person assigned to general observations at all times.

    Hard: 1:1 and 2:1 patients with Male-only flags must have Male staffers assigned.

    Hard: Each staffer can take one break and breaks occur only in a pre-defined [min,max] window of blocks (to prevent people being assigned a break too early or late in the day)

    Soft: Any employee working two shifts must receive a 1-hour break before the last 2 blocks of their second shift.
        - RMN breaks: weight=0.1 (not very important)
        - HCA breaks: weight=20 (very important)

    Soft: no member of staff assigned to more than 4 consecutive 1/2:1 blocks. weight=1 (moderately important)

    Soft: HCAs should be preferred for observation assignments over RMNs. weight=0.5 (moderately important)

## Approach
We use a combination of constraint satisfaction and heuristic greedy search. Given all the staffers and tasks, we solve for each time block individually, in chronological order. For a given block, we find all possible solutions that satisfy our hard constraints. Each solution is given a score based on the soft constraint weights. We keep the top K scoring viable solutions and use them to seed the next block; this proceeds recursively until we have solved every block. The result is a list of the K best solutions found.

## TODO
- Use an excel spreadsheet as input
- Build javascript front-end and make it a web app

