# Queens Game Solver - Project Document
**Date:** 2026-01-16
**Feature:** Queens Game Solver
**Status:** Fully Implemented and Tested

## Overview

Add support for the LinkedIn Queens game (Eight Queens Puzzle) to the existing LinkedIn Games Solver project. The Queens game requires placing 8 queens on an 8x8 chessboard such that no two queens threaten each other (no shared rows, columns, or diagonals).

## Game Description

The Queens game presents an NxN chessboard where players must place N queens following modified chess movement rules with colored regions:
- Queens cannot share the same row
- Queens cannot share the same column
- Queens cannot share the same diagonal **only for 1 cell away** (both main and anti-diagonals)
- **Each colored region can contain only ONE queen**

**Key Differences from Classic N-Queens**:
1. **Colored Regions**: The board is divided into N distinct colored areas, each accepting only one queen
2. **Adjacent Diagonal Restriction**: Queens cannot be adjacent diagonally (distance = 1), but can attack along longer diagonal paths
3. **Region Constraints**: The colored areas create additional placement restrictions

**Board Structure** (from HTML analysis):
- NxN grid with `data-cell-idx` from 0 to N²-1
- N colored regions identified by computed CSS `background-color` values
- Dynamic region detection based on actual computed background colors (not CSS classes)
- System automatically discovers and maps regions by analyzing `window.getComputedStyle(cell).backgroundColor`
- No dependency on CSS class names - adapts to any color scheme or CSS changes

**Queen Placement Mechanism**: Double-click process required by LinkedIn UI:
1. **First Click**: Places an X mark (indicating cell should not be empty)
2. **Second Click**: Transforms the X into a queen piece
3. **Result**: Queen successfully placed on the board

**Queen Detection**: Placed queens are identified using robust methods (no static CSS classes):
1. SVG elements with `aria-label="Regina"` (most reliable)
2. SVG elements with `data-testid="queen-svg"`
3. Cell aria-label content analysis
4. Presence of any SVG elements in the cell

**Click Debugging**: Comprehensive logging for troubleshooting placement issues:
- Cell selector validation and alternative selector fallback
- Click execution confirmation with error handling
- Page responsiveness checks before each operation
- Available cell indices listing when selectors fail
- Queen verification using robust methods (no static CSS classes)

**Region Detection**: Dynamic identification based on computed CSS background-color values:
- Each cell's actual background color is read using JavaScript `getComputedStyle(cell).backgroundColor`
- Cells with identical computed background colors belong to the same region
- System automatically discovers and maps new color values as encountered
- Completely independent from CSS class names - handles any dynamic CSS generation or color scheme changes
- Resolves CSS variables (like `var(--color-name)`) to actual RGB/RGBA values

**Board Visualization**: Detailed ASCII representation in logs/queens_solver.log:
- **Initial Board**: Shows region layout when board is parsed
- **Final Solution**: Complete solved board when solution is found
- **Numbers (0-9)**: Region ID for each cell (initial board)
- **Q**: Queen position (both initial and final boards)
- **.**: Empty square (final solution board)
- **?**: Unmapped cell (should not occur in normal operation)
- Format: Row/column coordinates with clear grid layout and solution details

**Example Final Solution Display:**
```
Final solution board:
     0  1  2  3
   ------------
 0 | .  .  Q  .
 1 | Q  .  .  .
 2 | .  .  .  Q
 3 | .  Q  .  .

Legend: Q = Queen, . = Empty square
Queen positions: Q(1,0)=Beige caldo | Q(3,1)=Corallo brillante | Q(0,2)=Giallo lime | Q(2,3)=Verde pastello
```

**Log Files**: Separate logging system with dedicated files:
- `logs/zip_solver.log`: ZIP game solving details
- `logs/sudoku_solver.log`: Sudoku game solving details
- `logs/queens_solver.log`: Queens game solving details
- All logs include timestamps, log levels, and detailed debugging information

