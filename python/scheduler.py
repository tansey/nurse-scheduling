'''
    Program to generate valid time allocations of a mental ward staff.


    Given:

    Two staff lists. Each list applies for a specific window of time. Lists may
    contain non-empty intersections of employees.

    Each employee has a designation as RMN or HCA.

    Each employee has a designation as Male or Female

    List of 1:1 patients that must have 1 staffer assigned at all times.

    List of 2:1 patients that must have 2 staffers assigned at all times.

    List of medication times that must each have 1 RMN assigned.

    List of unavailable times for each staffer where they cannot be assigned.

    Time is divided into blocks of 30 minutes. Staff shifts overlap by 2 blocks.


    Constraints:

    Any employee working two shifts must receive a 1-hour break before the last
    2 blocks of their second shift.
        - RMN breaks are soft constraints (preferences)
        - HCA breaks are hard constraints (requirements)

    Soft: no member of staff assigned to more than 4 consecutive 1/2:1 blocks.

    Soft: HCAs should be preferred for observation assignments over RMNs.

    Hard: one person assigned to general observations at all times.

    Hard: 1:1 and 2:1 patients with Male-only flags must have Male staffers assigned.
'''
import numpy as np
from collections import defaultdict
from constraint import Problem, AllDifferentConstraint

# General weightings
RMN_OBSERVATION_PENALTY = 0.5
CONSECUTIVE_OBSERVATION_PENALTY = 1
CONSECUTIVE_UNIQUE_OBSERVATION_PENALTY = 2
RMN_NO_BREAK_PENALTY = 0.1
HCA_NO_BREAK_PENALTY = 20

class Task:
    def __init__(self, name, blocks, nstaffers):
        self.name = name
        self.blocks = blocks
        self.nstaffers = nstaffers

    def score(self, assignments):
        '''All blocks must have a staffer assigned'''
        assigned_blocks = [b for b, _, _ in assignments]
        for block in self.blocks:
            if block not in assigned_blocks:
                return -1
        for block, task, staffers in assignments:
            if len(staffers) != self.nstaffers:
                return -1
        return self.task_score(assignments)

    def valid(self, staffer):
        return self.task_valid(staffer)

    def task_score(self, assignments):
        return 0

    def task_valid(self, staffer):
        return True

    def __repr__(self):
        return self.name

class MedicationTask(Task):
    def __init__(self, blocks):
        Task.__init__(self, 'Medication', blocks, 1)

    def task_valid(self, staffer):
        return staffer.rmn

class GeneralObservationTask(Task):
    def __init__(self, blocks):
        Task.__init__(self, 'General observations', blocks, 1)

class PatientObservationTask(Task):
    def __init__(self, name, blocks, nstaffers, male_only):
        Task.__init__(self, 'Patient {} ({}:1)'.format(name, nstaffers), blocks, nstaffers)
        self.male_only = male_only


    def task_valid(self, staffer):
        return (not self.male_only) or (self.male_only and staffer.male)


class Staffer:
    def __init__(self, name, rmn, male, available_blocks):
        self.name = name
        self.rmn = rmn
        self.male = male
        self.available_blocks = available_blocks

    def valid(self, task, block):
        return block in self.available_blocks and task.valid(self)

    def __repr__(self):
        return self.name

class Schedule:
    def __init__(self, blocks, block_times, staffers, tasks,
                        min_break_block, max_break_block, max_on_break):
        self.blocks = blocks
        self.block_times = block_times
        self.min_break_block = min_break_block
        self.max_break_block = max_break_block
        self.max_on_break = max_on_break
        self.staffers = staffers
        self.tasks = tasks

def solve_block(block, cur_solution, schedule, top_per_block, obs_penalties):
    print '\tSetting up'
    block_time = schedule.block_times[block]

    # Get the available staffers
    staffers = [s for s in schedule.staffers if block in s.available_blocks]

    # Get the tasks
    tasks = [t for t in schedule.tasks if block in t.blocks]

    # Are breaks allowed in this block?
    breaks_allowed = block >= schedule.min_break_block and block <= schedule.max_break_block

    # Setup the constraint satisfaction problem
    problem = Problem()
    block_vars = []

    # Add each task to the list that need to be fulfilled
    for task in tasks:
        options = [s for s in staffers if task.valid(s)]
        for i in range(task.nstaffers):
            variable = '{} {} {}'.format(block_time, task, i)
            block_vars.append(variable)
            problem.addVariable(variable, options)

    # Allow up to max_on_break people on break at once
    if breaks_allowed:
        prev_breaks = [s for v, s in cur_solution.iteritems() if 'Break' in str(v) and s != 'None']
        breakable_staffers = [s for s in staffers if s not in prev_breaks]
        for break_idx in range(schedule.max_on_break):
            problem.addVariable('{} Break {}'.format(block_time, break_idx), breakable_staffers + ['None'])
            block_vars.append('{} Break {}'.format(block_time, break_idx))

    # Only one task per person
    problem.addConstraint(AllDifferentConstraint(), block_vars)

    # Find every possible solution
    print '\tSolving'
    solutions = problem.getSolutions()

    # Score the options
    print '\tScoring'
    obs_tasks = [task for task in tasks if isinstance(task, PatientObservationTask) or isinstance(task, GeneralObservationTask)]
    scores = np.zeros(len(solutions))
    for sidx, solution in enumerate(solutions):
        score = 0
        # Add the current block observations
        for task in obs_tasks:
            staffer = solution['{} {} {}'.format(block_time, task, i)]
            score += obs_penalties[staffer]
        
        if breaks_allowed:
            for break_idx in range(schedule.max_on_break):
                on_break = solution['{} Break {}'.format(block_time, break_idx)]
                if on_break == 'None':
                    continue
                elif on_break.rmn:
                    score -= RMN_NO_BREAK_PENALTY
                else:
                    score -= HCA_NO_BREAK_PENALTY
        scores[sidx] = score

    print '\tFinding top'
    top_solutions = [solutions[i] for i in np.argsort(scores)[:top_per_block]]
    top_scores = scores[np.argsort(scores)[:top_per_block]]

    return top_solutions, top_scores

