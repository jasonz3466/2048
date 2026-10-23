# 2048

A Python/Pygame game using your classic palette, independent tile effects, and a short ordered input queue.

## Run on Windows

Open the outer `2048` folder in VS Code. Its `main.py` is the entry point.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Later launches only need the last command. On macOS or Linux, use `python3.12 -m venv .venv`, then `.venv/bin/python -m pip install -r requirements.txt` and `.venv/bin/python main.py`.

Keep `assets` alongside `main.py`. The bundled fonts require no separate installation. Their license is in `assets/FONT-LICENSE.txt`.

The inner folder is `2048_Game`, matching the string in your uploaded `main.py`. Preserve that capitalization. Python's usual import syntax cannot start with a digit, so `main.py` loads the package with `import_module()`.

## Updating your existing copy

Replace `animation.py`, `app.py`, `controls.py`, `screen.py`, and `settings.py` inside your game package, and add the new `tile_effects.py` beside them. Use the included `game.py` if you have not yet applied the corrected loss check. All files needed for a fresh installation are included.

Restart after copying the files. The new animation module imports `tile_effects.py`, so those files must be installed together.

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

In `2048_Game/settings.py`:

```python
SLIDE, SPAWN, MERGE = 0.12, 0.18, 0.16
POP = 0.18
INPUT_BUFFER = 2
```

Durations are in seconds. `POP` is the extra merge scale, so `0.18` produces a peak of `1.18` times normal size. The input buffer holds up to two directions beyond the active slide.

For a larger window, change the last line of `main.py` to `App(window_size=(720, 957)).run()`. `CANVAS` describes the drawing coordinates; the renderer scales that design to the actual window.

The title bar is set with `pygame.display.set_caption("2048")` in `app.py`. The large title inside the game is drawn in `screen.py`.

## Learn and verify

Read `LEARN.md` for the motion explanation, module map, exercises, and complete source of every application file.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The project includes 47 tests covering rules, premature loss, input, drawing, motion continuity, saving, and undo.