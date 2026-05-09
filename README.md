# hello-world

A small Python project with two tkinter desktop applications:

- `catsim_gui.py`: a CatSim v4 document-driven interface built from `User manual-EN.doc`, `Modelling Technical Manual-EN-Mark.doc`, and `doc-analysis.md`.
- `snake.py`: a classic Snake game.

## Run the CatSim document interface

```bash
python3 catsim_gui.py
```

The CatSim interface summarizes the documented Calibrate/Predict workflow, model modules, engineering risks, migration route, and includes a lightweight demonstration calculation panel. The calculation panel is intentionally transparent and does **not** reproduce proprietary CatSim formulas; it only shows the data flow described in the documents.

## Run the Snake game

```bash
python3 snake.py
```

## Snake controls

- Arrow keys or `W`/`A`/`S`/`D`: move the snake
- `Space`: pause or resume
- `R`: restart
- `Esc`: quit

Eat the red food, avoid the walls, and do not run into your own tail. The snake gets a little faster each time it eats.
