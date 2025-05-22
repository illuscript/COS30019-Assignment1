def dfs(grid, as_generator=False):
    """
    Depth-First Search algorithm for grid navigation.
    
    Args:
        grid: Grid object with navigation information
        as_generator: If True, yields state at each step for visualization
        
    Returns:
        If as_generator is False: (path, nodes_explored) tuple
        If as_generator is True: Generator yielding state dictionaries
    """
    # If as_generator is False, we need to run through the algorithm to completion and return the final result
    if not as_generator:
        # Create a generator
        generator = _dfs_generator(grid)
        # Run it to completion
        final_state = None
        for state in generator:
            final_state = state
        
        # Check if a path was found
        if final_state and 'path' in final_state:
            return final_state['path'], len(final_state['visited'])
        else:
            return [], len(final_state['visited']) if final_state else 0
    
    # If as_generator is True, return the generator directly
    return _dfs_generator(grid)

def _dfs_generator(grid):
    """
    Helper function that implements the DFS algorithm and yields states.
    
    Yields:
        Dictionary containing current state information:
        - 'visited': Set of visited positions
        - 'frontier': List of positions to explore next
        - 'path': List of positions from start to goal (only in final state)
    """
    start = grid.start_position
    goals = set(grid.goal_positions)
    visited = set()
    frontier = [start]  # Using list as stack
    
    # Track parents for path reconstruction
    parent = {start: None}
    
    # Handle empty grid case
    if not frontier:
        yield {'visited': visited, 'frontier': frontier}
        return
    
    while frontier:
        current = frontier.pop()  # DFS pops from the end (LIFO)
        
        # Skip if already visited
        if current in visited:
            continue
            
        visited.add(current)
        
        # If reached a goal, reconstruct path
        if current in goals:
            path = []
            while current:
                path.append(current)
                current = parent.get(current)
            path.reverse()
            
            yield {'visited': visited, 'frontier': frontier, 'path': path}
            return
        
        # Get neighbors in exploration preference order
        x, y = current
        neighbors = []
        # Define directions - we need to consider the actual visual grid orientation
        # The order here depends on how your grid is structured
        # Based on your visualization, this might need adjustment
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # RIGHT, DOWN, LEFT, UP
        
        for dx, dy in directions:
            neighbor = (x + dx, y + dy)
            if grid.is_valid_position(neighbor) and neighbor not in visited:
                neighbors.append(neighbor)
        
        # For DFS, we need to understand how the frontier.pop() and push order interaction works:
        # Last item pushed is first to be explored (LIFO - stack behavior)
        # To achieve RIGHT, DOWN, LEFT, UP exploration order, we need to push in UP, LEFT, DOWN, RIGHT order
        # This way when popping from stack, RIGHT comes out first, then DOWN, etc.
        reversed_neighbors = neighbors[::-1]  # Reverse to get UP, LEFT, DOWN, RIGHT
        for neighbor in reversed_neighbors:
            if neighbor not in parent:
                parent[neighbor] = current
                frontier.append(neighbor)
        
        yield {'visited': visited, 'frontier': frontier}
    
    # No path found
    yield {'visited': visited, 'frontier': frontier}