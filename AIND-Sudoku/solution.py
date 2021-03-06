assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# for diagnoal sudoku, add the diagnoal neighbors in the peer
diagonal_units= [[s+t  for s,t in list(zip(rows, cols))],  [s+t  for s,t in list(zip(rows, cols[::-1]))]]

unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # for two celles in any row, column and block that has exactly two possibilities 
    # and these two possibilities are the same

     
    twins_box = [sorted([box, peer]) for box in values.keys() for peer in peers[box] if len(values[box]) == 2 and len(values[peer]) == 2 and values[box] == values[peer] ]
    twins_set = set(map(tuple, twins_box)) 
    twins_box = list(map(list, twins_set)) #remove duplicates
        
    # Eliminate the naked twins as possibilities for their peers

    for naked_twins in twins_box:
        digit_pair = values[naked_twins[0]]
        for peer in peers[naked_twins[0]]:
            if peer in peers[naked_twins[1]]: 
                # find peer in both neighborhood 
                for digit in digit_pair:
                    assign_value(values, peer, values[peer].replace(digit, '')) 

    
    return values



def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    values = []
    all_digits = '123456789'
    for c in grid:
        if c == '.':
            values.append(all_digits)
        elif c in all_digits:
            values.append(c)
    assert(len(values) == 81)
    return dict(zip(boxes, values))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit, '')) 
    return values

def only_choice(values):
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
    return values

def reduce_puzzle(values):
    stalled = False

    while not stalled:
        #check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        #use eliminate 
        values = eliminate(values)
        #eliminate naked twins
        values = naked_twins(values)
        #use only-choice 
        values = only_choice(values)
        #check how many boxes have a deterimined value
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        #if no new values were added, stop the loop
        stalled = solved_values_before == solved_values_after
        #sanity check, return False if there is a box with zero available values
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False

    return values



def search(values):
    '''
      Using depth-first-search and propagation, create a search tree and solve the sudoku
      
    '''
    #reduce the puzzle using previous function
    values = reduce_puzzle(values)
    
    if values is False:
        return False
    elif all(len(values[box]) == 1 for box in values):
        return values

    # choose one of the unfilled squares with the fewest possibilities 
    n, min_box = min( (len(values[s]), s) for s in boxes if len(values[s]) > 1   )
    
    min_box_value = values[min_box]
    # user recursion to solve each one of the resulting sudokus, and if one returns a 
    # value (not False), return that answer!
    for digit in min_box_value:
        new_values = values.copy()
        assign_value(new_values, min_box, digit)
        attempt = search(new_values)
        if attempt:
            return attempt



def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """

    values = grid_values(grid)

    return search(values)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
