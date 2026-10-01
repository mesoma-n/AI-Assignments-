from __future__ import division
from __future__ import print_function

import sys
import math
import time
import queue as Q
import resource


#### SKELETON CODE ####
## The Class that Represents the Puzzle
class PuzzleState(object):
    def __init__(self, config, n, parent=None, action="Initial", cost=0):
        if n*n != len(config) or n < 2:
            raise Exception("The length of config is not correct!")
        if set(config) != set(range(n*n)):
            raise Exception("Config contains invalid/duplicate entries : ", config)

        self.n        = n
        self.cost     = cost
        self.parent   = parent
        self.action   = action
        self.config   = config
        self.children = []
        self.blank_index = self.config.index(0)

    def display(self):
        for i in range(self.n):
            print(self.config[self.n*i : self.n*(i+1)])

    def move_up(self):
        if self.blank_index < self.n:
            return None
        new_config = self.config[:]
        swap_index = self.blank_index - self.n
        new_config[self.blank_index], new_config[swap_index] = new_config[swap_index], new_config[self.blank_index]
        return PuzzleState(new_config, self.n, self, "Up", self.cost + 1)

    def move_down(self):
        if self.blank_index >= self.n * (self.n - 1):
            return None
        new_config = self.config[:]
        swap_index = self.blank_index + self.n
        new_config[self.blank_index], new_config[swap_index] = new_config[swap_index], new_config[self.blank_index]
        return PuzzleState(new_config, self.n, self, "Down", self.cost + 1)

    def move_left(self):
        if self.blank_index % self.n == 0:
            return None
        new_config = self.config[:]
        swap_index = self.blank_index - 1
        new_config[self.blank_index], new_config[swap_index] = new_config[swap_index], new_config[self.blank_index]
        return PuzzleState(new_config, self.n, self, "Left", self.cost + 1)

    def move_right(self):
        if self.blank_index % self.n == self.n - 1:
            return None
        new_config = self.config[:]
        swap_index = self.blank_index + 1
        new_config[self.blank_index], new_config[swap_index] = new_config[swap_index], new_config[self.blank_index]
        return PuzzleState(new_config, self.n, self, "Right", self.cost + 1)

    def expand(self):
        if len(self.children) != 0:
            return self.children
        children = [self.move_up(), self.move_down(), self.move_left(), self.move_right()]
        self.children = [state for state in children if state is not None]
        return self.children


def _solution_path(state):
    path = []
    while state.parent is not None:
        path.append(state.action)
        state = state.parent
    path.reverse()
    return path


def _ram_mb(start_ram):
    used = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss - start_ram
    # Linux reports ru_maxrss in KiB; macOS reports bytes.
    if sys.platform == "darwin":
        return used / (2 ** 20)
    return used / 1024.0


def writeOutput(goal_state, nodes_expanded, max_search_depth, running_time, max_ram_usage):
    path = _solution_path(goal_state)
    with open("output.txt", "w") as output:
        output.write("path to goal: %s\n" % path)
        output.write("cost of path: %d\n" % len(path))
        output.write("nodes expanded: %d\n" % nodes_expanded)
        output.write("search depth: %d\n" % goal_state.cost)
        output.write("max search depth: %d\n" % max_search_depth)
        output.write("running time: %.8f\n" % running_time)
        output.write("max ram usage: %.8f\n" % max_ram_usage)


def bfs_search(initial_state):
    start_time = time.time()
    start_ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    frontier = Q.Queue()
    frontier.put(initial_state)
    frontier_configs = {tuple(initial_state.config)}
    explored = set()
    nodes_expanded = 0
    max_search_depth = 0

    while not frontier.empty():
        state = frontier.get()
        key = tuple(state.config)
        frontier_configs.remove(key)

        if test_goal(state):
            writeOutput(state, nodes_expanded, max_search_depth,
                        time.time() - start_time, _ram_mb(start_ram))
            return state

        explored.add(key)
        nodes_expanded += 1

        for child in state.expand():
            child_key = tuple(child.config)
            if child_key not in explored and child_key not in frontier_configs:
                frontier.put(child)
                frontier_configs.add(child_key)
                if child.cost > max_search_depth:
                    max_search_depth = child.cost
    return None


def dfs_search(initial_state):
    start_time = time.time()
    start_ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    frontier = [initial_state]
    frontier_configs = {tuple(initial_state.config)}
    explored = set()
    nodes_expanded = 0
    max_search_depth = 0

    while frontier:
        state = frontier.pop()
        key = tuple(state.config)
        frontier_configs.remove(key)

        if test_goal(state):
            writeOutput(state, nodes_expanded, max_search_depth,
                        time.time() - start_time, _ram_mb(start_ram))
            return state

        explored.add(key)
        nodes_expanded += 1

        # Reverse UDLR when pushing so popping visits UDLR.
        for child in reversed(state.expand()):
            child_key = tuple(child.config)
            if child_key not in explored and child_key not in frontier_configs:
                frontier.append(child)
                frontier_configs.add(child_key)
                if child.cost > max_search_depth:
                    max_search_depth = child.cost
    return None


def A_star_search(initial_state):
    start_time = time.time()
    start_ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    frontier = Q.PriorityQueue()
    counter = 0
    frontier.put((calculate_total_cost(initial_state), counter, initial_state))
    frontier_configs = {tuple(initial_state.config)}
    explored = set()
    nodes_expanded = 0
    max_search_depth = 0

    while not frontier.empty():
        _, _, state = frontier.get()
        key = tuple(state.config)
        frontier_configs.remove(key)

        if test_goal(state):
            writeOutput(state, nodes_expanded, max_search_depth,
                        time.time() - start_time, _ram_mb(start_ram))
            return state

        explored.add(key)
        nodes_expanded += 1

        for child in state.expand():
            child_key = tuple(child.config)
            if child_key not in explored and child_key not in frontier_configs:
                counter += 1
                frontier.put((calculate_total_cost(child), counter, child))
                frontier_configs.add(child_key)
                if child.cost > max_search_depth:
                    max_search_depth = child.cost
    return None


def calculate_total_cost(state):
    total = state.cost
    for idx, value in enumerate(state.config):
        if value != 0:
            total += calculate_manhattan_dist(idx, value, state.n)
    return total


def calculate_manhattan_dist(idx, value, n):
    current_row, current_col = divmod(idx, n)
    goal_row, goal_col = divmod(value, n)
    return abs(current_row - goal_row) + abs(current_col - goal_col)


def test_goal(puzzle_state):
    return puzzle_state.config == list(range(puzzle_state.n * puzzle_state.n))


def main():
    search_mode = sys.argv[1].lower()
    begin_state = sys.argv[2].split(",")
    begin_state = list(map(int, begin_state))
    board_size  = int(math.sqrt(len(begin_state)))
    hard_state  = PuzzleState(begin_state, board_size)
    start_time  = time.time()

    if   search_mode == "bfs": bfs_search(hard_state)
    elif search_mode == "dfs": dfs_search(hard_state)
    elif search_mode == "ast": A_star_search(hard_state)
    else:
        print("Enter valid command arguments !")

    end_time = time.time()
    print("Program completed in %.3f second(s)"%(end_time-start_time))

if __name__ == '__main__':
    main()