def solve_block_greedy(schedule, max_on_break=2, top_per_block=2):
    print '{} Solving initial block {}'.format(0, schedule.block_times[0])
    obs_tasks = [t for t in schedule.tasks if isinstance(t, PatientObservationTask) or isinstance(t, GeneralObservationTask)]
    obs_penalties = {staffer: RMN_OBSERVATION_PENALTY if staffer.rmn else 0 for staffer in schedule.staffers}
    top_solutions, top_scores = solve_block(schedule.blocks[0], {}, schedule, top_per_block, obs_penalties)
    for block in schedule.blocks[1:]:
        print '{} Solving block {} with {} starting solutions'.format(block, schedule.block_times[block], len(top_solutions))
        next_round_solutions = []
        next_round_scores = []
        for solution, score in zip(top_solutions, top_scores):
            # Calculate the penalties for each staffer being put on observation duty
            print '\tCalculating staffer penalties'
            obs_counts = defaultdict(int)
            if block >= 3:
                for b in range(block-3, block):
                    for task in obs_tasks:
                        if b not in task.blocks:
                            continue
                        for i in range(task.nstaffers):
                            staffer = solution['{} {} {}'.format(schedule.block_times[b], task, i)]
                            obs_counts[staffer] += 1
                for s,c in obs_counts.iteritems():
                    if c == 3:
                        obs_penalties[s] = CONSECUTIVE_OBSERVATION_PENALTY + (RMN_OBSERVATION_PENALTY if s.rmn else 0)
                    else:
                        obs_penalties[s] = RMN_OBSERVATION_PENALTY if s.rmn else 0

            S, R = solve_block(block, solution, schedule, top_per_block, obs_penalties)

            print '\tPicking best {} solutions'.format(top_per_block)
            # Add good solutions
            for s, r in zip(S, R):
                r += score
                if len(next_round_solutions) < top_per_block or r < next_round_scores[top_per_block-1]:
                    for k, v in solution.iteritems():
                        s[k] = v
                    next_round_solutions.append(s)
                    next_round_scores.append(r)
            # Filter to just the top
            if len(next_round_solutions) > top_per_block:
                chosen = np.argsort(next_round_scores)[:top_per_block]
                next_round_solutions = [s for i,s in enumerate(next_round_solutions) if i in chosen]
                next_round_scores = [s for i,s in enumerate(next_round_scores) if i in chosen]

            print ''

        # Update the best solutions
        top_solutions = next_round_solutions
        top_scores = next_round_scores

        print_solution(schedule, top_solutions[0], max_block=block)

    print '***** SOLUTION 1 *****'
    print_solution(schedule, top_solutions[0])
    print '***** SOLUTION 2 *****'
    print_solution(schedule, top_solutions[1])
    print 'Scores: ', next_round_scores
    # import matplotlib.pylab as plt
    # plt.hist(next_round_scores, bins=50)
    # plt.show()
    # return

def print_solution(schedule, solution, max_block=None):
    for task in schedule.tasks:
        print task
        for block in task.blocks:
            if max_block is not None and block > max_block:
                continue
            staffers = [str(solution['{} {} {}'.format(schedule.block_times[block], task, i)]) for i in range(task.nstaffers)]
            print '{}: {}'.format(schedule.block_times[block], ', '.join(staffers))
        print ''
    print 'Breaks'
    for block in schedule.blocks[schedule.min_break_block:schedule.max_break_block+1]:
        if max_block is not None and block > max_block:
            continue
        staffers = [str(solution['{} Break {}'.format(schedule.block_times[block], i)]) for i in range(schedule.max_on_break)]
        staffers = [s for s in staffers if s != 'None']
        if len(staffers) > 0:
            print '{}: {}'.format(schedule.block_times[block], ', '.join(staffers))
    print ''


if __name__ == '__main__':
    blocks = range(26)
    block_times = [str(7+(i+1)/2) + ':' + ('00' if i % 2 == 1 else '30') for i in blocks]
    print list(enumerate(block_times))
    tasks = [MedicationTask([2, 10, 20]), GeneralObservationTask(blocks),
             PatientObservationTask('A', blocks, 2, False),
             PatientObservationTask('B', blocks, 2, True),
             PatientObservationTask('C', blocks, 1, False)]
    staffers = [Staffer('Lily', True, False, [0,1,2,3,4,5,12,13]),
                Staffer('Jack', True, True, range(14)),
                Staffer('Jenny', True, False, range(26)),
                Staffer('Bob', False, True, range(26)),
                Staffer('Douglas', False, True, range(5) + range(12,26)),
                Staffer('Maxine', False, False, range(26)),
                Staffer('Sally', False, False, range(26)),
                Staffer('Nicola', False, True, range(14)),
                Staffer('Marie', False, False, range(14)),
                Staffer('Mary', True, False, range(14,26)),
                Staffer('Eve', True, False, range(14,26)),
                Staffer('Ryan', False, True, range(14,26)),
                Staffer('Michael', False, True, range(14,26))]
    min_break_block = 12
    max_break_block = 22
    max_on_break = 1

    schedule = Schedule(blocks, block_times, staffers, tasks, min_break_block, max_break_block, max_on_break)

    solve_block_greedy(schedule)
