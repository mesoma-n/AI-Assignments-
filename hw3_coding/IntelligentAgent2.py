# Name: Mesomachukwu Nwankwo
# UNI: mn3372

import time
import math
from BaseAI import BaseAI


class SearchTimeout(Exception):
    pass


class IntelligentAgent(BaseAI):
    TIME_LIMIT = 0.17

    def check_time(self):
        if time.process_time() >= self.deadline:
            raise SearchTimeout()

    def evaluate(self, grid):
        board = grid.map
        empty = len(grid.getAvailableCells())
        values = [
            [math.log2(v) if v > 0 else 0 for v in row]
            for row in board
        ]

        empty_score = empty * 250
        smoothness = 0
        for i in range(4):
            for j in range(4):
                if board[i][j] == 0:
                    continue
                if j < 3 and board[i][j + 1] != 0:
                    smoothness -= abs(values[i][j] - values[i][j + 1])
                if i < 3 and board[i + 1][j] != 0:
                    smoothness -= abs(values[i][j] - values[i + 1][j])

        monotonicity = 0
        for row in values:
            increasing = sum(max(0, row[i + 1] - row[i]) for i in range(3))
            decreasing = sum(max(0, row[i] - row[i + 1]) for i in range(3))
            monotonicity -= min(increasing, decreasing)

        for j in range(4):
            col = [values[i][j] for i in range(4)]
            increasing = sum(max(0, col[i + 1] - col[i]) for i in range(3))
            decreasing = sum(max(0, col[i] - col[i + 1]) for i in range(3))
            monotonicity -= min(increasing, decreasing)

        max_tile = max(max(row) for row in board)
        corners = [board[0][0], board[0][3], board[3][0], board[3][3]]
        corner_score = (
            math.log2(max_tile) * 150
            if max_tile > 0 and max_tile in corners
            else 0
        )

        return (
            empty_score
            + smoothness * 20
            + monotonicity * 100
            + corner_score
        )

    def maximize(self, grid, depth, beta=float('inf')):
        self.check_time()
        if depth == 0:
            return self.evaluate(grid)

        moves = grid.getAvailableMoves()
        if not moves:
            return self.evaluate(grid)

        # Version 2: order moves at every MAX node, not only at the root.
        moves.sort(key=lambda item: self.evaluate(item[1]), reverse=True)
        alpha = float('-inf')
        for move, new_grid in moves:
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
            score = self.maximize(new_grid, depth, beta)
            beta = min(beta, score)
        return beta

    def chance(self, grid, depth):
        self.check_time()
        score_2 = self.minimize(grid, 2, depth)
        score_4 = self.minimize(grid, 4, depth)
        return 0.9 * score_2 + 0.1 * score_4

    def search(self, grid, depth):
        moves = grid.getAvailableMoves()
        best_move = moves[0][0]
        best_score = float('-inf')
        moves.sort(key=lambda item: self.evaluate(item[1]), reverse=True)

        for move, new_grid in moves:
            self.check_time()
            score = self.chance(new_grid, depth - 1)
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def getMove(self, grid):
        # Include initial move generation in the CPU-time budget.
        self.deadline = time.process_time() + self.TIME_LIMIT
        moves = grid.getAvailableMoves()
        if not moves:
            return None

        best_move = moves[0][0]