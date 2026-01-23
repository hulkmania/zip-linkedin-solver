"""
Queen piece representation for the Queens game solver.

This module defines the Queen class that represents individual queen pieces
on the board, including their position and attack calculations.
"""

from typing import Tuple, Set
import logging

logger = logging.getLogger('queens_solver')


class Queen:
    """
    Represents a queen piece in the Queens game.

    A queen has a position on the 8x8 board and belongs to a specific colored region.
    Queens cannot share rows, columns, or be adjacent diagonally, and each region
    can contain only one queen.
    """

    def __init__(self, row: int, col: int, region_id: int):
        """
        Initialize a queen at the specified position.

        Args:
            row: Row index (0-7)
            col: Column index (0-7)
            region_id: ID of the colored region this queen belongs to
        """
        self.row = row
        self.col = col
        self.region_id = region_id

    def __repr__(self) -> str:
        """String representation of the queen."""
        return f"Queen({self.row}, {self.col}, region={self.region_id})"

    def __eq__(self, other) -> bool:
        """Check equality based on position and region."""
        if not isinstance(other, Queen):
            return False
        return (self.row == other.row and
                self.col == other.col and
                self.region_id == other.region_id)

    def __hash__(self) -> int:
        """Hash based on position and region for use in sets."""
        return hash((self.row, self.col, self.region_id))

    def get_adjacent_diagonal_positions(self, board_size: int = 8) -> Set[Tuple[int, int]]:
        """
        Get positions that would be adjacent diagonally to this queen.
        These are the positions where queens cannot be placed.

        Args:
            board_size: Size of the board (NxN), defaults to 8

        Returns:
            Set of (row, col) tuples representing forbidden adjacent diagonal positions
        """
        forbidden_positions = set()

        # Adjacent diagonal positions (distance = 1)
        diagonals = [
            (self.row - 1, self.col - 1),  # Top-left
            (self.row - 1, self.col + 1),  # Top-right
            (self.row + 1, self.col - 1),  # Bottom-left
            (self.row + 1, self.col + 1),  # Bottom-right
        ]

        # Filter to valid board positions
        for r, c in diagonals:
            if 0 <= r < board_size and 0 <= c < board_size:
                forbidden_positions.add((r, c))

        return forbidden_positions

    def conflicts_with(self, other: 'Queen') -> bool:
        """
        Check if this queen conflicts with another queen according to game rules.

        Args:
            other: Another Queen instance

        Returns:
            True if queens conflict, False otherwise
        """
        # Same row
        if self.row == other.row:
            return True

        # Same column
        if self.col == other.col:
            return True

        # Adjacent diagonally (distance = 1)
        if abs(self.row - other.row) == 1 and abs(self.col - other.col) == 1:
            return True

        # Same region (each region can have only one queen)
        if self.region_id == other.region_id:
            return True

        # Queens can still attack along longer diagonals, but we don't check that here
        # as it's handled by the board validation

        return False

    def get_position(self) -> Tuple[int, int]:
        """Get the (row, col) position of this queen."""
        return (self.row, self.col)

    def get_region(self) -> int:
        """Get the region ID of this queen."""
        return self.region_id