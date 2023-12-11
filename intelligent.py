import numpy as np

WHITE = 0
CLUE = -1
BLACK = -2
DOWN = 'down'
RIGHT = 'right'

class KakuroCell():
    def __init__(self, location, category):
        self.location = location
        self.category = category

class KakuroClue():
    def __init__(self, direction, length, goal_sum):
        self.direction = direction
        self.length = length
        self.goal_sum = goal_sum
        self.location = None

class KakuroClueCell(KakuroCell):
    def __init__(self, location, down_clue, right_clue):
        super().__init__(location, category=CLUE)
        self.down_clue = down_clue
        if down_clue is not None:
            self.down_clue.location = self.location
        self.right_clue = right_clue
        if right_clue is not None:
            self.right_clue.location = self.location

class KakuroBlackCell(KakuroCell):
    def __init__(self, location):
        super().__init__(location, category=BLACK)

class KakuroWhiteCell(KakuroCell):
    def __init__(self, location, value=0):
        super().__init__(location, category=WHITE)
        self.value = value

class KakuroPuzzle():
    def __init__(self, height, width, cells):
        self.height = height
        self.width = width
        self.cells = cells
        self.clues = self.create_clues()
        self.puzzle = self.create_puzzle()
        self.print_puzzle()

    def print_puzzle(self):
        for i in range(self.height):
            for j in range(self.width):
                cell = self.puzzle[i][j]
                if cell.category == BLACK:
                    print("B", end=" ")
                elif cell.category == CLUE:
                    print("C", end=" ")
                elif cell.category == WHITE:
                    print(cell.value, end=" ")
            print()
        print()

    def create_clues(self):
        clues = []
        for cell in self.cells:
            if cell.category == CLUE:
                if cell.down_clue is not None:
                    clues.append(cell.down_clue)
                if cell.right_clue is not None:
                    clues.append(cell.right_clue)
        return clues

    def create_puzzle(self):
        puzzle = [[KakuroWhiteCell((i, j)) for j in range(self.width)] for i in range(self.height)]
        for cell in self.cells:
            puzzle[cell.location[0]][cell.location[1]] = cell
        return puzzle

    def get_cell_set(self, clue):
        cell_set = []
        if clue.direction == DOWN:
            for i in range(clue.length):
                cell_set.append(self.puzzle[clue.location[0] + i + 1][clue.location[1]])
        elif clue.direction == RIGHT:
            for i in range(clue.length):
                cell_set.append(self.puzzle[clue.location[0]][clue.location[1] + i + 1])
        return cell_set

    def assign_clue(self, clue, value_set):
        if clue.direction == DOWN:
            for i in range(clue.length):
                self.puzzle[clue.location[0] + i + 1][clue.location[1]].value = value_set[i]
        elif clue.direction == RIGHT:
            for i in range(clue.length):
                self.puzzle[clue.location[0]][clue.location[1] + i + 1].value = value_set[i]

    def is_clue_assigned(self, clue):
        return self.clue_unassigned_count(clue) == 0

    def clue_unassigned_count(self, clue):
        cell_set = self.get_cell_set(clue)
        unassigned_count = 0
        for cell in cell_set:
            if cell.value == 0:
                unassigned_count += 1
        return unassigned_count

    def is_complete(self):
        is_complete = True
        for i in range(self.height):
            for j in range(self.width):
                if self.puzzle[i][j].category == WHITE and self.puzzle[i][j].value == 0:
                    is_complete = False
        return is_complete

    def is_consistent(self):
        for clue in self.clues:
            cell_set = self.get_cell_set(clue)
            if self.is_clue_assigned(clue):
                current_sum = 0
                values = []
                for cell in cell_set:
                    values.append(cell.value)
                    current_sum += cell.value
                if current_sum != clue.goal_sum or any(values.count(x) > 1 for x in values):
                    return False
        return True
        
import copy

DOWN = 'down'
RIGHT = 'right'
DIGITS = [1, 2, 3, 4, 5, 6, 7, 8, 9]

