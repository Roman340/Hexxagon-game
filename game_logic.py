# game_logic.py
import json
import os

def axial_distance(q1, r1, q2, r2):
    return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) // 2

class HexGameEngine:
    def __init__(self, board_size=4):
        self.board_size = board_size
        self.current_player = 1  
        self.mode = "PvP"        
        self.difficulty = "Средний"
        self.cells_data = {}     

    def reset_board(self):
        self.cells_data.clear()
        self.current_player = 1
        
        for q in range(-self.board_size, self.board_size + 1):
            r1 = max(-self.board_size, -q - self.board_size)
            r2 = min(self.board_size, -q + self.board_size)
            for r in range(r1, r2 + 1):
                if axial_distance(0, 0, q, r) <= self.board_size:
                    self.cells_data[(q, r)] = {"player": 0}

        size = self.board_size
        if (-size, 0) in self.cells_data: self.cells_data[(-size, 0)]["player"] = 1
        if (0, size) in self.cells_data: self.cells_data[(0, size)]["player"] = 1
        if (size, -size) in self.cells_data: self.cells_data[(size, -size)]["player"] = 1
        
        if (size, 0) in self.cells_data: self.cells_data[(size, 0)]["player"] = 2
        if (0, -size) in self.cells_data: self.cells_data[(0, -size)]["player"] = 2
        if (-size, size) in self.cells_data: self.cells_data[(-size, size)]["player"] = 2

    def move_piece(self, from_q, from_r, to_q, to_r):
        dist = axial_distance(from_q, from_r, to_q, to_r)
        player = self.cells_data[(from_q, from_r)]["player"]

        if dist == 1:
            self.cells_data[(to_q, to_r)]["player"] = player
        elif dist == 2:
            self.cells_data[(to_q, to_r)]["player"] = player
            self.cells_data[(from_q, from_r)]["player"] = 0

        enemy = 2 if player == 1 else 1
        for coords, cell in self.cells_data.items():
            if cell["player"] == enemy:
                if axial_distance(to_q, to_r, coords[0], coords[1]) == 1:
                    self.cells_data[coords]["player"] = player

    def get_scores(self):
        p1 = sum(1 for c in self.cells_data.values() if c["player"] == 1)
        p2 = sum(1 for c in self.cells_data.values() if c["player"] == 2)
        return p1, p2

    def has_valid_moves(self, player_id):
        for f_coords, f_cell in self.cells_data.items():
            if f_cell["player"] == player_id:
                for t_coords, t_cell in self.cells_data.items():
                    if t_cell["player"] == 0:
                        if axial_distance(f_coords[0], f_coords[1], t_coords[0], t_coords[1]) <= 2:
                            return True
        return False

    def save_to_json(self, filename="savegame.json"):
        data = {
            "current_player": self.current_player,
            "mode": self.mode,
            "difficulty": self.difficulty,
            "cells": [{"q": k[0], "r": k[1], "player": v["player"]} for k, v in self.cells_data.items()]
        }
        with open(filename, "w") as f:
            json.dump(data, f)

    def load_from_json(self, filename="savegame.json"):
        if not os.path.exists(filename):
            return False
        with open(filename, "r") as f:
            data = json.load(f)
        self.current_player = data["current_player"]
        self.mode = data["mode"]
        self.difficulty = data["difficulty"]
        for item in data["cells"]:
            self.cells_data[(item["q"], item["r"])] = {"player": item["player"]}
        return True