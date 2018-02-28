# Nurse scheduling
This is a simple proof-of-concept project to help mental health nurses schedule their day. The app will take the staffer lists, and the different tasks for the day, and create a schedule automatically that tries to balance all the preferences for breaks, minimal RMNs on observations, etc.

## Example
Imagine we have a schedule setup like the following example done by-hand by an RMN:

![Example schedule](https://raw.githubusercontent.com/tansey/nurse-scheduling/master/example.jpg)

The current scheduler app would output the following schedule automatically:

    Time    Medication               General observations     Patient A (2:1)          Patient B (2:1)          Patient C (1:1)           Breaks
    7:30:                            Marie                    Sally, Maxine            Nicola, Douglas          Bob                             
    8:00:                            Marie                    Sally, Maxine            Nicola, Douglas          Bob                             
    8:30:   Jack                     Bob                      Sally, Lily              Douglas, Nicola          Marie                           
    9:00:                            Lily                     Maxine, Bob              Jack, Nicola             Jenny                           
    9:30:                            Marie                    Maxine, Jenny            Douglas, Bob             Sally                           
    10:00:                           Maxine                   Sally, Jenny             Nicola, Bob              Marie                           
    10:30:                           Sally                    Marie, Jenny             Nicola, Bob              Jack                            
    11:00:                           Maxine                   Nicola, Jenny            Jack, Bob                Sally                           
    11:30:                           Maxine                   Sally, Bob               Jack, Nicola             Marie                           
    12:00:                           Maxine                   Jenny, Sally             Bob, Jack                Marie                           
    12:30:  Jack                     Marie                    Maxine, Sally            Nicola, Bob              Jenny                           
    13:00:                           Jenny                    Jack, Marie              Nicola, Bob              Sally                           
    13:30:                           Maxine                   Lily, Jenny              Douglas, Jack            Nicola                   Marie  
    14:00:                           Maxine                   Bob, Lily                Douglas, Nicola          Marie                    Sally  
    14:30:                           Sally                    Douglas, Eve             Ryan, Bob                Michael                  Maxine 
    15:00:                           Maxine                   Sally, Mary              Michael, Ryan            Bob                      Douglas
    15:30:                           Maxine                   Douglas, Mary            Michael, Ryan            Sally                    Bob    
    16:00:                           Jenny                    Bob, Mary                Douglas, Michael         Maxine                   Ryan   
    16:30:                           Douglas                  Sally, Jenny             Ryan, Bob                Eve                      Michael
    17:00:                           Sally                    Maxine, Douglas          Michael, Ryan            Bob                      Jenny  
    17:30:  Jenny                    Sally                    Ryan, Eve                Michael, Douglas         Maxine                   Mary   
    18:00:                           Mary                     Maxine, Jenny            Michael, Douglas         Bob                      Eve    
    18:30:                           Mary                     Bob, Jenny               Ryan, Douglas            Sally                           
    19:00:                           Maxine                   Michael, Ryan            Bob, Douglas             Sally                           
    19:30:                           Maxine                   Ryan, Jenny              Michael, Bob             Sally                           
    20:00:                           Maxine                   Douglas, Jenny           Michael, Ryan            Eve                             

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

