import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from grid import Grid
import heapq
from search.bfs import bfs
from search.dfs import dfs
from search.gbfs import gbfs
from search.astar import astar
from search.ids import ids
from search.ida_star import ida_star

COLORS = {
    'start': 'red',
    'goal': 'green',
    'wall': 'grey',
    'empty': 'white',
    'frontier': 'orange',
    'visited': 'light blue',
    'path': 'yellow',
    'current_goal': 'dark green',  
    'completed_goal': 'lime green'  
}

class GridVisualizer:
    def __init__(self, grid=None):
        self.grid = grid
        self.cell_size = 40 
        self.delay = 200  # ms
        self.paused = True
        self.search_active = False
        self.search_gen = None
        
        # Multi-goal tracking
        self.current_goal_index = 0
        self.goal_results = []  # Store results for each goal
        self.original_start = None  # Store the original start position
        self.original_goals = []
        self.waiting_for_next_goal = False  # Flag to track if waiting for user to proceed
        
        self.root = tk.Tk()
        self.root.title("COS30019 - 104491705")
        self.root.geometry('1400x700')  # Bigger window
        
        # Create main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left frame for canvas
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Control Panel
        self.control_frame = tk.Frame(self.left_frame)
        self.control_frame.pack(pady=10, anchor='nw')

        # Load Map button
        self.load_btn = tk.Button(self.control_frame, text="Load Map", command=self.load_map)
        self.load_btn.pack(side=tk.LEFT, padx=5)

        # Algorithm selection via radio buttons
        self.method_var = tk.StringVar(value="bfs")
        methods = [("BFS", "bfs"), ("DFS", "dfs"), ("GBFS", "gbfs"), ("A*", "as"), ("IDS", "ids"), ("IDA*", "ida_star")]
        for text, mode in methods:
            rb = tk.Radiobutton(self.control_frame, text=text, variable=self.method_var, value=mode)
            rb.pack(side=tk.LEFT, padx=5)
        
        # Speed control
        self.speed_label = tk.Label(self.control_frame, text="Speed:")
        self.speed_label.pack(side=tk.LEFT, padx=5)
        self.speed_scale = ttk.Scale(self.control_frame, from_=1, to=500, orient=tk.HORIZONTAL, 
                                    length=100, value=self.delay,
                                    command=self.update_speed)
        self.speed_scale.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        self.start_btn = tk.Button(self.control_frame, text="Start", command=self.start_search, state=tk.DISABLED)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.pause_btn = tk.Button(self.control_frame, text="Pause", command=self.toggle_pause, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        self.restart_btn = tk.Button(self.control_frame, text="Restart", command=self.restart, state=tk.DISABLED)
        self.restart_btn.pack(side=tk.LEFT, padx=5)
        
        # Canvas
        self.canvas_frame = tk.Frame(self.left_frame)
        self.canvas_frame.pack(expand=True, fill=tk.BOTH)
        self.canvas = tk.Canvas(self.canvas_frame, bg='white')
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Bind resize event to update canvas
        self.canvas.bind('<Configure>', self.on_canvas_resize)

        # Info Panel
        self.info_frame = tk.Frame(self.left_frame)
        self.info_frame.pack(fill=tk.X, pady=5)
        self.info_label = tk.Label(self.info_frame, text="Nodes expanded: 0 | Frontier size: 0 | Goal: 0/0")
        self.info_label.pack(side=tk.LEFT, padx=10)

        # Right frame for results
        self.right_frame = tk.Frame(self.main_frame, width=300)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        self.right_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Results text area
        self.results_label = tk.Label(self.right_frame, text="Results:")
        self.results_label.pack(anchor='w', pady=(0, 5))
        self.results_text = scrolledtext.ScrolledText(self.right_frame, width=40, height=30)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        self.root.mainloop()

    def on_canvas_resize(self, event):
        if not self.grid:
            return
            
        # Get the current canvas dimensions
        canvas_width = event.width
        canvas_height = event.height
        
        # Calculate the maximum possible cell size to fit the grid in the canvas
        # Subtract some padding to account for borders
        max_cell_width = (canvas_width - 20) / self.grid.width
        max_cell_height = (canvas_height - 20) / self.grid.height
        
        # Use the smaller dimension to ensure cells remain square
        self.cell_size = min(max_cell_width, max_cell_height)
        
        # Redraw the grid with the new cell size
        self.initialize_grid()

    def update_speed(self, val):
        self.delay = int(float(val))

    def load_map(self):
        file_path = filedialog.askopenfilename(initialdir=".", title="Select map file", filetypes=(("Text files","*.txt"),))
        if not file_path:
            return
        
        try:
            self.grid = Grid(file_path)
            
            # Verify the grid has a valid start position and at least one goal
            if not hasattr(self.grid, 'start_position') or self.grid.start_position is None:
                raise ValueError("Invalid map: No start position found")
            
            if not hasattr(self.grid, 'goal_positions') or not self.grid.goal_positions:
                raise ValueError("Invalid map: No goal positions found")
                
            self.original_goals = self.grid.goal_positions.copy()
            self.original_start = self.grid.start_position  # Store the original start position
            
            # Get current canvas size and adjust cell size to fit
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Calculate the maximum possible cell size
            if canvas_width > 1 and canvas_height > 1:  # Ensure canvas has been drawn
                max_cell_width = (canvas_width - 20) / self.grid.width
                max_cell_height = (canvas_height - 20) / self.grid.height
                self.cell_size = min(max_cell_width, max_cell_height)
            
            self.initialize_grid()
            
            # Reset controls and state
            self.paused = True
            self.search_active = False
            self.search_gen = None
            self.current_goal_index = 0
            self.goal_results = []
            self.waiting_for_next_goal = False
            
            # Update UI
            self.start_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED, text="Pause")
            self.restart_btn.config(state=tk.DISABLED)
            self.update_info(0, 0)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Loaded map with {len(self.original_goals)} goal(s)\n")
            self.results_text.insert(tk.END, f"Start position: {self.original_start}\n")
            self.results_text.insert(tk.END, f"Goals: {', '.join(str(g) for g in self.original_goals)}\n\n")
            
        except Exception as e:
            # Show error message
            messagebox.showerror("Error Loading Map", f"Failed to load map file:\n{str(e)}")
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Error loading map: {str(e)}\n")
            
            # Disable buttons since we don't have a valid map
            self.start_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.DISABLED)
            self.restart_btn.config(state=tk.DISABLED)

    def initialize_grid(self):
        self.canvas.delete("all")
        self.cell_map = {}

        # Calculate grid dimensions 
        grid_width = self.grid.width * self.cell_size
        grid_height = self.grid.height * self.cell_size
        
        # Center the grid in the canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Calculate offsets to center the grid
        x_offset = max(0, (canvas_width - grid_width) / 2)
        y_offset = max(0, (canvas_height - grid_height) / 2)

        for y in range(self.grid.height):
            for x in range(self.grid.width):
                color = COLORS['empty']
                if (x, y) == self.grid.start_position:
                    color = COLORS['start']
                elif (x, y) in self.grid.goal_positions:
                    color = COLORS['goal']
                elif (x, y) in self.grid.wall_positions:
                    color = COLORS['wall']
                rect = self.canvas.create_rectangle(
                    x_offset + x*self.cell_size, y_offset + y*self.cell_size,
                    x_offset + (x+1)*self.cell_size, y_offset + (y+1)*self.cell_size,
                    fill=color, outline='black', tags=f"cell_{x}_{y}"
                )
                self.cell_map[(x, y)] = rect

    def update_cell(self, x, y, color):
        # Don't update walls
        if (x, y) in self.grid.wall_positions:
            return
        # Special case for goals - only update if not the current goal or completed goal
        if (x, y) in self.original_goals:
            goal_idx = self.original_goals.index((x, y))
            if goal_idx == self.current_goal_index:
                color = COLORS['current_goal']
            elif goal_idx < self.current_goal_index:
                color = COLORS['completed_goal']
            else:
                color = COLORS['goal']
        # Special case for start position
        elif (x, y) == self.original_start:
            color = COLORS['start']
        # Otherwise update normally
        self.canvas.itemconfig(self.cell_map[(x, y)], fill=color)

    def update_info(self, nodes, frontier_size):
        total_goals = len(self.original_goals) if self.original_goals else 0
        self.info_label.config(text=f"Nodes expanded: {nodes} | Frontier size: {frontier_size} | " + 
                              f"Goal: {self.current_goal_index + 1}/{total_goals}")

    def path_to_moves(self, path):
        """Convert a path of coordinates to a sequence of moves."""
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

    def start_search(self):
        if not self.grid:
            messagebox.showerror("Error", "No map loaded!")
            return
        
        if self.waiting_for_next_goal:
            # Setup next goal and reset grid
            self.grid.goal_positions = [self.original_goals[self.current_goal_index]]
            self.grid.start_position = self.original_start
            self.refresh_grid_display()
            self.waiting_for_next_goal = False
        else:
            # Starting a new search from the beginning
            self.current_goal_index = 0
            self.goal_results = []
            self.grid.start_position = self.original_start
            if len(self.original_goals) > 0:
                self.grid.goal_positions = [self.original_goals[0]]
                self.refresh_grid_display()
            else:
                messagebox.showinfo("Info", "No goals to attempt!")
                return
        
        # Begin search
        self.paused = False
        self.search_active = True
        self.search_gen = None
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.restart_btn.config(state=tk.NORMAL)
        self.run_search()

    def setup_next_goal(self):
        """Prepare grid for next goal"""
        if self.current_goal_index < len(self.original_goals):
            # Set current goal as the only active goal
            self.grid.goal_positions = [self.original_goals[self.current_goal_index]]
            # Always use the original start position
            self.grid.start_position = self.original_start
            # Update grid visualization (highlight current goal)
            self.refresh_grid_display()
            return True
        return False

    def refresh_grid_display(self):
        """Refresh the grid to update goal and start indicators"""
        for (x, y), rect in self.cell_map.items():
            if (x, y) in self.grid.wall_positions:
                continue
            
            if (x, y) == self.original_start:
                color = COLORS['start']
            elif (x, y) in self.original_goals:
                goal_idx = self.original_goals.index((x, y))
                if goal_idx == self.current_goal_index:
                    color = COLORS['current_goal']
                elif goal_idx < self.current_goal_index:
                    color = COLORS['completed_goal']
                else:
                    color = COLORS['goal']
            else:
                color = COLORS['empty']
                
            self.canvas.itemconfig(self.cell_map[(x, y)], fill=color)

    def toggle_pause(self):
        if not self.search_active:
            return
        self.paused = not self.paused
        self.pause_btn.config(text="Resume" if self.paused else "Pause")
        if not self.paused:
            self.run_search()

    def restart(self):
        # Reset everything
        self.paused = True
        self.search_active = False
        self.search_gen = None
        self.current_goal_index = 0
        self.goal_results = []
        self.waiting_for_next_goal = False
        
        # Restore original state
        self.grid.start_position = self.original_start
        self.grid.goal_positions = self.original_goals
        
        # Update UI
        self.initialize_grid()
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text="Pause")
        self.restart_btn.config(state=tk.DISABLED)
        self.update_info(0, 0)
        
        # Clear results
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Loaded map with {len(self.original_goals)} goal(s)\n")
        self.results_text.insert(tk.END, f"Start position: {self.original_start}\n")
        self.results_text.insert(tk.END, f"Goals: {', '.join(str(g) for g in self.original_goals)}\n\n")

    def run_search(self):
        if self.paused or not self.search_active:
            return
            
        if self.search_gen is None:
            method = self.method_var.get()
            try:
                if method == "bfs":
                    self.search_gen = bfs(self.grid, as_generator=True)
                elif method == "dfs":
                    self.search_gen = dfs(self.grid, as_generator=True)
                elif method == "gbfs":
                    self.search_gen = gbfs(self.grid, as_generator=True)
                elif method == "as":
                    self.search_gen = astar(self.grid, as_generator=True)
                elif method == "ids":
                    self.search_gen = ids(self.grid, as_generator=True)
                elif method == "ida_star":
                    self.search_gen = ida_star(self.grid, as_generator=True)
            except Exception as e:
                messagebox.showerror("Error", f"Error starting search: {str(e)}")
                self.search_active = False
                self.start_btn.config(state=tk.NORMAL)
                self.pause_btn.config(state=tk.DISABLED)
                return
                
        try:
            state = next(self.search_gen)
            self.update_visualization(state)
            nodes = len(state.get('visited', []))
            frontier_size = len(state.get('frontier', []))
            self.update_info(nodes, frontier_size)
            
            # Check if we have a path (solution found)
            if 'path' in state:
                self.process_completed_search(state)
            else:
                self.root.after(self.delay, self.run_search)
                
        except StopIteration:
            method = self.method_var.get().upper()
            self.results_text.insert(tk.END, f"Goal {self.current_goal_index + 1}: {self.original_goals[self.current_goal_index]}\n")
            self.results_text.insert(tk.END, f"Method: {method}\n")
            self.results_text.insert(tk.END, "No solution found.\n\n")
            
            self.current_goal_index += 1
            self.search_gen = None
            
            if self.current_goal_index < len(self.original_goals):
                self.waiting_for_next_goal = True
                self.search_active = False
                self.results_text.insert(tk.END, "No solution found. Press Start to continue to next goal.\n")
                self.start_btn.config(state=tk.NORMAL)
                self.pause_btn.config(state=tk.DISABLED)
            else:
                self.search_active = False
                self.results_text.insert(tk.END, "All goals attempted!\n")
                self.pause_btn.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Error during search: {str(e)}")
            self.search_active = False
            self.start_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED)
            
    def process_completed_search(self, final_state):
        """Process the results of a completed search for the current goal"""
        method = self.method_var.get().upper()
        if "path" in final_state:
            path = final_state["path"]
            nodes_expanded = len(final_state.get('visited', []))
            moves = self.path_to_moves(path)
            
            # Add result to our tracking
            result = {
                "goal_index": self.current_goal_index,
                "goal": self.original_goals[self.current_goal_index],
                "path": path,
                "nodes_expanded": nodes_expanded,
                "moves": moves
            }
            self.goal_results.append(result)
            
            # Update results display
            self.results_text.insert(tk.END, f"Goal {self.current_goal_index + 1}: {self.original_goals[self.current_goal_index]}\n")
            self.results_text.insert(tk.END, f"Method: {method}\n")
            self.results_text.insert(tk.END, f"Nodes expanded: {nodes_expanded}\n")
            self.results_text.insert(tk.END, f"Path length: {len(path)}\n")
            self.results_text.insert(tk.END, f"Moves: {'; '.join(moves)}\n\n")
            
            self.current_goal_index += 1
            self.search_gen = None
            
            if self.current_goal_index < len(self.original_goals):
                self.waiting_for_next_goal = True
                self.search_active = False
                self.results_text.insert(tk.END, "Goal reached! Press Start to continue to next goal.\n")
                self.start_btn.config(state=tk.NORMAL)
                self.pause_btn.config(state=tk.DISABLED)
            else:
                self.search_active = False
                self.results_text.insert(tk.END, "All goals reached!\n")
                self.pause_btn.config(state=tk.DISABLED)
        else:
            self.results_text.insert(tk.END, f"Goal {self.current_goal_index + 1}: {self.original_goals[self.current_goal_index]}\n")
            self.results_text.insert(tk.END, f"Method: {method}\n")
            self.results_text.insert(tk.END, "No solution found.\n\n")
            
            self.current_goal_index += 1
            self.search_gen = None
            
            if self.current_goal_index < len(self.original_goals):
                self.waiting_for_next_goal = True
                self.search_active = False
                self.results_text.insert(tk.END, "No solution found. Press Start to continue to next goal.\n")
                self.start_btn.config(state=tk.NORMAL)
                self.pause_btn.config(state=tk.DISABLED)
            else:
                self.search_active = False
                self.results_text.insert(tk.END, "All goals attempted!\n")
                self.pause_btn.config(state=tk.DISABLED)

    def update_visualization(self, state):
        # Reset non-essential cells
        for (x, y), rect in self.cell_map.items():
            if (x, y) not in [self.original_start] + self.original_goals + list(self.grid.wall_positions):
                self.canvas.itemconfig(rect, fill=COLORS['empty'])

        # Update visited nodes
        for (x, y) in state.get('visited', []):
            self.update_cell(x, y, COLORS['visited'])
        # Update frontier nodes
        for (x, y) in state.get('frontier', []):
            self.update_cell(x, y, COLORS['frontier'])
        # Update current path
        if 'path' in state:
            for (x, y) in state['path']:
                self.update_cell(x, y, COLORS['path'])

if __name__ == "__main__":
    GridVisualizer()