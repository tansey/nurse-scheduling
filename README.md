# Nurse scheduling
This is a simple proof-of-concept project to help mental health nurses schedule their day. The app will take the staffer lists, and the different tasks for the day, and create a schedule automatically that tries to balance all the preferences for breaks, minimal RMNs on observations, etc.

## Example
Imagine we have a schedule setup like the following example done by-hand by an RMN:

![Example schedule](https://raw.githubusercontent.com/tansey/nurse-scheduling/master/example.jpg)

The current scheduler app would output the following schedule automatically:

    Time    Medication               General observations     Patient A (2:1)          Patient B (2:1)          Patient C (1:1)           Breaks                   Unassigned
    7:30:                            Jack                     Maxine, Jenny            Bob, Douglas             Marie                                             Lily, Sally, Nicola
    8:00:                            Jack                     Maxine, Douglas          Bob, Nicola              Sally                                             Lily, Jenny, Marie
    8:30:   Jenny                    Jack                     Marie, Maxine            Nicola, Douglas          Sally                                             Lily, Bob
    9:00:                            Jack                     Marie, Sally             Nicola, Douglas          Bob                                               Lily, Jenny, Maxine
    9:30:                            Jack                     Marie, Sally             Douglas, Bob             Maxine                                            Lily, Jenny, Nicola
    10:00:                           Jack                     Marie, Maxine            Nicola, Bob              Sally                                             Lily, Jenny
    10:30:                           Jack                     Sally, Marie             Nicola, Bob              Maxine                                            Jenny
    11:00:                           Jack                     Sally, Marie             Bob, Nicola              Maxine                                            Jenny
    11:30:                           Jack                     Sally, Marie             Nicola, Bob              Maxine                                            Jenny
    12:00:                           Jack                     Sally, Marie             Nicola, Bob              Maxine                                            Jenny
    12:30:  Jenny                    Jack                     Marie, Sally             Bob, Nicola              Maxine
    13:00:                           Jack                     Marie, Maxine            Bob, Nicola              Sally                                             Jenny
    13:30:                           Jack                     Sally, Douglas           Bob, Nicola              Marie                    Maxine                   Lily, Jenny
    14:00:                           Jack                     Sally, Marie             Nicola, Bob              Douglas                  Maxine                   Lily, Jenny
    14:30:                           Sally                    Jenny, Maxine            Douglas, Michael         Ryan                     Bob                      Mary, Eve
    15:00:                           Sally                    Maxine, Eve              Douglas, Michael         Ryan                     Bob                      Jenny, Mary
    15:30:                           Sally                    Bob, Mary                Ryan, Michael            Maxine                   Douglas                  Jenny, Eve
    16:00:                           Sally                    Mary, Ryan               Bob, Michael             Maxine                   Douglas                  Jenny, Eve
    16:30:                           Sally                    Maxine, Jenny            Bob, Michael             Douglas                  Ryan                     Mary, Eve
    17:00:                           Sally                    Douglas, Maxine          Bob, Michael             Eve                      Ryan                     Jenny, Mary
    17:30:  Mary                     Sally                    Maxine, Jenny            Ryan, Douglas            Bob                      Michael                  Eve
    18:00:                           Sally                    Maxine, Mary             Ryan, Bob                Douglas                  Michael                  Jenny, Eve
    18:30:                           Sally                    Douglas, Maxine          Michael, Ryan            Bob                      Eve                      Jenny, Mary
    19:00:                           Sally                    Bob, Michael             Ryan, Douglas            Maxine                                            Jenny, Mary, Eve
    19:30:                           Sally                    Douglas, Ryan            Bob, Michael             Maxine                                            Jenny, Mary, Eve
    20:00:                           Sally                    Michael, Bob             Douglas, Ryan            Maxine                                            Jenny, Mary, Eve


## Given

    Time is divided into blocks of 30 minutes.

    List of staff, each with different available blocks of time

    Each employee has a designation as RMN (Registered Mental health Nurse) or HCA (Health Care Assistant).

    Each employee has a designation as Male or Female (necessary for some male-only patients)

    List of 1:1 patients that must have 1 staffer assigned at all times; optional male staffers only flag for each patient.

    List of 2:1 patients that must have 2 staffers assigned at all times; optional male staffers only flag for each patient.

    List of medication times that must each have 1 RMN assigned.

## Constraints
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

## Contact
If you actually would like to use this for your nursing schedules, contact me: wes.tansey@gmail.com -- I'd love for it to be useful to someone!

