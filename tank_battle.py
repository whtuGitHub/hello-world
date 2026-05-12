"""Classic Tank Battle game implemented with Python's standard tkinter library.

Run with:
    python3 tank_battle.py
"""

from __future__ import annotations

import random
import tkinter as tk
from dataclasses import dataclass
from enum import Enum
from tkinter import messagebox


CELL_SIZE = 24
GRID_WIDTH = 26
GRID_HEIGHT = 20
CANVAS_WIDTH = GRID_WIDTH * CELL_SIZE
CANVAS_HEIGHT = GRID_HEIGHT * CELL_SIZE
TICK_MS = 45
PLAYER_MOVE_COOLDOWN = 3
ENEMY_MOVE_COOLDOWN = 10
PLAYER_BULLET_COOLDOWN = 9
MAX_ENEMIES_ON_FIELD = 4
TOTAL_ENEMIES = 18
PLAYER_LIVES = 3


class Tile(Enum):
    """Board tile types."""

    EMPTY = 0
    BRICK = 1
    STEEL = 2
    BASE = 3


class Direction(Enum):
    """Cardinal movement and firing directions."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def vector(self) -> tuple[int, int]:
        return self.value


@dataclass(frozen=True)
class Point:
    """A coordinate on the game grid."""

    x: int
    y: int

    def moved(self, direction: Direction, distance: int = 1) -> "Point":
        dx, dy = direction.vector
        return Point(self.x + dx * distance, self.y + dy * distance)


@dataclass
class Tank:
    """A player or enemy tank."""

    position: Point
    direction: Direction
    color: str
    is_player: bool = False
    move_counter: int = 0
    fire_counter: int = 0


@dataclass
class Bullet:
    """A bullet traveling across the grid."""

    position: Point
    direction: Direction
    owner: str


class TankBattleGame:
    """Main controller for a tkinter Tank Battle game."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Tank Battle - Python")
        self.root.resizable(False, False)

        self.score_var = tk.StringVar()
        self.status_var = tk.StringVar()

        header = tk.Frame(self.root, padx=10, pady=8)
        header.pack(fill=tk.X)
        tk.Label(header, textvariable=self.score_var, font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        tk.Label(header, textvariable=self.status_var, font=("Arial", 10)).pack(side=tk.RIGHT)

        self.canvas = tk.Canvas(
            self.root,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg="#0f172a",
            highlightthickness=0,
        )
        self.canvas.pack(padx=10, pady=(0, 10))

        self.board: list[list[Tile]] = []
        self.player = Tank(Point(GRID_WIDTH // 2 - 1, GRID_HEIGHT - 2), Direction.UP, "#22c55e", True)
        self.enemies: list[Tank] = []
        self.bullets: list[Bullet] = []
        self.keys_pressed: set[str] = set()
        self.score = 0
        self.lives = PLAYER_LIVES
        self.enemies_spawned = 0
        self.running = False
        self.paused = False
        self.after_id: str | None = None

        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.reset_game()

    def reset_game(self) -> None:
        """Reset the whole match and begin a new game."""
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.board = self.create_board()
        self.player = Tank(Point(GRID_WIDTH // 2 - 1, GRID_HEIGHT - 2), Direction.UP, "#22c55e", True)
        self.enemies = []
        self.bullets = []
        self.keys_pressed = set()
        self.score = 0
        self.lives = PLAYER_LIVES
        self.enemies_spawned = 0
        self.running = True
        self.paused = False
        self.update_labels()
        self.draw()
        self.schedule_next_tick()

    def create_board(self) -> list[list[Tile]]:
        """Create a Battle City-inspired arena with bricks, steel, and a base."""
        board = [[Tile.EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

        brick_columns = (3, 4, 8, 9, 13, 14, 18, 19, 22)
        for x in brick_columns:
            for y in range(3, GRID_HEIGHT - 4):
                if y % 4 != 1:
                    board[y][x] = Tile.BRICK

        for x, y in ((6, 6), (7, 6), (18, 6), (19, 6), (11, 10), (14, 10), (6, 14), (19, 14)):
            board[y][x] = Tile.STEEL

        base = Point(GRID_WIDTH // 2, GRID_HEIGHT - 1)
        board[base.y][base.x] = Tile.BASE
        for point in (Point(base.x - 1, base.y), Point(base.x + 1, base.y), Point(base.x - 1, base.y - 1), Point(base.x, base.y - 1), Point(base.x + 1, base.y - 1)):
            board[point.y][point.x] = Tile.BRICK

        safe_zones = [
            Point(GRID_WIDTH // 2 - 1, GRID_HEIGHT - 2),
            Point(GRID_WIDTH // 2 - 1, GRID_HEIGHT - 1),
            Point(1, 1),
            Point(GRID_WIDTH // 2, 1),
            Point(GRID_WIDTH - 2, 1),
        ]
        for point in safe_zones:
            board[point.y][point.x] = Tile.EMPTY
        return board

    def on_key_press(self, event: tk.Event) -> None:
        """Remember pressed keys and handle one-shot controls."""
        key = event.keysym.lower()
        self.keys_pressed.add(key)
        if key == "space":
            self.player_fire()
        elif key == "p":
            self.toggle_pause()
        elif key == "r":
            self.reset_game()
        elif key == "escape":
            self.root.destroy()

    def on_key_release(self, event: tk.Event) -> None:
        """Forget released keys."""
        self.keys_pressed.discard(event.keysym.lower())

    def toggle_pause(self) -> None:
        """Pause or resume the game loop."""
        if not self.running:
            return
        self.paused = not self.paused
        self.update_labels()
        if not self.paused:
            self.schedule_next_tick()
        self.draw()

    def schedule_next_tick(self) -> None:
        """Schedule the next frame."""
        if self.running and not self.paused:
            self.after_id = self.root.after(TICK_MS, self.tick)

    def tick(self) -> None:
        """Advance the game simulation."""
        self.after_id = None
        self.handle_player_movement()
        self.update_enemies()
        self.update_bullets()
        self.spawn_enemy_if_needed()
        self.update_labels()
        self.draw()
        if self.running:
            self.schedule_next_tick()

    def handle_player_movement(self) -> None:
        """Move the player according to currently pressed keys."""
        self.player.fire_counter = max(0, self.player.fire_counter - 1)
        self.player.move_counter = max(0, self.player.move_counter - 1)
        key_to_direction = [
            (("up", "w"), Direction.UP),
            (("down", "s"), Direction.DOWN),
            (("left", "a"), Direction.LEFT),
            (("right", "d"), Direction.RIGHT),
        ]
        for keys, direction in key_to_direction:
            if any(key in self.keys_pressed for key in keys):
                self.player.direction = direction
                if self.player.move_counter == 0:
                    self.try_move_tank(self.player, direction)
                    self.player.move_counter = PLAYER_MOVE_COOLDOWN
                return

    def player_fire(self) -> None:
        """Fire a player bullet if the reload timer is ready."""
        if self.running and not self.paused and self.player.fire_counter == 0:
            self.add_bullet(self.player, "player")
            self.player.fire_counter = PLAYER_BULLET_COOLDOWN

    def update_enemies(self) -> None:
        """Move enemy tanks and let them fire occasionally."""
        for enemy in list(self.enemies):
            enemy.move_counter = max(0, enemy.move_counter - 1)
            enemy.fire_counter = max(0, enemy.fire_counter - 1)
            if enemy.move_counter == 0:
                if random.random() < 0.28:
                    enemy.direction = random.choice(list(Direction))
                if not self.try_move_tank(enemy, enemy.direction):
                    enemy.direction = random.choice(list(Direction))
                enemy.move_counter = ENEMY_MOVE_COOLDOWN
            if enemy.fire_counter == 0 and random.random() < 0.08:
                self.add_bullet(enemy, "enemy")
                enemy.fire_counter = random.randint(12, 24)

    def update_bullets(self) -> None:
        """Move bullets, resolve collisions, and remove expired bullets."""
        next_bullets: list[Bullet] = []
        for bullet in self.bullets:
            new_position = bullet.position.moved(bullet.direction)
            if not self.in_bounds(new_position):
                continue
            if self.hit_tile(new_position, bullet):
                continue
            if self.hit_tank(new_position, bullet):
                continue
            if self.hit_bullet(new_position, bullet, next_bullets):
                continue
            bullet.position = new_position
            next_bullets.append(bullet)
        self.bullets = next_bullets

    def spawn_enemy_if_needed(self) -> None:
        """Spawn enemies at the top until the wave is cleared."""
        if self.enemies_spawned >= TOTAL_ENEMIES:
            if not self.enemies and not any(b.owner == "enemy" for b in self.bullets):
                self.win_game()
            return
        if len(self.enemies) >= MAX_ENEMIES_ON_FIELD:
            return

        spawn_points = [Point(1, 1), Point(GRID_WIDTH // 2, 1), Point(GRID_WIDTH - 2, 1)]
        random.shuffle(spawn_points)
        occupied = {self.player.position, *(enemy.position for enemy in self.enemies)}
        for point in spawn_points:
            if point not in occupied and self.is_walkable(point):
                self.enemies.append(Tank(point, Direction.DOWN, "#ef4444", False, ENEMY_MOVE_COOLDOWN, random.randint(8, 18)))
                self.enemies_spawned += 1
                break

    def try_move_tank(self, tank: Tank, direction: Direction) -> bool:
        """Move a tank one cell if the destination is open."""
        destination = tank.position.moved(direction)
        if not self.in_bounds(destination) or not self.is_walkable(destination):
            return False
        if destination == self.player.position and not tank.is_player:
            return False
        if any(enemy is not tank and enemy.position == destination for enemy in self.enemies):
            return False
        tank.position = destination
        return True

    def add_bullet(self, tank: Tank, owner: str) -> None:
        """Create a bullet just in front of a tank."""
        start = tank.position
        self.bullets.append(Bullet(start, tank.direction, owner))

    def hit_tile(self, point: Point, bullet: Bullet) -> bool:
        """Return whether a bullet hits terrain and apply tile effects."""
        tile = self.board[point.y][point.x]
        if tile == Tile.EMPTY:
            return False
        if tile == Tile.BRICK:
            self.board[point.y][point.x] = Tile.EMPTY
        elif tile == Tile.BASE:
            self.board[point.y][point.x] = Tile.EMPTY
            self.end_game("基地被摧毁！")
        return True

    def hit_tank(self, point: Point, bullet: Bullet) -> bool:
        """Return whether a bullet hits a tank and apply damage."""
        if bullet.owner == "enemy" and point == self.player.position:
            self.lives -= 1
            if self.lives <= 0:
                self.end_game("你的坦克被击毁！")
            else:
                self.player.position = Point(GRID_WIDTH // 2 - 1, GRID_HEIGHT - 2)
                self.player.direction = Direction.UP
            return True

        if bullet.owner == "player":
            for enemy in list(self.enemies):
                if enemy.position == point:
                    self.enemies.remove(enemy)
                    self.score += 100
                    return True
        return False

    def hit_bullet(self, point: Point, bullet: Bullet, next_bullets: list[Bullet]) -> bool:
        """Cancel bullets that collide head-on or cross into each other."""
        for existing in list(next_bullets):
            if existing.position == point and existing.owner != bullet.owner:
                next_bullets.remove(existing)
                return True
        return False

    def in_bounds(self, point: Point) -> bool:
        """Return whether a point is inside the arena."""
        return 0 <= point.x < GRID_WIDTH and 0 <= point.y < GRID_HEIGHT

    def is_walkable(self, point: Point) -> bool:
        """Return whether tanks can occupy a point."""
        return self.board[point.y][point.x] == Tile.EMPTY

    def draw(self) -> None:
        """Render the board, tanks, bullets, and overlays."""
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_tiles()
        self.draw_tank(self.player)
        for enemy in self.enemies:
            self.draw_tank(enemy)
        for bullet in self.bullets:
            self.draw_bullet(bullet)
        if self.paused:
            self.draw_center_text("Paused", "按 P 继续游戏")

    def draw_grid(self) -> None:
        """Draw subtle grid lines."""
        for x in range(0, CANVAS_WIDTH, CELL_SIZE):
            self.canvas.create_line(x, 0, x, CANVAS_HEIGHT, fill="#1e293b")
        for y in range(0, CANVAS_HEIGHT, CELL_SIZE):
            self.canvas.create_line(0, y, CANVAS_WIDTH, y, fill="#1e293b")

    def draw_tiles(self) -> None:
        """Draw bricks, steel blocks, and the base."""
        colors = {
            Tile.BRICK: ("#b45309", "#fed7aa"),
            Tile.STEEL: ("#64748b", "#cbd5e1"),
            Tile.BASE: ("#facc15", "#fef08a"),
        }
        for y, row in enumerate(self.board):
            for x, tile in enumerate(row):
                if tile == Tile.EMPTY:
                    continue
                fill, outline = colors[tile]
                self.draw_cell(Point(x, y), fill, outline)
                if tile == Tile.BASE:
                    self.canvas.create_text(
                        x * CELL_SIZE + CELL_SIZE // 2,
                        y * CELL_SIZE + CELL_SIZE // 2,
                        text="★",
                        fill="#78350f",
                        font=("Arial", 14, "bold"),
                    )

    def draw_tank(self, tank: Tank) -> None:
        """Draw a tank as a body plus cannon."""
        x = tank.position.x * CELL_SIZE
        y = tank.position.y * CELL_SIZE
        pad = 3
        self.canvas.create_rectangle(x + pad, y + pad, x + CELL_SIZE - pad, y + CELL_SIZE - pad, fill=tank.color, outline="#f8fafc", width=2)
        self.canvas.create_oval(x + 7, y + 7, x + CELL_SIZE - 7, y + CELL_SIZE - 7, fill="#0f172a", outline="")
        cx = x + CELL_SIZE // 2
        cy = y + CELL_SIZE // 2
        dx, dy = tank.direction.vector
        self.canvas.create_line(cx, cy, cx + dx * 12, cy + dy * 12, fill="#f8fafc", width=4, capstyle=tk.ROUND)

    def draw_bullet(self, bullet: Bullet) -> None:
        """Draw a bullet."""
        x = bullet.position.x * CELL_SIZE + CELL_SIZE // 2
        y = bullet.position.y * CELL_SIZE + CELL_SIZE // 2
        color = "#fde047" if bullet.owner == "player" else "#fb7185"
        self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill=color, outline="#f8fafc")

    def draw_cell(self, point: Point, fill: str, outline: str) -> None:
        """Draw one grid cell."""
        x1 = point.x * CELL_SIZE + 1
        y1 = point.y * CELL_SIZE + 1
        x2 = (point.x + 1) * CELL_SIZE - 1
        y2 = (point.y + 1) * CELL_SIZE - 1
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=2)

    def draw_center_text(self, title: str, subtitle: str) -> None:
        """Draw a centered overlay panel."""
        center_x = CANVAS_WIDTH // 2
        center_y = CANVAS_HEIGHT // 2
        self.canvas.create_rectangle(center_x - 170, center_y - 60, center_x + 170, center_y + 60, fill="#020617", outline="#f8fafc", width=2)
        self.canvas.create_text(center_x, center_y - 16, text=title, fill="#f8fafc", font=("Arial", 25, "bold"))
        self.canvas.create_text(center_x, center_y + 24, text=subtitle, fill="#cbd5e1", font=("Arial", 12))

    def update_labels(self) -> None:
        """Refresh score and help text."""
        remaining = TOTAL_ENEMIES - self.enemies_spawned + len(self.enemies)
        self.score_var.set(f"Score: {self.score} | Lives: {self.lives} | Enemies: {remaining}")
        if self.paused:
            self.status_var.set("Paused | P: 继续 | R: 重开 | Esc: 退出")
        else:
            self.status_var.set("方向键/WASD: 移动 | Space: 开火 | P: 暂停 | R: 重开")

    def end_game(self, reason: str) -> None:
        """Stop the match and offer to restart."""
        if not self.running:
            return
        self.running = False
        self.draw()
        self.draw_center_text("Game Over", f"{reason} 得分: {self.score} | 按 R 重开")
        messagebox.showinfo("Game Over", f"{reason}\n得分: {self.score}\n按 R 开始新一局。")

    def win_game(self) -> None:
        """Handle clearing all enemy tanks."""
        if not self.running:
            return
        self.running = False
        self.draw()
        self.draw_center_text("You Win!", f"全部敌人已清除！得分: {self.score}")
        messagebox.showinfo("You Win!", f"胜利！最终得分: {self.score}")

    def run(self) -> None:
        """Start the tkinter event loop."""
        self.root.mainloop()


if __name__ == "__main__":
    TankBattleGame().run()
