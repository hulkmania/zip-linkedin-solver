"""
Board representation for the Queens game solver.

This module defines the Board class that represents the 8x8 chessboard
with colored regions and handles queen placement validation.
"""

from typing import Dict, List, Set, Tuple, Optional
import logging
from .queen import Queen

logger = logging.getLogger('queens_solver')


class Board:
    """
    Represents the Queens game board with colored regions.

    The board is an 8x8 grid divided into 8 distinct colored regions.
    Each region can contain exactly one queen.
    """

    # Background color mappings for colored regions
    # This is populated dynamically by the DOM reader as new background colors are discovered
    # Keys are CSS background-color values, values are region IDs
    REGION_CLASSES: Dict[str, int] = {}

    # Board size is dynamic, but Queens typically uses 9x9 with 9 regions
    # Determined at runtime from the actual board

    def __init__(self, size: int = 8):
        """
        Initialize an empty board.

        Args:
            size: Board size (NxN), defaults to 8
        """
        self.size = size
        self.queens: List[Queen] = []
        self.region_map: Dict[Tuple[int, int], int] = {}
        self._occupied_rows: Set[int] = set()
        self._occupied_cols: Set[int] = set()
        self._occupied_regions: Set[int] = set()

    def set_region_map(self, region_map: Dict[Tuple[int, int], int]):
        """
        Set the mapping of board positions to colored regions.

        Args:
            region_map: Dictionary mapping (row, col) tuples to region IDs (0-7)
        """
        self.region_map = region_map.copy()

    def get_region_at(self, row: int, col: int) -> Optional[int]:
        """
        Get the region ID at the specified position.

        Args:
            row: Row index (0-7)
            col: Column index (0-7)

        Returns:
            Region ID (0-7) or None if position not mapped
        """
        return self.region_map.get((row, col))

    def is_valid_placement(self, queen: Queen) -> bool:
        """
        Check if placing a queen at the specified position is valid.

        Args:
            queen: Queen to place

        Returns:
            True if placement is valid, False otherwise
        """
        row, col, region_id = queen.row, queen.col, queen.region_id

        # Check bounds
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False

        # Check if position belongs to the correct region
        expected_region = self.get_region_at(row, col)
        if expected_region is None or expected_region != region_id:
            return False

        # Check row conflict
        if row in self._occupied_rows:
            return False

        # Check column conflict
        if col in self._occupied_cols:
            return False

        # Check region conflict (each region can have only one queen)
        if region_id in self._occupied_regions:
            return False

        # Check adjacent diagonal conflicts with existing queens
        for existing_queen in self.queens:
            if abs(row - existing_queen.row) == 1 and abs(col - existing_queen.col) == 1:
                return False

        return True

    def place_queen(self, queen: Queen) -> bool:
        """
        Place a queen on the board if the position is valid.

        Args:
            queen: Queen to place

        Returns:
            True if placement was successful, False otherwise
        """
        if not self.is_valid_placement(queen):
            return False

        self.queens.append(queen)
        self._occupied_rows.add(queen.row)
        self._occupied_cols.add(queen.col)
        self._occupied_regions.add(queen.region_id)

        return True

    def remove_queen(self, queen: Queen) -> bool:
        """
        Remove a queen from the board.

        Args:
            queen: Queen to remove

        Returns:
            True if removal was successful, False otherwise
        """
        if queen not in self.queens:
            return False

        self.queens.remove(queen)
        self._occupied_rows.discard(queen.row)
        self._occupied_cols.discard(queen.col)
        self._occupied_regions.discard(queen.region_id)

        return True

    def is_complete(self) -> bool:
        """
        Check if the board has a complete solution (N queens, one per region).

        For Queens, this means one queen per colored region.

        Returns:
            True if board is complete, False otherwise
        """
        return len(self.queens) == self.size

    def get_queens(self) -> List[Queen]:
        """Get a copy of all queens on the board."""
        return self.queens.copy()

    def get_queen_positions(self) -> List[Tuple[int, int, int]]:
        """
        Get list of queen positions as (row, col, region_id) tuples.

        Returns:
            List of tuples representing queen positions and their regions
        """
        return [(q.row, q.col, q.region_id) for q in self.queens]

    def clear(self):
        """Remove all queens from the board."""
        self.queens.clear()
        self._occupied_rows.clear()
        self._occupied_cols.clear()
        self._occupied_regions.clear()

    def __str__(self) -> str:
        """String representation of the board."""
        grid = [['.' for _ in range(self.size)] for _ in range(self.size)]

        # Place queens on the grid
        for queen in self.queens:
            grid[queen.row][queen.col] = 'Q'

        # Add region information
        lines = []
        for i, row in enumerate(grid):
            line = ' '.join(cell for cell in row)
            region_info = f" | Row {i}"
            lines.append(f"{line}{region_info}")

        return '\n'.join(lines)

    @classmethod
    def get_region_name(cls, region_id: int) -> str:
        """
        Get the human-readable name of a region.

        For Queens game regions, returns generic color-based names since colors are dynamic.
        For dynamically discovered regions, returns generic names.

        Args:
            region_id: Region ID

        Returns:
            Region name
        """
        # Generic region names since colors are now dynamic
        if region_id < 26:  # A-Z
            return f"Region {chr(65 + region_id)}"  # A, B, C, etc.
        else:
            return f"Region {region_id}"

    @classmethod
    def reset_region_classes(cls):
        """
        Reset the region class mappings.
        Useful for testing or when starting a new game.
        """
        cls.REGION_CLASSES.clear()