from collections import deque

def bfs(grid, as_generator=False):
    if not as_generator:
        # Create a generator
        generator = _bfs_generator(grid)
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
    return _bfs_generator(grid)

def _bfs_generator(grid):
    # Helper function that implements the BFS algorithm and yields states
    start = grid.start_position
    goals = set(grid.goal_positions)
    visited = set()
    frontier = deque([start])
    
    # Track parents for path reconstruction
    parent = {start: None}
    
    while frontier:
        current = frontier.popleft()
        
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
            
            yield {'visited': visited, 'frontier': list(frontier), 'path': path}
            return
        
        # Process neighbors in RIGHT, DOWN, LEFT, UP order
        x, y = current
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:  # RIGHT, DOWN, LEFT, UP
            neighbor = (x + dx, y + dy)
            if grid.is_valid_position(neighbor) and neighbor not in visited and neighbor not in frontier:
                parent[neighbor] = current
                frontier.append(neighbor)
        
        yield {'visited': visited, 'frontier': list(frontier)}
    
    # No path found
    yield {'visited': visited, 'frontier': list(frontier)}