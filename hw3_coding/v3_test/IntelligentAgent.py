# Name: Mesomachukwu Nwankwo
# UNI: mn3372

import math
import time
from BaseAI import BaseAI


class SearchTimeout(Exception):
    pass


class IntelligentAgent(BaseAI):
    TIME_LIMIT = 0.17

    def check_time(self):
        if time.process_time() >= self.deadline:
            raise SearchTimeout()

    @staticmethod
    def board_key(grid):
        return tuple(v for row in grid.map for v in row)

    def evaluate(self, grid):
        key = self.board_key(grid)
        cached = self.eval_cache.get(key)
        if cached is not None:
            return cached

        board = grid.map
        empty = sum(v == 0 for row in board for v in row)
        values = [[v.bit_length() - 1 if v else 0 for v in row] for row in board]
        smoothness = 0
        for i in range(4):
            for j in range(4):
                if not board[i][j]:
                    continue
                if j < 3 and board[i][j + 1]:
                    smoothness -= abs(values[i][j] - values[i][j + 1])
                if i < 3 and board[i + 1][j]:
                    smoothness -= abs(values[i][j] - values[i + 1][j])

        monotonicity = 0
        for row in values:
            increasing = sum(max(0, row[k + 1] - row[k]) for k in range(3))
            decreasing = sum(max(0, row[k] - row[k + 1]) for k in range(3))
            monotonicity -= min(increasing, decreasing)
        for j in range(4):
            col = [values[i][j] for i in range(4)]
            increasing = sum(max(0, col[k + 1] - col[k]) for k in range(3))
            decreasing = sum(max(0, col[k] - col[k + 1]) for k in range(3))
            monotonicity -= min(increasing, decreasing)

        max_tile = max(key)
        corners = (board[0][0], board[0][3], board[3][0], board[3][3])
        corner_score = (max_tile.bit_length() - 1) * 150 if max_tile in corners and max_tile else 0
        score = empty * 250 + smoothness * 20 + monotonicity * 100 + corner_score
        self.eval_cache[key] = score
        return score

    def maximize(self, grid, depth, beta=float('inf')):
        self.check_time()
        if depth <= 0:
            return self.evaluate(grid)
        moves = grid.getAvailableMoves()
        if not moves:
            return self.evaluate(grid)
        alpha = float('-inf')
        # No sorting here: heuristic sorting cost may outweigh pruning savings.
        for _, new_grid in moves:
            self.check_time()
            score = self.chance(new_grid, depth - 1)
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        return alpha

    def minimize(self, grid, tile, depth):
        self.check_time()
        cells = grid.getAvailableCells()
        if not cells:
            return self.maximize(grid, depth)
        beta = float('inf')
        for cell in cells:
            self.check_time()
            new_grid = grid.clone()
            new_grid.insertTile(cell, tile)
            beta = min(beta, self.maximize(new_grid, depth, beta))
        return beta

    def chance(self, grid, depth):
        self.check_time()
        score_2 = self.minimize(grid, 2, depth)
        score_4 = self.minimize(grid, 4, depth)
        return 0.9 * score_2 + 0.1 * score_4

    def search(self, grid, depth):
        moves = grid.getAvailableMoves()
        moves.sort(key=lambda item: self.evaluate(item[1]), reverse=True)
        best_move = moves[0][0]
        best_score = float('-inf')
        for move, new_grid in moves:
            self.check_time()
            score = self.chance(new_grid, depth - 1)
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def getMove(self, grid):
        self.deadline = time.process_time() + self.TIME_LIMIT
        self.eval_cache = {}
        moves = grid.getAvailableMoves()
        if not moves:
            return None
        best_move = moves[0][0]
        depth = 1
        while True:
            try:
                best_move = self.search(grid, depth)
                depth += 1
            except SearchTimeout:
                return best_move
