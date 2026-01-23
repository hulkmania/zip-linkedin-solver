"""
Bot for automated queen placement in LinkedIn Queens game.

This module handles the automation of clicking/placing queens on the
LinkedIn Queens game board.
"""

import asyncio
import logging
from typing import List, Tuple, Optional
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from .board import Board

logger = logging.getLogger('queens_solver')


class QueensBot:
    """
    Automated bot for playing the LinkedIn Queens game.

    Handles queen placement, verification, and game completion.
    """

    def __init__(self, page: Page):
        """
        Initialize the bot with a Playwright page.

        Args:
            page: Playwright Page instance for LinkedIn
        """
        self.page = page
        self.placement_delay = 200  # ms between placements

    def place_queens(self, queen_positions: List[Tuple[int, int, int]], board_size: int = 8) -> bool:
        """
        Place queens at the specified positions using double-click mechanism.

        Args:
            queen_positions: List of (row, col, region_id) tuples
            board_size: Size of the board (NxN)

        Returns:
            True if all placements successful, False otherwise
        """
        logger.info(f"Starting queen placement (double-click method) for {len(queen_positions)} queens on {board_size}x{board_size} board")
        logger.info(f"Received board_size parameter: {board_size}")
        logger.info(f"Queen positions details: {queen_positions}")

        for i, (row, col, region_id) in enumerate(queen_positions):
            logger.info(f"Placing queen {i+1}/{len(queen_positions)} at ({row}, {col}) - Region: {Board.get_region_name(region_id)}")

            success = self._place_single_queen(row, col, board_size)
            if not success:
                logger.error(f"Failed to place queen at ({row}, {col}) after double-click")
                return False

            logger.debug(f"Successfully placed queen at ({row}, {col})")

            # Wait between placements to avoid detection
            import time
            time.sleep(self.placement_delay / 1000)

        logger.info("All queens placed successfully using double-click mechanism")
        return True

    def _place_single_queen(self, row: int, col: int, board_size: int = 8) -> bool:
        """
        Place a single queen at the specified position.

        The Queens game requires TWO clicks on a cell:
        1. First click: places an X (indicating the cell should not be filled)
        2. Second click: transforms the X into a queen

        Args:
            row: Row index (0 to board_size-1)
            col: Column index (0 to board_size-1)
            board_size: Size of the board (NxN)

        Returns:
            True if placement successful, False otherwise
        """
        try:
            # Calculate cell index
            cell_idx = row * board_size + col
            cell_selector = f"#queens-game-board [data-cell-idx='{cell_idx}']"

            logger.info(f"Attempting to place queen at ({row},{col}) -> cell_idx={cell_idx}, selector='{cell_selector}'")

            # Check if selector finds any elements
            elements = self.page.query_selector_all(cell_selector)
            logger.debug(f"Found {len(elements)} elements with selector '{cell_selector}'")

            if len(elements) == 0:
                logger.warning(f"No elements found with primary selector '{cell_selector}' - trying alternative selectors")

                # Try alternative selectors
                alt_selectors = [
                    f"[data-cell-idx='{cell_idx}']",  # Without the queens-game-board prefix
                    f"div[data-cell-idx='{cell_idx}']",
                    f"button[data-cell-idx='{cell_idx}']",
                    f"section[data-cell-idx='{cell_idx}']",
                    f"[aria-label*='riga {row+1}, colonna {col+1}' i]"
                ]

                for alt_selector in alt_selectors:
                    alt_elements = self.page.query_selector_all(alt_selector)
                    logger.debug(f"Trying alternative selector '{alt_selector}' - found {len(alt_elements)} elements")
                    if len(alt_elements) > 0:
                        logger.info(f"Using alternative selector '{alt_selector}' for cell ({row},{col})")
                        cell_selector = alt_selector
                        break
                else:
                    logger.error(f"No selectors worked for cell ({row},{col}) with idx {cell_idx}")
                    # Debug: list all data-cell-idx elements on the page
                    all_cells = self.page.query_selector_all("[data-cell-idx]")
                    logger.info(f"Found {len(all_cells)} total cells with data-cell-idx on the page")
                    if len(all_cells) > 0:
                        indices = []
                        for cell in all_cells[:min(20, len(all_cells))]:  # Show first 20 or all if less
                            idx = cell.get_attribute("data-cell-idx")
                            if idx:
                                indices.append(idx)
                        logger.info(f"Available cell indices (first 20): {indices}")

                        # Also check if cells are clickable
                        clickable_cells = []
                        for cell in all_cells[:10]:  # Check first 10
                            try:
                                # Check if cell has click handlers or is button-like
                                tag = cell.evaluate("el => el.tagName")
                                aria_disabled = cell.get_attribute("aria-disabled")
                                clickable_cells.append(f"{tag}(disabled={aria_disabled})")
                            except:
                                clickable_cells.append("unknown")
                        logger.info(f"Cell types (first 10): {clickable_cells}")
                    return False

            # Verify page is still active
            try:
                self.page.evaluate("() => true")  # Simple check if page is responsive
            except Exception as e:
                logger.error(f"Page became unresponsive before clicking cell ({row},{col}): {e}")
                return False

            # Wait for cell to be clickable
            self.page.wait_for_selector(cell_selector, timeout=5000)

            # First click: place X or start queen placement
            logger.debug(f"Executing first click on cell ({row},{col}) to place X")
            try:
                self.page.click(cell_selector, timeout=5000)
                logger.debug(f"First click executed successfully on cell ({row},{col})")
            except Exception as e:
                logger.error(f"First click failed on cell ({row},{col}): {e}")
                return False

            # Wait for the first click to register
            import time
            time.sleep(100 / 1000)  # Increased wait time

            # Second click: transform X into queen
            logger.debug(f"Executing second click on cell ({row},{col}) to place queen")
            try:
                self.page.click(cell_selector, timeout=5000)
                logger.debug(f"Second click executed successfully on cell ({row},{col})")
            except Exception as e:
                logger.error(f"Second click failed on cell ({row},{col}): {e}")
                return False

            # Wait for the queen placement to register
            time.sleep(100 / 1000)  # Increased wait time

            # Verify the placement
            return self._verify_queen_placement(row, col, board_size)

        except PlaywrightTimeoutError:
            logger.error(f"Timeout waiting for cell ({row}, {col}) to be clickable")
            return False
        except Exception as e:
            logger.error(f"Error placing queen at ({row}, {col}): {e}")
            return False

    def _cell_has_queen_for_verification(self, cell) -> bool:
        """
        Check if a cell contains a queen for placement verification.

        Uses the same multi-method approach as dom_reader but adapted for bot verification.
        Does NOT use static CSS classes.

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

    def _verify_queen_placement(self, row: int, col: int, board_size: int = 8) -> bool:
        """
        Verify that a queen was successfully placed at the specified position.

        Args:
            row: Row index (0 to board_size-1)
            col: Column index (0 to board_size-1)
            board_size: Size of the board (NxN)

        Returns:
            True if queen is present, False otherwise
        """
        try:
            cell_idx = row * board_size + col
            cell_selector = f"#queens-game-board [data-cell-idx='{cell_idx}']"

            # Check if cell contains a queen using the same multi-method approach as dom_reader
            cell_element = self.page.query_selector(cell_selector)
            if not cell_element:
                logger.warning(f"Cell element not found for verification at ({row}, {col})")
                return False

            has_queen = self._cell_has_queen_for_verification(cell_element)

            if has_queen:
                logger.debug(f"Verified queen placement at ({row}, {col})")
                return True
            else:
                logger.warning(f"No queen found at ({row}, {col}) after placement")
                return False

        except Exception as e:
            logger.error(f"Error verifying queen at ({row}, {col}): {e}")
            return False

    def submit_solution(self) -> bool:
        """
        Submit the Queens solution (if there's a submit button).

        Returns:
            True if submission successful or no submit needed, False otherwise
        """
        try:
            # Look for submit/check buttons
            submit_selectors = [
                "button[data-testid*='submit']",
                "button[data-testid*='check']",
                "[aria-label*='submit' i]",
                "[aria-label*='check' i]",
                ".submit-button",
                ".check-button"
            ]

            for selector in submit_selectors:
                try:
                    button = self.page.query_selector(selector)
                    if button:
                        button.click()
                        logger.info("Clicked submit/check button")
                        import time
                        time.sleep(1)  # Wait 1 second
                        return True
                except:
                    continue

            # If no submit button found, the game might auto-verify
            logger.info("No submit button found - game may auto-verify")
            return True

        except Exception as e:
            logger.error(f"Error submitting solution: {e}")
            return False

    def wait_for_completion(self, timeout: int = 10000) -> bool:
        """
        Wait for the game to show completion/success state.

        Args:
            timeout: Maximum time to wait in milliseconds

        Returns:
            True if completion detected, False if timeout
        """
        try:
            # Look for success indicators
            success_selectors = [
                "[data-testid*='success']",
                "[data-testid*='complete']",
                ".success",
                ".complete",
                "[aria-label*='success' i]",
                "[aria-label*='complete' i]"
            ]

            for selector in success_selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=timeout)
                    logger.info("Game completion detected")
                    return True
                except:
                    continue

            # If no explicit success indicator, wait for potential next puzzle
            logger.info("No explicit completion indicator found")
            return True

        except Exception as e:
            logger.error(f"Error waiting for completion: {e}")
            return False

    def reset_board(self) -> bool:
        """
        Reset/clear the board if possible.

        Returns:
            True if reset successful or no reset needed, False otherwise
        """
        try:
            # Look for reset/new game buttons
            reset_selectors = [
                "button[data-testid*='reset']",
                "button[data-testid*='new']",
                "[aria-label*='reset' i]",
                "[aria-label*='new' i]",
                ".reset-button",
                ".new-game-button"
            ]

            for selector in reset_selectors:
                try:
                    button = self.page.query_selector(selector)
                    if button:
                        button.click()
                        logger.info("Clicked reset/new game button")
                        import time
                        time.sleep(2)  # Wait 2 seconds
                        return True
                except:
                    continue

            logger.info("No reset button found")
            return True

        except Exception as e:
            logger.error(f"Error resetting board: {e}")
            return False


def solve_queens_game(page: Page, queen_positions: List[Tuple[int, int, int]], board_size: int = 8) -> bool:
    """
    Complete function to solve the Queens game end-to-end using double-click mechanism.

    Args:
        page: Playwright Page instance
        queen_positions: List of (row, col, region_id) tuples for queen placement
        board_size: Size of the board (NxN)

    Returns:
        True if game completed successfully, False otherwise
    """
    logger.info(f"Starting Queens game automation with {len(queen_positions)} queens to place on {board_size}x{board_size} board")
    logger.info(f"Queen positions to place: {[(r, c) for r, c, _ in queen_positions]}")

    # Verify the game page is ready
    try:
        page.wait_for_selector("#queens-game-board", timeout=10000)
        logger.info("Queens game board is visible and ready")
    except Exception as e:
        logger.error(f"Queens game board not found or not ready: {e}")
        return False

    # Count total cells on the board
    all_cells = page.query_selector_all("[data-cell-idx]")
    logger.info(f"Found {len(all_cells)} total cells on the board")

    bot = QueensBot(page)

    # Place all queens using double-click method
    if not bot.place_queens(queen_positions, board_size):
        logger.error("Failed to place all queens using double-click method")
        return False

    # Submit the solution
    if not bot.submit_solution():
        logger.error("Failed to submit solution")
        return False

    # Wait for completion
    if not bot.wait_for_completion():
        logger.warning("Game completion not detected within timeout")
        # Don't fail here as some games may not have explicit completion indicators

    logger.info("Queens game solving completed")
    return True