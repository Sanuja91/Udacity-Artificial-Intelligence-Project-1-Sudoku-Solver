
from utils import *
import pydash as py_

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
left_diagonal_units  = [rows[x] + cols[x] for x in range(len(cols))]
right_diagonal_units  = [rows[x] + cols[len(cols) - 1 - x] for x in range(len(cols))]
unitlist = row_units + column_units + square_units 

# DONE: Update the unit list to add the new diagonal units
unitlist = unitlist + left_diagonal_units + right_diagonal_units


# Must be called after all units (including diagonals) are added to the unitlist
units = extract_units(unitlist, boxes)
peers = extract_peers(units, boxes)

def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    The naked twins strategy says that if you have two or more unallocated boxes
    in a unit and there are only two digits that can go in those two boxes, then
    those two digits can be eliminated from the possible assignments of all other
    boxes in the same unit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    Your solution can either process all pairs of naked twins from the input once,
    or it can continue processing pairs of naked twins until there are no such
    pairs remaining -- the project assistant test suite will accept either
    convention. However, it will not accept code that does not process all pairs
    of naked twins from the original input. (For example, if you start processing
    pairs of twins and eliminate another pair of twins before the second pair
    is processed then your code will fail the PA test suite.)

    The first convention is preferred for consistency with the other strategies,
    and because it is simpler (since the reduce_puzzle function already calls this
    strategy repeatedly).

    See Also
    --------
    Pseudocode for this algorithm on github:
    https://github.com/udacity/artificial-intelligence/blob/master/Projects/1_Sudoku/pseudocode.md
    """
    # TODO: Implement this function!
    raise NotImplementedError


def get_peers(key, values):

    keys = values.keys()
    row = key[0]
    col = key[1]
    row_peers = [x for x in keys if row in x and key != x]
    # print("ROW PEERS", row_peers)
    col_peers = [x for x in keys if col in x and key != x]
    # print("COL PEERS", col_peers)
    square_peers = []
    left_diag_peers = []
    right_diag_peers = []
    
    for square in square_units:
        if key in square:
            square_peers = square
            square_peers = [x for x in square_peers if x != key]
            # print("SQUARE PEERS", square_peers)
            break

    if key in left_diagonal_units:
        left_diag_peers = [x for x in left_diagonal_units if x != key]
        # print("DIAG LEFT PEERS", left_diag_peers)
    if key in right_diagonal_units:
        right_diag_peers = [x for x in right_diagonal_units if x != key]
        # print("DIAG RIGHT PEERS", right_diag_peers)

    diag_peers = [peer for sub_peers in [left_diag_peers, right_diag_peers] for peer in sub_peers]

    return row_peers, col_peers, square_peers, diag_peers


def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        row_peers, col_peers, box_peers, diag_peers = get_peers(box, values)
        peers = list(set([peer for sub_peers in [row_peers, col_peers, box_peers, diag_peers] for peer in sub_peers]))
        for peer in peers:
            values[peer] = values[peer].replace(digit,'')
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
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    """
    # DONE: Copy your code from the classroom to complete this function
    keys = values.keys()

    for key in keys:
        if len(values[key]) > 1:
            row_peers, col_peers, box_peers, diag_peers = get_peers(key, values)
            peers = list(set([peer for sub_peers in [row_peers, col_peers, box_peers, diag_peers] for peer in sub_peers]))
            peer_values = [values[peer] for peer in peers]
            joined_values = list(set(''.join(peer_values)))

            if len(joined_values) != 9:
                for value in values[key]:
                    if value not in joined_values:
                        values[key] = value
                        break
                
    return values


def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable 
    """
    # DONE: Copy your code from the classroom and modify it to complete this function
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
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.
    """
    # DONE: Copy your code from the classroom to complete this function
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


def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    grid_hard = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)


    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
