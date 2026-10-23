# 2048

A Python/Pygame simple 2048 game

## Run on Windows

Open the outer `2048` folder in VS Code.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirement.txt
```

Later launches only need to run the application. You can start the game using **either** of the following methods from your terminal:

### Method 1: Run from the root directory (Recommended)
Stay in the main folder and target the entry point inside `src`:
```powershell
.\.venv\Scripts\python.exe src\main.py
```

### Method 2: Change directories into `src`
Navigate into the `src` folder first, then run the script (pointing back one directory to your virtual environment):
```powershell
cd src
..\.venv\Scripts\python.exe main.py
```

On macOS or Linux, use `python3.12 -m venv .venv`, then `.venv/bin/python -m pip install -r requirement.txt` and `.venv/bin/python src/main.py`.

Keep `assets` alongside `main.py` inside the `src` folder. The bundled fonts require no separate installation. Their license is in `assets/FONT-LICENSE.txt`.

The inner folder is `2048_Game`, matching the string in your uploaded `main.py`. Preserve that capitalization. Python's usual import syntax cannot start with a digit, so `main.py` loads the package with `import_module()`.

## Controls

| Input | Action |
| --- | --- |
| Arrow keys or WASD | Slide tiles |
| Hold a direction | Repeat moves |
| Mouse or touch swipe | Slide in the swipe direction |
| R | New game |
| U or Z | Undo one move |
| M | Toggle reduced motion |
| Tab / Shift+Tab | Move button focus |
| Enter / Space | Activate a focused button or ending-screen action |
| Esc | Quit |

The best score and motion preference retain the existing save location and JSON keys. Undo restores the previous board, score, and random-generator state.

## Change the feel

In `src/2048_Game/settings.py`:

```python
SLIDE, SPAWN, MERGE = 0.12, 0.18, 0.16
POP = 0.18
INPUT_BUFFER = 2
```

Durations are in seconds. `POP` is the extra merge scale, so `0.18` produces a peak of `1.18` times normal size. The input buffer holds up to two directions beyond the active slide.

For a larger window, change the last line of `main.py` to `App(window_size=(720, 957)).run()`. `CANVAS` describes the drawing coordinates; the renderer scales that design to the actual window.

The title bar is set with `pygame.display.set_caption("2048")` in `app.py`. The large title inside the game is drawn in `screen.py`.
