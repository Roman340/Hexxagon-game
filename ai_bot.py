# ai_bot.py
import random

def get_axial_distance(q1, r1, q2, r2):
    return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) // 2

class HexAIBot:
    def __init__(self, difficulty="Средний"):
        self.difficulty = difficulty

    def calculate_best_move(self, cells):
        all_possible_moves = []

        for from_coords, from_cell in cells.items():
            if from_cell["player"] == 2:
                for to_coords, to_cell in cells.items():
                    if to_cell["player"] == 0:
                        dist = get_axial_distance(from_coords[0], from_coords[1], to_coords[0], to_coords[1])
                        if dist <= 2:
                            captured_count = 0
                            for neighbor_coords, neighbor_cell in cells.items():
                                if neighbor_cell["player"] == 1:
                                    if get_axial_distance(to_coords[0], to_coords[1], neighbor_coords[0], neighbor_coords[1]) == 1:
                                        captured_count += 1
                            
                            move_value = captured_count + (1 if dist == 1 else 0)
                            all_possible_moves.append((move_value, from_coords, to_coords))

        if not all_possible_moves:
            return None

        if self.difficulty == "Легкий":
            _, b_from, b_to = random.choice(all_possible_moves)
            return b_from, b_to
        elif self.difficulty == "Сложный":
            all_possible_moves.sort(key=lambda x: x[0], reverse=True)
            _, b_from, b_to = all_possible_moves[0]
            return b_from, b_to
        else:
            best_score = -999
            best_move = None
            for val, f_c, t_c in all_possible_moves:
                if val > best_score:
                    best_score = val
                    best_move = (f_c, t_c)
            return best_move