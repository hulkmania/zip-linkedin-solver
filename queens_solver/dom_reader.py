"""
DOM reader for Queens game on LinkedIn.

This module parses the LinkedIn DOM to extract the Queens board state,
including colored regions and existing queen placements.
"""

import logging
import re
from typing import Dict, List, Tuple, Optional, Set
from playwright.async_api import Page
from .board import Board
from .queen import Queen

logger = logging.getLogger('queens_solver')


class QueensDOMReader:
    """
    Reads and parses the Queens game state from LinkedIn DOM.
    """

    # CSS selectors for Queens game elements
    QUEENS_BOARD_SELECTOR = "#queens-game-board"
    CELL_SELECTOR = "[data-cell-idx]"

    def __init__(self, page: Page):
        """
        Initialize the DOM reader with a Playwright page.

        Args:
            page: Playwright Page instance for LinkedIn
        """
        self.page = page

    def read_board_state(self) -> Tuple[Board, List[Queen]]:
        """
        Read the current state of the Queens board from the DOM.

        Returns:
            Tuple of (Board with region mapping, List of existing queens)
        """
        logger.info("Reading Queens board state from DOM")

        # Wait for the board to be visible
        self.page.wait_for_selector(self.QUEENS_BOARD_SELECTOR, timeout=10000)

        # Determine board size
        board_size = self._get_board_size()
        logger.info(f"Detected board size: {board_size}x{board_size}")

        board = Board(board_size)
        existing_queens = []

        # Read region mapping from cells
        region_map = self._read_region_mapping()
        board.set_region_map(region_map)

        # Read existing queens
        existing_queens = self._read_existing_queens(region_map)

        # Log board visualization for debugging
        board_visualization = self._create_board_visualization(region_map, existing_queens)
        logger.info(f"Board parsed: {len(region_map)} cells mapped, {len(existing_queens)} existing queens")
        logger.info("Board region layout (numbers = region IDs, Q = existing queens):")
        for line in board_visualization:
            logger.info(line)

        return board, existing_queens

    def _read_region_mapping(self) -> Dict[Tuple[int, int], int]:
        """
        Read the mapping of board positions to colored regions.

        Returns:
            Dictionary mapping (row, col) to region_id
        """
        region_map = {}

        # Get all cells
        cells = self.page.query_selector_all(f"{self.QUEENS_BOARD_SELECTOR} {self.CELL_SELECTOR}")

        # Determine board size once
        board_size = self._get_board_size()

        for cell in cells:
            cell_idx = cell.get_attribute("data-cell-idx")
            if cell_idx is None:
                continue

            idx = int(cell_idx)
            row = idx // board_size
            col = idx % board_size

            # Get computed background color using JavaScript
            bg_color = self.page.evaluate("""
                (cell) => {
                    const computedStyle = window.getComputedStyle(cell);
                    return computedStyle.backgroundColor;
                }
            """, cell)

            # Assign region ID based on background color
            if bg_color not in Board.REGION_CLASSES:
                new_region_id = len(Board.REGION_CLASSES)
                Board.REGION_CLASSES[bg_color] = new_region_id
                logger.info(f"Discovered new background color: '{bg_color}' -> Region ID {new_region_id}")

            region_id = Board.REGION_CLASSES[bg_color]
            region_map[(row, col)] = region_id
            logger.debug(f"Cell ({row}, {col}) -> Region {region_id} (color: {bg_color})")

        return region_map

    def _extract_region_from_classes(self, class_string: str) -> Optional[int]:
        """
        Extract region ID from CSS classes based on background-color.

        Uses the color classes identified from CSS analysis to map regions correctly.
        Each color class corresponds to a specific region number (0-8).

        Args:
            class_string: Space-separated CSS classes

        Returns:
            Region ID (0-8) or None if not found
        """
        classes = class_string.split()

        # DEPRECATED: This method uses fixed class mappings that don't work with dynamic CSS
        logger.warning("_extract_region_from_classes is deprecated. Regions are now identified dynamically by background-color.")
        return None

    def _create_board_visualization(self, region_map: Dict[Tuple[int, int], int], existing_queens: List[Queen] = None) -> List[str]:
        """
        Create a visual representation of the board showing region IDs and existing queens.

        Args:
            region_map: Mapping of (row, col) to region_id
            existing_queens: List of existing Queen objects

        Returns:
            List of strings representing the board visualization
        """
        if not region_map:
            return ["(empty board)"]

        # Determine board size
        max_row = max(r for r, c in region_map.keys())
        max_col = max(c for r, c in region_map.keys())
        board_size = max(max_row, max_col) + 1

        # Create queen position map for quick lookup
        queen_positions = set()
        if existing_queens:
            queen_positions = {(q.row, q.col) for q in existing_queens}

        visualization = []

        # Add header
        header = "    " + " ".join(f"{i:2d}" for i in range(board_size))
        visualization.append(header)
        visualization.append("   " + "-" * (board_size * 3))

        # Add each row
        for row in range(board_size):
            row_str = f"{row:2d} |"
            for col in range(board_size):
                if (row, col) in queen_positions:
                    cell_str = " Q"
                else:
                    region_id = region_map.get((row, col), -1)
                    if region_id == -1:
                        cell_str = " ?"
                    else:
                        cell_str = f"{region_id:2d}"
                row_str += cell_str
            visualization.append(row_str)

        return visualization

    def _read_existing_queens(self, region_map: Dict[Tuple[int, int], int]) -> List[Queen]:
        """
        Read existing queens from the board.

        Args:
            region_map: Mapping of positions to regions

        Returns:
            List of existing Queen objects
        """
        existing_queens = []

        # Get all cells
        cells = self.page.query_selector_all(f"{self.QUEENS_BOARD_SELECTOR} {self.CELL_SELECTOR}")

        # Determine board size once
        board_size = self._get_board_size()

        for cell in cells:
            cell_idx = cell.get_attribute("data-cell-idx")
            if cell_idx is None:
                continue

            idx = int(cell_idx)
            row = idx // board_size
            col = idx % board_size

            # Check if cell contains a queen
            has_queen = self._cell_has_queen(cell)
            if has_queen:
                region_id = region_map.get((row, col))
                if region_id is not None:
                    queen = Queen(row, col, region_id)
                    existing_queens.append(queen)
                    logger.debug(f"Found existing queen at ({row}, {col}) in region {region_id}")

        return existing_queens

    def _cell_has_queen(self, cell) -> bool:
        """
        Check if a cell contains a queen by looking for queen indicators.

        Uses multiple detection methods for robustness:
        1. SVG elements with queen aria-label
        2. Queen indicator classes (fallback)
        3. Special div elements that indicate queen presence

        Args:
            cell: Playwright element handle for the cell

        Returns:
            True if cell contains a queen, False otherwise
        """
        try:
            # Method 1: Look for SVG elements with queen aria-label (most reliable)
            queen_svgs = cell.query_selector_all('svg[aria-label="Regina"]')
            if queen_svgs:
                return True

            # Method 2: Look for queen SVG by data-testid
            queen_svgs_alt = cell.query_selector_all('svg[data-testid="queen-svg"]')
            if queen_svgs_alt:
                return True

            # Method 3: Check aria-label of the cell itself
            aria_label = cell.get_attribute("aria-label")
            if aria_label and "regina" in aria_label.lower():
                return True

            # Method 4: Look for any child elements that might indicate a queen
            # Check for any SVG elements (queens are typically represented as SVGs)
            all_svgs = cell.query_selector_all('svg')
            if all_svgs:
                # If there are SVGs in the cell, likely a queen is placed
                logger.debug(f"Found {len(all_svgs)} SVG elements in cell - assuming queen")
                return True

        except Exception as e:
            logger.debug(f"Error checking cell for queen: {e}")

        return False

    def get_cell_selector(self, row: int, col: int, board_size: int = 8) -> str:
        """
        Get the CSS selector for a specific cell.

        Args:
            row: Row index (0 to board_size-1)
            col: Column index (0 to board_size-1)
            board_size: Size of the board (NxN)

        Returns:
            CSS selector for the cell
        """
        cell_idx = row * board_size + col
        return f"{self.QUEENS_BOARD_SELECTOR} [data-cell-idx='{cell_idx}']"

    def is_board_ready(self) -> bool:
        """
        Check if the Queens board is loaded and ready.

        Returns:
            True if board is ready, False otherwise
        """
        try:
            self.page.wait_for_selector(self.QUEENS_BOARD_SELECTOR, timeout=5000)
            return True
        except:
            return False

    def _get_board_size(self) -> int:
        """
        Get the size of the Queens board (N for NxN).

        Returns:
            Board size N
        """
        cells = self.page.query_selector_all(f"{self.QUEENS_BOARD_SELECTOR} {self.CELL_SELECTOR}")
        total_cells = len(cells)

        # Calculate board size from total cells
        # Assume square board, so size = sqrt(total_cells)
        import math
        board_size = int(math.sqrt(total_cells))

        if board_size * board_size != total_cells:
            logger.warning(f"Board is not square: {total_cells} cells, using {board_size}x{board_size} approximation")

        logger.info(f"Calculated board size: {board_size} ({total_cells} cells)")
        return board_size

    def get_board_dimensions(self) -> Tuple[int, int]:
        """
        Get the dimensions of the Queens board.

        Returns:
            Tuple of (rows, cols) - (N, N) for Queens
        """
        size = self._get_board_size()
        return (size, size)


def read_queens_board(page: Page) -> Tuple[Board, List[Queen]]:
    """
    Convenience function to read Queens board state.

    Args:
        page: Playwright Page instance

    Returns:
        Tuple of (Board, existing_queens)
    """
    reader = QueensDOMReader(page)
    return reader.read_board_state()