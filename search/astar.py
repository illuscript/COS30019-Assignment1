import heapq
from .heuristic_manhattan import heuristic_manhattan

def astar(grid, as_generator=False):
    # If as_generator is False, run through the algorithm to completion
    if not as_generator:
        # Create a generator
        generator = _astar_generator(grid)
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
    return _astar_generator(grid)

def _astar_generator(grid):
    start = grid.start_position
    goals = grid.goal_positions
    
    # When multiple goals exist, focus on the current target goal
    # In main.py, we're already processing one goal at a time
    current_goal = goals[0] if goals else None
    if not current_goal:
        yield {'visited': set(), 'frontier': []}
        return
    
    visited = set()
    
    # Priority queue for frontier: (f_score, tie_breaker, position)
    # The tie_breaker is now: (h_score, sequence_number)
    # This creates a more consistent ordering when f_scores are equal
    heap = []
    
    # For visualization purposes
    frontier_nodes = set()  # Changed from list to set for O(1) containment checks
    
    # Track parents for path reconstruction and g_scores
    parent = {start: None}
    g_score = {start: 0}
    seq = 0  # Sequence number for tie-breaking
    
    # Initialize with start position
    # Calculate heuristic directly to the current target goal
    h_score = heuristic_manhattan(start, [current_goal])
    f_score = h_score  # g_score is 0 for start
    heapq.heappush(heap, (f_score, (h_score, seq), start))
    frontier_nodes.add(start)
    seq += 1
    
    # Precompute directions
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # RIGHT, DOWN, LEFT, UP
    
    while heap:
        # Get the most promising node
        f, (h, _), current = heapq.heappop(heap)
        frontier_nodes.discard(current)
        
        # Skip if already visited
        if current in visited:
            continue
            
        visited.add(current)
        
        # If reached the current goal, reconstruct path
        if current == current_goal:
            path = []
            while current:
                path.append(current)
                current = parent.get(current)
            path.reverse()
            
            # Convert to list for visualization
            frontier = list(frontier_nodes)
            yield {'visited': visited, 'frontier': frontier, 'path': path}
            return
        
        # Process neighbors
        x, y = current
        current_g = g_score[current]
        
        for i, (dx, dy) in enumerate(directions):
            neighbor = (x + dx, y + dy)
            
            # Skip invalid positions
            if not grid.is_valid_position(neighbor):
                continue
                
            # Calculate new g score (uniform cost of 1 per step)
            tentative_g = current_g + 1
            
            # Only process if this path is better than any previously found
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                # Update tracking information
                parent[neighbor] = current
                g_score[neighbor] = tentative_g
                
                # Calculate scores directly to the current target goal
                new_h = heuristic_manhattan(neighbor, [current_goal])
                new_f = tentative_g + new_h
                
                # Improved tie-breaking:
                # Uses the h-score as primary tie-breaker (prefer nodes closer to goal)
                # Uses sequence number as secondary tie-breaker (breadth-first ordering)
                heapq.heappush(heap, (new_f, (new_h, seq), neighbor))
                frontier_nodes.add(neighbor)
                seq += 1  # Increment sequence for each node
        
        # Yield current state for visualization
        frontier = list(frontier_nodes)  # Convert set to list for visualization
        yield {'visited': visited, 'frontier': frontier}
    
    # No path found
    frontier = list(frontier_nodes)
    yield {'visited': visited, 'frontier': frontier}