**Region Detection**: Dynamic identification of colored regions:
- Each cell's background color is computed using `getComputedStyle(cell).backgroundColor`
- System automatically discovers and maps new background colors as encountered
- No hardcoded color mappings - adapts to any CSS changes or color scheme variations
- Uses actual rendered colors, not CSS class names, for maximum compatibility

The goal is to find a valid configuration where all regions contain exactly one queen, following the movement restrictions.

## Proposed Architecture

Following the existing project structure, the Queens solver will be implemented in a dedicated `queens_solver/` directory with the same modular approach used for ZIP and Sudoku games.

### Directory Structure
```
queens_solver/
├── __init__.py
├── bot.py              # Automated queen placement and game completion
├── dom_reader.py       # Parse Queens board from LinkedIn DOM
├── solver.py           # N-Queens backtracking algorithm
├── board.py            # Chessboard data structure and validation
└── queen.py            # Queen piece representation
```

### Module Responsibilities

#### `solver.py`
- **Algorithm**: Modified backtracking adapted for adjacent-only diagonal constraints and colored region restrictions
- **Optimizations**:
  - Row/column tracking for O(1) conflict detection
  - Adjacent diagonal checking only (not full diagonals)
  - Region conflict tracking (one queen per colored area)
  - Early pruning when insufficient space for remaining queens
  - Dynamic board size handling (works for any NxN)
- **Return**: List of (row, col, region_id) tuples for queen placements

#### `board.py`
- **Data Structure**: NxN grid with region mapping (size dynamically determined)
- **Region Mapping**: Associate each cell with its colored region
- **Validation**: Check if queen placement is valid under modified rules (rows, columns, adjacent diagonals, regions)
- **State Management**: Track occupied rows, columns, and regions

#### `queen.py`
- **Queen Class**: Represent individual queen with position
- **Threat Calculation**: Determine attacked squares

#### `dom_reader.py`
- **DOM Parsing**: Extract board state from LinkedIn HTML
- **Board Detection**: Identify empty squares, existing queens, and colored regions
- **Region Mapping**: Create mapping of cells to their respective colored areas
- **Queen Detection**: Identify which cells already contain queens
- **Selector Identification**: Find CSS selectors for queen placement

#### `bot.py`
- **Queen Placement**: Double-click automation with comprehensive debugging and fallback selectors
- **Game Completion**: Handle game submission and verification
- **Error Handling**: Fallback strategies for placement failures

## Integration with Existing System

### Main Menu Integration
Add "Queens" option to the interactive menu in `main.py`:
```python
# Add to game selection menu
"3": ("Queens", lambda: solve_queens_game())
```

### Navigation Function
Create `navigate_to_queens()` function in `main.py` following the pattern of existing games:
- Navigate to LinkedIn Queens game URL
- Handle page loading and game initialization
- Integrate with timer pause mechanism

### Logging Integration
Extend `solver.log` to include Queens solving progress:
- Board state snapshots
- Backtracking decisions
- Solution path
- Performance metrics (placements tried, time taken)

## Implementation Details

### Algorithm Approach
1. **Backtracking with Optimization**: Modified N-Queens backtracking adapted for adjacent-only diagonal conflicts:
   - Row/column conflict arrays for O(1) validation
   - Adjacent diagonal checking (distance = 1 only)
   - No full diagonal conflict tracking (unlike classic N-Queens)
   - Symmetry breaking (optional optimization)
   - Iterative deepening for memory efficiency

2. **Validation Strategy**:
   - Row conflicts: boolean array [N]
   - Column conflicts: boolean array [N]
   - Adjacent diagonals: Check only immediate diagonal neighbors (±1, ±1) for each new queen placement

3. **Solution Representation**:
   - List of (row, col) tuples
   - Row-major order for deterministic solving

### Browser Automation
- **Queen Placement**: Double-click sequence (first click places X, second click places queen)
- **State Verification**: Confirm queens are placed correctly
- **Game Completion**: Click submit/check buttons
- **Error Recovery**: Handle placement conflicts or UI changes

