# Project Overview

This project is a Python-based solver for the LinkedIn "ZIP" game. It uses the Playwright library to automate a Chromium browser, allowing it to read the game's grid structure directly from the live DOM.

The core of the project is a sophisticated solver that employs a recursive Depth First Search (DFS) algorithm with backtracking to find the correct path through the puzzle. To optimize the search, the solver implements intelligent cutoff strategies, including:

*   **Manhattan Distance:** It prunes paths where the distance to the next required number is greater than the number of remaining cells to be visited.
*   **Connectivity Analysis:** It discards paths that would result in "islands" of unvisited cells, which would be impossible to traverse.

The project is structured into several modules:

*   `main.py`: The main entry point that orchestrates the browser automation, grid parsing, and solving process.
*   `zip_solver/solver.py`: Contains the core DFS-based puzzle-solving logic.
*   `zip_solver/dom_reader.py`: Responsible for parsing the game's grid, numbers, and walls from the browser's DOM.
*   `zip_solver/bot.py`: Automates the process of clicking the solution path in the browser.
*   `zip_solver/grid.py` and `zip_solver/cell.py`: Define the data structures for representing the game's grid and its individual cells.

## Building and Running

### Prerequisites

*   Python 3
*   A virtual environment is recommended.

### Installation

1.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    .venv\Scripts\Activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install the Chromium browser for Playwright (one-time setup):**
    ```bash
    python -m playwright install chromium
    ```

### Running the Solver

1.  **Execute the main script:**
    ```bash
    python main.py
    ```

2.  **First-time run:** The script will open a browser and navigate to LinkedIn. You will need to log in manually. After logging in, press Enter in the console to continue.

3.  **Subsequent runs:** The browser profile is saved in the `browser_profile` directory, so you should remain logged in.

The solver will then navigate to the ZIP game, analyze the grid, and automatically click through the solution. Detailed logs of the solving process are written to `solver.log`.

## Development Conventions

*   **Modular Design:** The code is organized into distinct modules with clear responsibilities (e.g., `solver`, `dom_reader`, `bot`).
*   **Logging:** The solver provides detailed logging to a `solver.log` file, which is useful for debugging the backtracking algorithm.
*   **Browser Automation:** The project uses Playwright for robust browser automation, including techniques to avoid being detected as a bot.
*   **DOM Parsing:** The `dom_reader` module is designed to be adaptable to potential changes in the LinkedIn game's HTML structure.

## New Feature Workflow

Before implementing any new feature, the following process must be followed:

1.  **Create a Project Document:** A project document must be created that outlines the new feature.
2.  **Document Content:** The document should describe in detail what will be developed and how it will be implemented.
3.  **Naming and Location:** The document must be named using the format `YYYY-MM-DD-feature-name.md` (e.g., `2026-01-09-new-feature.md`) and placed in the `/docs` directory. The current date must be used in the filename.
4.  **Confirmation:** Await confirmation from the user before proceeding with the implementation.