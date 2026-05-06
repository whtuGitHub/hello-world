"""A simple Snake game implemented with Python's standard tkinter library."""

from __future__ import annotations

import random
import tkinter as tk
from dataclasses import dataclass
from enum import Enum
from tkinter import messagebox


CELL_SIZE = 24
GRID_WIDTH = 25
GRID_HEIGHT = 20
INITIAL_SPEED_MS = 130
MIN_SPEED_MS = 55
SPEED_STEP_MS = 3


class Direction(Enum):
    """Movement directions for the snake."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def is_opposite(self, other: "Direction") -> bool:
        return self.value[0] + other.value[0] == 0 and self.value[1] + other.value[1] == 0


@dataclass(frozen=True)
class Point:
    """A coordinate on the game grid."""

    x: int
    y: int

    def moved(self, direction: Direction) -> "Point":
        dx, dy = direction.value
        return Point(self.x + dx, self.y + dy)


class SnakeGame:
    """Main game controller for a tkinter Snake game."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Snake - Python")
        self.root.resizable(False, False)

        self.score_var = tk.StringVar()
        self.status_var = tk.StringVar()

        header = tk.Frame(self.root, padx=10, pady=8)
        header.pack(fill=tk.X)

        tk.Label(header, textvariable=self.score_var, font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        tk.Label(header, textvariable=self.status_var, font=("Arial", 11)).pack(side=tk.RIGHT)

        self.canvas = tk.Canvas(
            self.root,
            width=GRID_WIDTH * CELL_SIZE,
            height=GRID_HEIGHT * CELL_SIZE,
            bg="#111827",
            highlightthickness=0,
        )
        self.canvas.pack(padx=10, pady=(0, 10))

        self.direction = Direction.RIGHT
        self.pending_direction = Direction.RIGHT
        self.snake: list[Point] = []
        self.food = Point(0, 0)
        self.score = 0
        self.speed_ms = INITIAL_SPEED_MS
        self.running = False
        self.paused = False
        self.after_id: str | None = None

        self.root.bind("<KeyPress>", self.on_key_press)
        self.reset_game()

    def reset_game(self) -> None:
        """Reset state and start a new round."""
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.snake = [Point(start_x - offset, start_y) for offset in range(3)]
        self.direction = Direction.RIGHT
        self.pending_direction = Direction.RIGHT
        self.score = 0
        self.speed_ms = INITIAL_SPEED_MS
        self.running = True
        self.paused = False
        self.spawn_food()
        self.update_labels()
        self.draw()
        self.schedule_next_tick()

    def spawn_food(self) -> None:
        """Place food on a random empty grid cell."""
        occupied = set(self.snake)
        free_cells = [
            Point(x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if Point(x, y) not in occupied
        ]
        if not free_cells:
            self.win_game()
            return
        self.food = random.choice(free_cells)

    def on_key_press(self, event: tk.Event) -> None:
        """Handle keyboard controls."""
        key = event.keysym.lower()
        direction_keys = {
            "up": Direction.UP,
            "w": Direction.UP,
            "down": Direction.DOWN,
            "s": Direction.DOWN,
            "left": Direction.LEFT,
            "a": Direction.LEFT,
            "right": Direction.RIGHT,
            "d": Direction.RIGHT,
        }

        if key in direction_keys:
            next_direction = direction_keys[key]
            if not next_direction.is_opposite(self.direction):
                self.pending_direction = next_direction
        elif key == "space":
            self.toggle_pause()
        elif key == "r":
            self.reset_game()
        elif key == "escape":
            self.root.destroy()

    def toggle_pause(self) -> None:
        """Pause or resume the current round."""
        if not self.running:
            return
        self.paused = not self.paused
        self.update_labels()
        if not self.paused:
            self.schedule_next_tick()

    def schedule_next_tick(self) -> None:
        """Schedule the next game update."""
        if self.running and not self.paused:
            self.after_id = self.root.after(self.speed_ms, self.tick)

    def tick(self) -> None:
        """Advance the game by one step."""
        self.after_id = None
        self.direction = self.pending_direction
        new_head = self.snake[0].moved(self.direction)

        if self.is_collision(new_head):
            self.end_game()
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            self.speed_ms = max(MIN_SPEED_MS, self.speed_ms - SPEED_STEP_MS)
            self.spawn_food()
        else:
            self.snake.pop()

        self.update_labels()
        self.draw()
        self.schedule_next_tick()

    def is_collision(self, point: Point) -> bool:
        """Return whether a point hits a wall or the snake's body."""
        hits_wall = point.x < 0 or point.x >= GRID_WIDTH or point.y < 0 or point.y >= GRID_HEIGHT
        # Moving into the current tail position is legal because the tail
        # moves away on non-food turns. Food never spawns on the snake.
        hits_body = point in self.snake[:-1]
        return hits_wall or hits_body

    def draw(self) -> None:
        """Render the current game state."""
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_cell(self.food, "#ef4444", outline="#fecaca")

        for index, segment in enumerate(self.snake):
            color = "#22c55e" if index == 0 else "#16a34a"
            outline = "#bbf7d0" if index == 0 else "#86efac"
            self.draw_cell(segment, color, outline=outline)

        if self.paused:
            self.draw_center_text("Paused", "Press Space to continue")

    def draw_grid(self) -> None:
        """Draw subtle grid lines."""
        for x in range(0, GRID_WIDTH * CELL_SIZE, CELL_SIZE):
            self.canvas.create_line(x, 0, x, GRID_HEIGHT * CELL_SIZE, fill="#1f2937")
        for y in range(0, GRID_HEIGHT * CELL_SIZE, CELL_SIZE):
            self.canvas.create_line(0, y, GRID_WIDTH * CELL_SIZE, y, fill="#1f2937")

    def draw_cell(self, point: Point, fill: str, outline: str) -> None:
        """Draw a rounded-looking grid cell with padding."""
        padding = 2
        x1 = point.x * CELL_SIZE + padding
        y1 = point.y * CELL_SIZE + padding
        x2 = (point.x + 1) * CELL_SIZE - padding
        y2 = (point.y + 1) * CELL_SIZE - padding
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=2)

    def draw_center_text(self, title: str, subtitle: str) -> None:
        """Draw centered overlay text."""
        center_x = GRID_WIDTH * CELL_SIZE // 2
        center_y = GRID_HEIGHT * CELL_SIZE // 2
        self.canvas.create_rectangle(
            center_x - 150,
            center_y - 55,
            center_x + 150,
            center_y + 55,
            fill="#030712",
            outline="#f9fafb",
        )
        self.canvas.create_text(center_x, center_y - 14, text=title, fill="#f9fafb", font=("Arial", 24, "bold"))
        self.canvas.create_text(center_x, center_y + 22, text=subtitle, fill="#d1d5db", font=("Arial", 12))

    def update_labels(self) -> None:
        """Refresh score and help text."""
        self.score_var.set(f"Score: {self.score}")
        if self.paused:
            self.status_var.set("Paused | Space: resume | R: restart | Esc: quit")
        else:
            self.status_var.set("Move: arrows/WASD | Space: pause | R: restart")

    def end_game(self) -> None:
        """Stop the round and offer to restart."""
        self.running = False
        self.draw()
        self.draw_center_text("Game Over", f"Final score: {self.score} | Press R to restart")
        if messagebox.askyesno("Game Over", f"Your score: {self.score}\nPlay again?"):
            self.reset_game()

    def win_game(self) -> None:
        """Handle the rare case where the snake fills the board."""
        self.running = False
        self.draw()
        self.draw_center_text("You Win!", "The board is full. Press R to restart")
        messagebox.showinfo("You Win!", f"Perfect game! Your score: {self.score}")

    def run(self) -> None:
        """Start the tkinter event loop."""
        self.root.mainloop()


if __name__ == "__main__":
    SnakeGame().run()
