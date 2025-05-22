def heuristic_manhattan(current, goals):
    min_distance = float('inf')
    for goal in goals:
        distance = abs(current[0] - goal[0]) + abs(current[1] - goal[1])
        if distance < min_distance:
            min_distance = distance
    return min_distance