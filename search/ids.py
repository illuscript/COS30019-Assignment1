def ids(grid, as_generator=False):
    # If as_generator is False, run through the algorithm to completion
    if not as_generator:
        # Create a generator
        generator = _ids_generator(grid)
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
    return _ids_generator(grid)

def _ids_generator(grid):
    start = grid.start_position
    goals = set(grid.goal_positions)
    
    # Calculate a reasonable upper limit for max depth
    # Use Manhattan distance from start to the farthest goal as a heuristic
    max_depth = 0
    for goal in goals:
        manhattan_dist = abs(start[0] - goal[0]) + abs(start[1] - goal[1])
        max_depth = max(max_depth, manhattan_dist)
    
    # Add some buffer to account for walls/obstacles
    max_depth = max_depth * 2
    
    # Track overall visited nodes across all depth iterations
    all_visited = set()
    
    # Precalculate the directions once
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # RIGHT, DOWN, LEFT, UP
    
    # Try increasing depth limits
    for depth_limit in range(max_depth + 1):  # +1 to include max_depth
        # Reset visited set for this depth iteration
        visited = set()
        
        # For visualization purposes - use a list for frontier to make ordering consistent
        frontier = []
        frontier_set = set()  # For O(1) lookups
        
        # DLS - Depth Limited Search
        stack = [(start, 0)]  # (position, depth)
        frontier.append(start)
        frontier_set.add(start)
        
        # Track parents for path reconstruction
        parent = {start: None}
        
        # Make visualization more responsive
        yield_frequency = 5  # Reduced for more frequent updates
        
        found_solution = False
        
        while stack and not found_solution:
            current, depth = stack.pop()
            
            # Update frontier visualization
            if current in frontier_set:
                frontier_set.remove(current)
                # Finding the item in a list is O(n), but frontier should be fairly small
                if current in frontier:
                    frontier.remove(current)
            
            # Skip if already visited in this depth-limited search
            if current in visited:
                # Still yield periodically for visualization
                if len(visited) % yield_frequency == 0:
                    yield {'visited': all_visited, 'frontier': frontier}
                continue
                
            visited.add(current)
            all_visited.add(current)
            
            # If reached a goal, reconstruct path
            if current in goals:
                path = []
                while current:
                    path.append(current)
                    current = parent.get(current)
                path.reverse()
                
                yield {'visited': all_visited, 'frontier': frontier, 'path': path}
                found_solution = True
                break
            
            # Yield state more frequently for smoother visualization
            if len(visited) % yield_frequency == 0:
                yield {'visited': all_visited, 'frontier': frontier}
            
            # If at depth limit, don't explore further
            if depth >= depth_limit:
                continue
            
            # Get valid neighbors
            x, y = current
            neighbors = []
            
            for dx, dy in directions:
                neighbor = (x + dx, y + dy)
                if grid.is_valid_position(neighbor) and neighbor not in visited:
                    neighbors.append(neighbor)
            
            # For DFS-like behavior, add neighbors in reverse order
            for neighbor in reversed(neighbors):
                # Only add to stack if unvisited or would create a shorter path
                if neighbor not in parent or depth + 1 < get_depth(parent, neighbor):
                    parent[neighbor] = current
                    stack.append((neighbor, depth + 1))
                    
                    # Only add to frontier if not already there
                    if neighbor not in frontier_set:
                        frontier.append(neighbor)
                        frontier_set.add(neighbor)
        
        # Don't continue if solution found
        if found_solution:
            break
            
        # No solution found at this depth, try next depth
        # Yield current state before moving to next depth
        if not found_solution:
            yield {'visited': all_visited, 'frontier': frontier}
    
    # No path found within max depth
    if not found_solution:
        yield {'visited': all_visited, 'frontier': []}

def get_depth(parent_dict, node):
    depth = 0
    current = node
    while current in parent_dict and parent_dict[current] is not None:
        depth += 1
        current = parent_dict[current]
    return depth