class KakuroAgent():
    def __init__(self, puzzle):
        self.puzzle = puzzle

    # Solve the puzzle using backtracking
    def solve(self):
        solution = self.backtracking_search(self.puzzle)
        if solution is not None:
            solution.print_puzzle()
            puzzle = solution
        else:
            print("No solution found")

    def backtracking_search(self, puzzle):
        return self.recursive_backtracking(copy.deepcopy(puzzle))

    def recursive_backtracking(self, assignment):
        if assignment.is_complete() and assignment.is_consistent():
            print("YAY!")
            return assignment

        clue = self.select_unassigned_clue(assignment)

        if clue is not None:
            cell_set = assignment.get_cell_set(clue)
            value_sets = self.order_domain_values(clue, cell_set, assignment)

            for value_set in value_sets:
                if self.is_consistent(clue, copy.deepcopy(value_set), copy.deepcopy(assignment)):
                    assignment.assign_clue(clue, value_set)
                    assignment.print_puzzle()
                    result = self.recursive_backtracking(copy.deepcopy(assignment))
                    if result is not None:
                        return result

        return None

    def select_unassigned_clue(self, assignment):
        for clue in assignment.clues:
            if not assignment.is_clue_assigned(clue):
                return clue

    def order_domain_values(self, clue, cell_set, assignment):
        value_sets = []
        assigned_cells = []
        unassigned_cells = []
        allowed_values = copy.deepcopy(DIGITS)

        for cell in cell_set:
            if cell.value == 0:
                unassigned_cells.append(cell)
            else:
                if cell.value in allowed_values:
                    allowed_values.remove(cell.value)
                assigned_cells.append(cell)

        current_sum = 0
        for cell in assigned_cells:
            current_sum += cell.value

        net_goal_sum = clue.goal_sum - current_sum
        net_cell_count = clue.length - len(assigned_cells)
        unassigned_value_sets = self.sum_to_n(net_goal_sum, net_cell_count, allowed_values)

        for unassigned_value_set in unassigned_value_sets:
            variable_set = copy.deepcopy(cell_set)
            value_set = []

            for cell in variable_set:
                if cell.value == 0:
                    value_set.append(unassigned_value_set.pop(0))
                else:
                    value_set.append(cell.value)

            value_sets.append(value_set)

        return value_sets

    # Returns different ways to write integer n as the sum of k numbers between 1 and 9
    def sum_to_n(self, n, k, allowed_values):
        if k == 1 and n in allowed_values:
            return [[n]]

        combos = []

        for i in allowed_values:
            allowed_values_copy = copy.deepcopy(allowed_values)
            allowed_values_copy.remove(i)

            if n - i > 0:
                combos += [[i] + combo for combo in self.sum_to_n(n - i, k - 1, allowed_values_copy)]

        for combo in combos:
            if any(combo.count(x) > 1 for x in combo):
                combos.remove(combo)

        return combos

    def is_consistent(self, clue, value_set, assignment):
        assignment.assign_clue(clue, value_set)
        assignment.print_puzzle()
        return assignment.is_consistent()

from operator import itemgetter

class IntelligentKakuroAgent(KakuroAgent):
    def __init__(self, puzzle):
        super().__init__(puzzle)

    # Minimum Remaining Values (Most Constrained Variable) - chooses the clue with the
    # least number of unassigned cells, but gives priority to clues that are partially assigned
    def select_unassigned_clue(self, assignment):
        clue_list = []
        partial_assigned_list = []
        unassigned_list = []

        for clue in assignment.clues:
            if not assignment.is_clue_assigned(clue):
                unassigned_count = assignment.clue_unassigned_count(clue)
                if unassigned_count == clue.length:
                    unassigned_list.append((clue, unassigned_count))
                else:
                    partial_assigned_list.append((clue, unassigned_count))

        unassigned_list.sort(key=itemgetter(1))
        partial_assigned_list.sort(key=itemgetter(1))
        clue_list = partial_assigned_list + unassigned_list

        return clue_list[0][0]

import copy
import timeit

# Define cells for the Kakuro puzzle
cells = []

# 5X5 sample:
# row 1
cells.append(KakuroBlackCell((0, 0)))
cells.append(KakuroBlackCell((0, 1)))
cells.append(KakuroClueCell((0, 2), KakuroClue(DOWN, 4, 22), None))
cells.append(KakuroClueCell((0, 3), KakuroClue(DOWN, 4, 12), None))
cells.append(KakuroBlackCell((0, 4)))

# row 2
cells.append(KakuroBlackCell((1, 0)))
cells.append(KakuroClueCell((1, 1), KakuroClue(DOWN, 2, 15), KakuroClue(RIGHT, 2, 12)))
cells.append(KakuroClueCell((1, 4), KakuroClue(DOWN, 2, 9), None))

# row 3
cells.append(KakuroClueCell((2, 0), None, KakuroClue(RIGHT, 4, 13)))

# row 4
cells.append(KakuroClueCell((3, 0), None, KakuroClue(RIGHT, 4, 29)))

# row 5
cells.append(KakuroBlackCell((4, 0)))
cells.append(KakuroClueCell((4, 1), None, KakuroClue(RIGHT, 2, 4)))
cells.append(KakuroBlackCell((4, 4)))

# Create a Kakuro puzzle
puzzle = KakuroPuzzle(5, 5, cells)

# Create an intelligent agent
intelligent_agent = IntelligentKakuroAgent(copy.deepcopy(puzzle))

# Measure the time taken by the intelligent agent to solve the puzzle
intelligent_start = timeit.default_timer()
intelligent_agent.solve()
intelligent_stop = timeit.default_timer()
intelligent_time = intelligent_stop - intelligent_start

# Print the time taken by the intelligent agent to solve the puzzle
print("Intelligent agent solved the puzzle in: \t", str(intelligent_time))
