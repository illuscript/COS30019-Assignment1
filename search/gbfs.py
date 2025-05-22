import heapq
from .heuristic_manhattan import heuristic_manhattan

def gbfs(grid, as_generator=False):
    if not as_generator:
        # Create a generator
        generator = _gbfs_generator(grid)
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
    return _gbfs_generator(grid)

def _gbfs_generator(grid):
    # If no goals, return empty path
    if not grid.goal_positions:
        yield {'visited': set(), 'frontier': []}
        return
    
    start = grid.start_position
    goals = grid.goal_positions
    visited = set()
    
    # Priority queue elements: (heuristic, sequence_number, position)
    heap = []
    frontier = []  # For visualization purposes
    
    # Track parents for path reconstruction
    parent = {start: None}
    seq = 0  # Sequence number for consistent tie-breaking
    
    # Initialize with start position
    initial_h = heuristic_manhattan(start, goals)
    heapq.heappush(heap, (initial_h, seq, start))
    frontier.append(start)
    seq += 1
    
    while heap:
        h, s, current = heapq.heappop(heap)
        frontier.remove(current)
        
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
        
        # Process neighbors in RIGHT, DOWN, LEFT, UP order
        x, y = current
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # RIGHT, DOWN, LEFT, UP
        
        for i, (dx, dy) in enumerate(directions):
            neighbor = (x + dx, y + dy)
            if grid.is_valid_position(neighbor) and neighbor not in visited:
                if neighbor not in parent:
                    parent[neighbor] = current
                    new_h = heuristic_manhattan(neighbor, goals)
                    direction_pref = i * 0.1  # Small preference based on direction
                    heapq.heappush(heap, (new_h, seq + direction_pref, neighbor))
                    frontier.append(neighbor)
        
        seq += 1  # Increment sequence after all neighbors are processed
        
        yield {'visited': visited, 'frontier': frontier}
    
    # No path found
    yield {'visited': visited, 'frontier': frontier}