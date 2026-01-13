import time


def click_path(frame, path, cols, delay=0.001):
    for r, c in path:
        idx = r * cols + c
        # Usa lo stesso selettore di read_grid: data-cell-idx
        try:
            frame.click(f"//div[@data-cell-idx='{idx}']", timeout=5000)
        except Exception as e:
            # Se fallisce, prova con force click
            print(f"⚠️ Click normale fallito su cella {idx} ({r},{c}), provo force click...")
            try:
                frame.locator(f"//div[@data-cell-idx='{idx}']").click(force=True, timeout=5000)
            except Exception as e2:
                print(f"❌ Anche force click fallito su cella {idx} ({r},{c}): {e2}")
                continue
        time.sleep(delay)
