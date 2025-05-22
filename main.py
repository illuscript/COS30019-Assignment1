import sys
import os
from grid import Grid
from search.bfs import bfs
from search.dfs import dfs
from search.gbfs import gbfs
from search.astar import astar
from search.ids import ids
from search.ida_star import ida_star

def path_to_moves(path):
    moves = []
    for i in range(1, len(path)):
        prev = path[i-1]
        curr = path[i]
        dx = curr[0] - prev[0]
        dy = curr[1] - prev[1]
        if dx == 1:
            moves.append('right')
        elif dx == -1:
            moves.append('left')
        elif dy == 1:
            moves.append('down')
        elif dy == -1:
            moves.append('up')
    return moves

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 main.py <input_file> <method>")
        sys.exit(1)

    filename = sys.argv[1]
    method = sys.argv[2].lower()

    # Determine the correct file path
    file_path = None
    if os.path.isfile(filename):
        file_path = filename
    else:
        map_path = os.path.join('map', filename)
        if os.path.isfile(map_path):
            file_path = map_path
        else:
            print(f"Error: File '{filename}' not found in current directory or 'map/' directory.")
            sys.exit(1)

    # Load the grid with the resolved file path
    grid = Grid(file_path)
    original_goals = grid.goal_positions.copy()

    # Process each goal sequentially
    for idx, goal in enumerate(original_goals):
        grid.goal_positions = [goal]
        
        path = []
        num_nodes = 0
        
        try:
            if method == "bfs":
                result = bfs(grid, as_generator=False)
                if result:
                    if isinstance(result, tuple) and len(result) == 2:
                        path, num_nodes = result
                    else:
                        print(f"Warning: bfs returned unexpected format: {result}")
            elif method == "dfs":
                result = dfs(grid, as_generator=False)
                if result:
                    if isinstance(result, tuple) and len(result) == 2:
                        path, num_nodes = result
                    else:
                        print(f"Warning: dfs returned unexpected format: {result}")
            elif method == "gbfs":
                result = gbfs(grid, as_generator=False)
                if result:
                    if isinstance(result, tuple) and len(result) == 2:
                        path, num_nodes = result
                    else:
                        print(f"Warning: gbfs returned unexpected format: {result}")
            elif method == "as":
                result = astar(grid, as_generator=False)
                if result:
                    if isinstance(result, tuple) and len(result) == 2:
                        path, num_nodes = result
                    else:
                        print(f"Warning: astar returned unexpected format: {result}")
            elif method == "ids":
                result = ids(grid, as_generator=False)
                if result:
                    if isinstance(result, tuple) and len(result) == 2:
                        path, num_nodes = result
                    else:
                        print(f"Warning: ids returned unexpected format: {result}")
            elif method == "ida_star":
                result = ida_star(grid, as_generator=False)
                if result:
                    if isinstance(result, tuple) and len(result) == 2:
                        path, num_nodes = result
                    else:
                        print(f"Warning: ida_star returned unexpected format: {result}")
            else:
                print("Unknown method. Please use: bfs, dfs, gbfs, as, ids, or ida_star")
                sys.exit(1)
        except Exception as e:
            print(f"Error running {method}: {str(e)}")
            path = []
            num_nodes = 0

        print(f"{filename} {method.upper()} [Goal {idx+1}]")
        print(f"Start at {grid.start_position}")
        print(f"Goal at {goal}")
        print(f"{num_nodes} nodes expanded")
        
        if path:
            # Calculate and display path length (number of moves)
            path_length = len(path) - 1  # Subtract 1 because the path includes the start position
            print(f"Path length: {path_length}")
            
            moves = path_to_moves(path)
            print("; ".join(moves))
        else:
            print("No solution found.")
        print("-----------------------")

    grid.goal_positions = original_goals

if __name__ == "__main__":
    main()