# hello-world

A small Python project with three tkinter desktop applications:

- `catsim_gui.py`: a CatSim v4 document-driven interface built from `User manual-EN.doc`, `Modelling Technical Manual-EN-Mark.doc`, and `doc-analysis.md`.
- `snake.py`: a classic Snake game.
- `tank_battle.py`: a classic Tank Battle / Battle City-style game.

## Run the CatSim document interface

```bash
python3 catsim_gui.py
```

The CatSim interface summarizes the documented Calibrate/Predict workflow, model modules, engineering risks, migration route, and includes a lightweight demonstration calculation panel. The calculation panel is intentionally transparent and does **not** reproduce proprietary CatSim formulas; it only shows the data flow described in the documents.

## Run the Snake game

```bash
python3 snake.py
```

## Run the Tank Battle game

```bash
python3 tank_battle.py
```

## Tank Battle controls

- Arrow keys or `W`/`A`/`S`/`D`: move your tank
- `Space`: fire
- `P`: pause or resume
- `R`: restart
- `Esc`: quit

Destroy enemy tanks, break brick walls, protect the base marked with a star, and avoid enemy fire. Steel blocks cannot be destroyed.

## Snake controls

- Arrow keys or `W`/`A`/`S`/`D`: move the snake
- `Space`: pause or resume
- `R`: restart
- `Esc`: quit

Eat the red food, avoid the walls, and do not run into your own tail. The snake gets a little faster each time it eats.
