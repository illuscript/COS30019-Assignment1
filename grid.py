class Grid:
    def __init__(self, filename):
        self.width = 0
        self.height = 0
        self.start_position = None
        self.goal_positions = []
        self.wall_positions = set()
        self.load_from_file(filename)

    def load_from_file(self, filename):
        with open(filename, 'r') as f:
            size_line = f.readline().strip()
            self.width, self.height = map(int, size_line.split('x'))

            self.start_position = tuple(map(int, f.readline().strip().split(',')))
            goals_line = f.readline().strip()
            self.goal_positions = [tuple(map(int, p.split(','))) for p in goals_line.split('; ')]

            for line in f:
                if line.strip():
                    wall = tuple(map(int, line.strip().split(',')))
                    self.wall_positions.add(wall)

    def is_valid_position(self, position):
        x, y = position
        return (0 <= x < self.width and
                0 <= y < self.height and
                position not in self.wall_positions)