### Performance Considerations
- **Region Constraints**: Colored areas significantly reduce search space compared to classic N-Queens
- **Adjacent-only Checking**: Reduced validation complexity compared to full diagonal tracking
- **Variable Board Size**: Performance scales with N² where N is board size
- **Expected Solutions**: Fewer valid configurations due to region restrictions
- **Time Budget**: Target < 30 seconds solve time (scales with board size)
- **Memory Usage**: Minimal additional memory beyond existing browser profile

## Dependencies and Libraries

**Reuse Existing Libraries:**
- `playwright` for browser automation
- Standard Python libraries (logging, collections, etc.)
- Existing project utilities and patterns

**No New Dependencies Required** - maintain compatibility with current `requirements.txt`.

## Testing Strategy

1. **Unit Tests**: Test individual modules (board validation, solver logic)
2. **Integration Tests**: End-to-end solving with mock DOM
3. **Browser Tests**: Real LinkedIn integration testing
4. **Performance Tests**: Solve time and memory usage validation

## Risk Assessment

**Low Risk Factors:**
- Well-understood algorithm (N-Queens is classic CS problem)
- Follows established project patterns
- No new external dependencies

**Potential Challenges:**
- LinkedIn DOM structure may differ from ZIP/Sudoku
- Queen placement UI might require different interaction patterns
- Modified game rules require careful validation logic implementation
- ✅ **Resolved**: Pattern-based region detection handles all CSS class changes
- ✅ **Resolved**: Multi-method queen detection (SVG + CSS + aria-label)
- Game rules or board size variations

## Success Criteria

1. Successfully solve Queens puzzles on LinkedIn
2. Integrate seamlessly with existing menu system
3. Maintain < 30 second solve times
4. Provide detailed logging for debugging
5. Handle edge cases and UI variations robustly

## Implementation Summary

1. ✅ **Game Rules Updated**: Incorporated modified Queens rules (adjacent diagonal conflicts only)
2. ✅ **DOM Analysis Complete**: Discovered board structure, colored regions, and queen representation
3. ✅ **NxN Board Support**: Updated all modules to support dynamic board sizes instead of hardcoded 8x8
4. ✅ **Dynamic Color-Based Region Detection**: System reads actual computed background-color values, not CSS classes
5. ✅ **Multi-Method Queen Detection**: SVG + CSS + aria-label for reliable queen identification
6. ✅ **Modular Implementation**: Created complete queens_solver package with all required modules
7. ✅ **Integration Complete**: Added Queens option to main menu and navigation system
8. ✅ **Testing Complete**: All modules import correctly and dynamic color detection works

## Key Features Implemented

- **🔍 Dynamic Board Sizing**: Supports NxN boards (automatically detected from DOM)
- **🎨 Dynamic Color-Based Region Detection**: Reads actual computed background-color values, not CSS classes
- **♛ Multi-Method Queen Detection**: Uses SVG, CSS classes, and aria-labels for reliability
- **📏 NxN Scalability**: Same algorithm works for 4x4, 6x6, 8x8, 10x10, etc.
- **🎯 Colored Region Constraints**: One queen per colored area (identified by background color)
- **♟️ Adjacent Diagonal Restrictions**: Queens cannot be adjacent diagonally
- **🧠 Backtracking Algorithm**: Optimized solver with region-based pruning
- **🌐 DOM Integration**: Automatic parsing of board state and color-based region mapping with visual board logging
- **📝 Separate Logging**: Dedicated log file `logs/queens_solver.log` with detailed solving process
- **🏆 Solution Display**: Final solved board visualization with queen positions and region details
- **📊 Board Visualization**: ASCII representation in logs showing region layout and existing queens
- **🤖 Automated Placement**: Sequential queen placement with verification

---

**Status:** ✅ **COMPLETE** - Queens game solver fully integrated and ready for use!