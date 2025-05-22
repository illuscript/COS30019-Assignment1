def heuristic_manhattan(current, goals):
    """Calculate Manhattan distance to closest goal"""
    if not goals:
        return 0
    return min(abs(current[0] - goal[0]) + abs(current[1] - goal[1]) for goal in goals)

def ida_star(grid, as_generator=False):
    """
    IDA* implementation that maintains the same interface as your other algorithms
    """
    if not as_generator:
        path, visited_count = ida_star_search(grid)
        return path, visited_count
    else:
        return ida_star_generator(grid)

def ida_star_search(grid):
    """
    Standard IDA* search returning (path, visited_count)
    """
    start = grid.start_position
    goals = set(grid.goal_positions)
    
    # Initialize threshold to heuristic value of start
    threshold = heuristic_manhattan(start, goals)
    
    # Track total visited nodes across all iterations
    total_visited = set()
    
    # Limit iterations to prevent infinite loops
    max_iterations = 1000
    iteration = 0
    
    while iteration < max_iterations:
        # Reset path for this iteration
        path = [start]
        visited_this_iteration = set([start])
        
        # Perform threshold-limited DFS
        result = dfs_limited(grid, start, 0, threshold, path, goals, visited_this_iteration, total_visited)
        
        if result == "FOUND":
            return path, len(total_visited)
        elif result == float('inf'):
            # No solution exists
            return [], len(total_visited)
        else:
            # Update threshold to the minimum f-value that exceeded the previous threshold
            threshold = result
        
        iteration += 1
    
    # Max iterations reached
    return [], len(total_visited)

def dfs_limited(grid, node, g_cost, threshold, path, goals, visited_this_iteration, total_visited):
    """
    Depth-limited DFS that returns:
    - "FOUND" if goal is reached
    - float('inf') if no solution possible
    - minimum f-value > threshold otherwise
    """
    # Calculate f = g + h
    h_cost = heuristic_manhattan(node, goals)
    f_cost = g_cost + h_cost
    
    # If f exceeds threshold, return f for next threshold consideration
    if f_cost > threshold:
        return f_cost
    
    # Check if we reached a goal
    if node in goals:
        return "FOUND"
    
    # Track all visited nodes
    total_visited.add(node)
    
    # Explore neighbors
    min_next_threshold = float('inf')
    
    # Standard 4-directional movement
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # down, right, up, left
    
    for dx, dy in directions:
        x, y = node
        neighbor = (x + dx, y + dy)
        
        # Skip if invalid position, wall, or already in current path
        if (not grid.is_valid_position(neighbor) or 
            neighbor in path):  # Cycle detection - don't revisit nodes in current path
            continue
        
        # Add neighbor to current path
        path.append(neighbor)
        visited_this_iteration.add(neighbor)
        
        # Recursive call
        result = dfs_limited(grid, neighbor, g_cost + 1, threshold, path, goals, visited_this_iteration, total_visited)
        
        if result == "FOUND":
            return "FOUND"
        elif result != float('inf'):
            min_next_threshold = min(min_next_threshold, result)
        
        # Backtrack - remove from current path
        path.pop()
    
    return min_next_threshold

def ida_star_generator(grid):
    """
    Generator version for GUI visualization
    """
    start = grid.start_position
    goals = set(grid.goal_positions)
    
    # Initialize threshold
    threshold = heuristic_manhattan(start, goals)
    
    # Track overall visited nodes
    all_visited = set()
    
    # Initial state
    yield {
        'visited': set([start]),
        'frontier': [start],
        'current_bound': threshold
    }
    
    max_iterations = 1000
    iteration = 0
    
    while iteration < max_iterations:
        # Reset for this iteration
        path = [start]
        visited_this_iteration = set([start])
        
        # Generator version of DFS
        search_gen = dfs_limited_generator(grid, start, 0, threshold, path, goals, visited_this_iteration, all_visited)
        
        result = None
        min_next_threshold = float('inf')
        
        try:
            while True:
                state = next(search_gen)
                
                if 'result' in state:
                    result = state['result']
                    if result == "FOUND":
                        # Found solution
                        yield {
                            'visited': all_visited,
                            'frontier': [],
                            'path': path,
                            'current_bound': threshold
                        }
                        return
                    elif result != float('inf'):
                        min_next_threshold = min(min_next_threshold, result)
                else:
                    # Regular visualization state
                    yield {
                        'visited': all_visited,
                        'frontier': state.get('frontier', []),
                        'current_bound': threshold
                    }
        except StopIteration:
            pass
        
        if min_next_threshold == float('inf'):
            # No solution
            yield {
                'visited': all_visited,
                'frontier': [],
                'message': 'No solution found'
            }
            return
        
        # Update threshold
        old_threshold = threshold
        threshold = min_next_threshold
        
        yield {
            'visited': all_visited,
            'frontier': [],
            'message': f'Increasing threshold from {old_threshold} to {threshold}'
        }
        
        iteration += 1
    
    # Max iterations reached
    yield {
        'visited': all_visited,
        'frontier': [],
        'message': 'Maximum iterations reached'
    }

def dfs_limited_generator(grid, node, g_cost, threshold, path, goals, visited_this_iteration, all_visited):
    """
    Generator version of depth-limited DFS
    """
    # Calculate f = g + h
    h_cost = heuristic_manhattan(node, goals)
    f_cost = g_cost + h_cost
    
    # Add to visited
    all_visited.add(node)
    
    # Yield current state for visualization
    yield {
        'frontier': path.copy(),
        'visited': all_visited.copy()
    }
    
    # If f exceeds threshold, return f
    if f_cost > threshold:
        yield {'result': f_cost}
        return
    
    # Check if goal reached
    if node in goals:
        yield {'result': "FOUND"}
        return
    
    # Explore neighbors
    min_next_threshold = float('inf')
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    for dx, dy in directions:
        x, y = node
        neighbor = (x + dx, y + dy)
        
        # Skip invalid positions
        if (not grid.is_valid_position(neighbor) or 
            neighbor in path):
            continue
        
        # Add to path
        path.append(neighbor)
        visited_this_iteration.add(neighbor)
        
        # Recursive generator call
        neighbor_gen = dfs_limited_generator(grid, neighbor, g_cost + 1, threshold, path, goals, visited_this_iteration, all_visited)
        
        try:
            while True:
                state = next(neighbor_gen)
                if 'result' in state:
                    result = state['result']
                    if result == "FOUND":
                        yield {'result': "FOUND"}
                        return
                    elif result != float('inf'):
                        min_next_threshold = min(min_next_threshold, result)
                else:
                    yield state
        except StopIteration:
            pass
        
        # Backtrack
        path.pop()
    
    # Return minimum threshold found
    yield {'result': min_next_threshold}