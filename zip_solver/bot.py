import time


def click_path(frame, path, cols, delay=0.001):
    for r, c in path:
        idx = r * cols + c
        # Usa lo stesso selettore di read_grid: data-cell-idx
        frame.click(f"//div[@data-cell-idx='{idx}']")
        time.sleep(delay)
