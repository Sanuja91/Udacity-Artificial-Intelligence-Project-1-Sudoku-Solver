import numpy as np
import pydash as py_

from utils import *

def grid_values(grid):
    """Convert grid string into {<box>: <value>} dict with '.' value for empties.

    Args:
        grid: Sudoku grid in string form, 81 characters long
    Returns:
        Sudoku grid in dictionary form:
        - keys: Box labels, e.g. 'A1'
        - values: Value in corresponding box, e.g. '8', or '.' if it is empty.
    """
    rows = 'ABCDEFGHI'
    cols = '123456789'
    values = {}
    count = 0
    for row in rows:
        for col in cols:
            if grid[count] == '.':
                values[row + col] = '123456789'
            else:
                values[row + col] = grid[count]

            count += 1  

    return values

def get_peers(key, values):

    keys = values.keys()

    boxes = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

    row = key[0]
    col = key[1]
    row_peers = [key for key in keys if row in key]
    col_peers = [key for key in keys if col in key]
    box_peers = []
    for box in boxes:
        if key in box:
            box_peers = box
            break

    return row_peers, col_peers, box_peers


    
def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    keys = values.keys()

    for key in keys:
        if len(values[key]) == 1:
            peers = []
            row_peers, col_peers, box_peers = get_peers(key, values)
            peers.append(row_peers)
            peers.append(col_peers)
            peers.append(box_peers)

            peers = py_.uniq(py_.flatten(peers))

            for peer in peers:
                if len(values[peer]) > 1:
                    values[peer] = values[peer].replace(values[key], '')

    return values

def sub_only_choice(peers, values):

    peer_values = [values[peer] for peer in peers]
    joined_values = ''.join(peer_values)
    unique_values = []
    
    for joined_value in set(joined_values):
        if joined_values.count(joined_value) == 1:
            unique_values.append(joined_value)
    
    for unique_value in unique_values:
        for peer in peers:
            if unique_value in values[peer]:
                values[peer] = unique_value
                break
    return values

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    keys = values.keys()

    for key in keys:
        if len(values[key]) > 1:
            row_peers, col_peers, box_peers = get_peers(key, values)
            values = sub_only_choice(row_peers, values)
            values = sub_only_choice(col_peers, values)
            values = sub_only_choice(box_peers, values)

    return values


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Your code here: Use the Eliminate Strategy
        values = eliminate(values)

        # Your code here: Use the Only Choice Strategy
        values = only_choice(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

# `grid` is defined in the test code scope as the following:
# (note: changing the value here will _not_ change the test code)
grid = '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..'
grid_hard = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'


values = grid_values(grid_hard)
search(values)