"""
Solver for the Queens game using backtracking algorithm.

This module implements the backtracking algorithm to solve the Queens puzzle
with colored regions and modified movement rules.
"""

import logging
import time
import logging
from typing import List, Tuple, Optional, Dict
from .board import Board
from .queen import Queen

logger = logging.getLogger('queens_solver')


class QueensSolver:
    """
    Solver for the Queens game using backtracking.

    Places one queen per colored region following the game rules:
    - No shared rows or columns
    - No adjacent diagonal positions
    - One queen per colored region
    """

    def __init__(self, board: Board):
        """
        Initialize the solver with a board.

        Args:
            board: Board instance with region mapping
        """
        self.board = board
        self.solution: Optional[List[Queen]] = None
        self.attempts = 0
        self.backtracks = 0
        self.start_time = 0

    def solve(self) -> bool:
        """
        Solve the Queens puzzle using backtracking.

        Returns:
            True if solution found, False otherwise
        """
        logger.info("Starting Queens puzzle solving")
        self.start_time = time.time()
        self.attempts = 0
        self.backtracks = 0

        # Clear any existing queens
        self.board.clear()

        # Try to place queens one region at a time
        if self._backtrack(0):
            self.solution = self.board.get_queens()
            elapsed = time.time() - self.start_time

            # Log the final solution board
            solution_board = self._create_solution_visualization()
            logger.info(".2f")
            logger.info("Final solution board:")
            for line in solution_board:
                logger.info(line)
            return True
        else:
            elapsed = time.time() - self.start_time
            logger.warning(".2f")
            return False

    def _backtrack(self, region_index: int) -> bool:
        """
        Recursive backtracking function.

        Args:
            region_index: Current region to place a queen in (0 to board_size-1)

        Returns:
            True if solution found from this state, False otherwise
        """
        # Base case: all regions have queens
        if region_index >= self.board.size:
            return True

        current_region = region_index

        # Get all valid positions for this region
        region_positions = self._get_region_positions(current_region)

        logger.debug(f"Trying region {current_region} ({Board.get_region_name(current_region)}) "
                    f"with {len(region_positions)} possible positions")

        # Try each possible position in this region
        for row, col in region_positions:
            self.attempts += 1

            queen = Queen(row, col, current_region)

            if self.board.is_valid_placement(queen):
                logger.debug(f"Placing queen at ({row}, {col}) in region {current_region}")

                # Place the queen
                if self.board.place_queen(queen):
                    # Recurse to next region
                    if self._backtrack(region_index + 1):
                        return True

                    # Backtrack: remove the queen
                    self.board.remove_queen(queen)
                    self.backtracks += 1
                    logger.debug(f"Backtracking from ({row}, {col}) in region {current_region}")

        logger.debug(f"No valid position found for region {current_region}")
        return False

    def _get_region_positions(self, region_id: int) -> List[Tuple[int, int]]:
        """
        Get all board positions that belong to a specific region.

        Args:
            region_id: Region ID (0 to board_size-1)

        Returns:
            List of (row, col) tuples for the region
        """
        positions = []
        for row in range(self.board.size):
            for col in range(self.board.size):
                if self.board.get_region_at(row, col) == region_id:
                    positions.append((row, col))
        return positions

    def _create_solution_visualization(self) -> List[str]:
        """
        Create a visual representation of the final solution board.

        Returns:
            List of strings representing the solved board
        """
        if not self.solution:
            return ["(no solution)"]

        # Create a board_size x board_size grid
        board_size = self.board.size
        grid = [['.' for _ in range(board_size)] for _ in range(board_size)]

        # Place queens on the grid
        for queen in self.solution:
            row, col = queen.row, queen.col
            grid[row][col] = 'Q'

        # Also show region information for each queen
        queen_info = []
        for queen in self.solution:
            region_name = Board.get_region_name(queen.region_id)
            queen_info.append(f"Q({queen.row},{queen.col})={region_name}")

        visualization = []

        # Add header
        header = f"    {' '.join(f'{i:2d}' for i in range(board_size))}"
        visualization.append(header)
        visualization.append(f"   {'-' * (board_size * 3)}")

        # Add each row
        for row_idx, row in enumerate(grid):
            row_str = f"{row_idx:2d} |"
            for cell in row:
                row_str += f" {cell} "
            visualization.append(row_str)

        # Add legend and queen positions
        visualization.append("")
        visualization.append("Legend: Q = Queen, . = Empty square")
        visualization.append(f"Queen positions: {' | '.join(queen_info)}")

        return visualization

    def get_solution(self) -> Optional[List[Tuple[int, int, int]]]:
        """
        Get the solution as a list of (row, col, region_id) tuples.

        Returns:
            Solution positions or None if no solution found
        """
        if self.solution is None:
            return None
        return [(q.row, q.col, q.region_id) for q in self.solution]

    def get_stats(self) -> Dict[str, int]:
        """
        Get solving statistics.

        Returns:
            Dictionary with solving statistics
        """
        return {
            'attempts': self.attempts,
            'backtracks': self.backtracks,
            'queens_placed': len(self.board.get_queens()),
            'time_elapsed': time.time() - self.start_time if self.start_time > 0 else 0
        }


def solve_queens(board: Board) -> Optional[List[Tuple[int, int, int]]]:
    """
    Convenience function to solve a Queens puzzle.

    Args:
        board: Board instance with region mapping

    Returns:
        Solution as list of (row, col, region_id) tuples, or None if unsolvable
    """
    solver = QueensSolver(board)
    if solver.solve():
        return solver.get_solution()
    return None