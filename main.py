from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.utils import get_color_from_hex
import random
import math

# Snake 3D-style: shaded spheres, glossy highlights and a perspective grid.
# Built with Kivy so it can later be packaged as an Android APK.

Window.clearcolor = get_color_from_hex("#08111f")
GRID_W, GRID_H = 22, 28


class SnakeBoard(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.snake = []
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = (12, 14)
        self.score = 0
        self.running = True
        self.paused = False
        self.game_over = False
        self.on_score = lambda score: None
        self.on_state = lambda text: None
        self.touch_start = None
        self.reset()
        Clock.schedule_interval(self.update, 0.13)
        self.bind(pos=self.redraw, size=self.redraw)

    def reset(self):
        cx, cy = GRID_W // 2, GRID_H // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.running = True
        self.paused = False
        self.game_over = False
        self.spawn_food()
        self.on_score(self.score)
        self.on_state("Собирай яблоки!")
        self.redraw()

    def spawn_food(self):
        free = [(x, y) for x in range(GRID_W) for y in range(GRID_H)
                if (x, y) not in self.snake]
        self.food = random.choice(free) if free else None

    def steer(self, d):
        if d != (-self.direction[0], -self.direction[1]):
            self.next_direction = d

    def update(self, dt):
        if not self.running or self.paused or self.game_over:
            return
        self.direction = self.next_direction
        hx, hy = self.snake[0]
        dx, dy = self.direction
        head = (hx + dx, hy + dy)
        ate = head == self.food
        body = self.snake if ate else self.snake[:-1]
        if head[0] < 0 or head[0] >= GRID_W or head[1] < 0 or head[1] >= GRID_H or head in body:
            self.game_over = True
            self.on_state("Игра окончена — нажми «Заново»")
            self.redraw()
            return
        self.snake.insert(0, head)
        if ate:
            self.score += 1
            self.on_score(self.score)
            self.spawn_food()
            if self.food is None:
                self.game_over = True
                self.on_state("Победа! Поле заполнено")
        else:
            self.snake.pop()
        self.redraw()

    def cell_metrics(self):
        # Fit the board while leaving a little margin.
        cell = min(self.width / GRID_W, self.height / GRID_H)
        bw, bh = cell * GRID_W, cell * GRID_H
        ox = self.x + (self.width - bw) / 2
        oy = self.y + (self.height - bh) / 2
        return cell, ox, oy

    def sphere(self, x, y, cell, ox, oy, kind="body", index=0):
        # Fake 3D sphere using layered circles and a small specular highlight.
        px = ox + x * cell + cell * 0.08
        py = oy + y * cell + cell * 0.08
        size = cell * 0.84
        if kind == "food":
            Color(0.20, 0.01, 0.03, 0.5)
            Ellipse(pos=(px + size * 0.06, py - size * 0.03), size=(size, size * 0.72))
            Color(1.0, 0.12, 0.20, 1)
            Ellipse(pos=(px, py), size=(size, size))
            Color(1.0, 0.34, 0.37, 1)
            Ellipse(pos=(px + size * 0.12, py + size * 0.17), size=(size * 0.64, size * 0.64))
            Color(1, 0.75, 0.73, 0.95)
            Ellipse(pos=(px + size * 0.20, py + size * 0.62), size=(size * 0.19, size * 0.13))
            Color(0.28, 0.90, 0.44, 1)
            Line(points=[px + size * 0.53, py + size * 0.87,
                         px + size * 0.59, py + size * 1.06], width=max(1, cell * 0.07))
            return

        if kind == "head":
            Color(0.02, 0.22, 0.13, 1)
            Ellipse(pos=(px - size * 0.02, py - size * 0.04), size=(size * 1.08, size * 1.08))
            Color(0.10, 0.92, 0.46, 1)
            Ellipse(pos=(px, py), size=(size, size))
            Color(0.34, 1.0, 0.60, 1)
            Ellipse(pos=(px + size * 0.10, py + size * 0.13), size=(size * 0.70, size * 0.70))
            Color(0.72, 1.0, 0.82, 0.95)
            Ellipse(pos=(px + size * 0.18, py + size * 0.67), size=(size * 0.20, size * 0.12))
            # Eyes placed toward the moving direction.
            Color(0.02, 0.07, 0.08, 1)
            dx, dy = self.direction
            for ex, ey in ([(0.68, 0.65), (0.68, 0.30)] if dx >= 0 else
                           ([(0.15, 0.65), (0.15, 0.30)] if dx < 0 else
                            ([(0.30, 0.70), (0.67, 0.70)] if dy > 0 else
                             [(0.30, 0.18), (0.67, 0.18)])):
                Ellipse(pos=(px + size * ex, py + size * ey), size=(size * 0.11, size * 0.11))
        else:
            shade = max(0.35, 0.94 - index * 0.012)
            Color(0.02, 0.22 * shade, 0.12 * shade, 1)
            Ellipse(pos=(px - size * 0.02, py - size * 0.04), size=(size * 1.08, size * 1.08))
            Color(0.08 * shade, 0.78 * shade, 0.38 * shade, 1)
            Ellipse(pos=(px, py), size=(size, size))
            Color(0.25 * shade, 0.98 * shade, 0.53 * shade, 1)
            Ellipse(pos=(px + size * 0.10, py + size * 0.16), size=(size * 0.68, size * 0.68))
            Color(0.65, 1, 0.76, 0.70)
            Ellipse(pos=(px + size * 0.18, py + size * 0.66), size=(size * 0.16, size * 0.10))

    def redraw(self, *args):
        self.canvas.clear()
        if self.width <= 0 or self.height <= 0:
            return
        cell, ox, oy = self.cell_metrics()
        bw, bh = cell * GRID_W, cell * GRID_H
        with self.canvas:
            # Board shadow and rounded dark board.
            Color(0.01, 0.03, 0.07, 1)
            RoundedRectangle(pos=(ox - 4, oy - 4), size=(bw + 8, bh + 8), radius=[dp(14)])
            Color(0.035, 0.075, 0.12, 1)
            RoundedRectangle(pos=(ox, oy), size=(bw, bh), radius=[dp(10)])
            # Fine perspective-like grid lines.
            Color(0.10, 0.19, 0.26, 0.42)
            for gx in range(GRID_W + 1):
                xx = ox + gx * cell
                Line(points=[xx, oy, xx, oy + bh], width=0.5)
            for gy in range(GRID_H + 1):
                yy = oy + gy * cell
                Line(points=[ox, yy, ox + bw, yy], width=0.5)
            # Soft floor glow under the snake.
            Color(0.03, 0.35, 0.18, 0.12)
            Ellipse(pos=(ox + bw * 0.18, oy + bh * 0.25), size=(bw * 0.64, bh * 0.5))
            if self.food:
                self.sphere(self.food[0], self.food[1], cell, ox, oy, "food")
            for i, (sx, sy) in enumerate(reversed(self.snake)):
                # Draw tail-to-head so head sits on top.
                real_index = len(self.snake) - 1 - i
                self.sphere(sx, sy, cell, ox, oy,
                            "head" if real_index == 0 else "body", real_index)
            if self.paused or self.game_over:
                Color(0.015, 0.03, 0.06, 0.78)
                RoundedRectangle(pos=(ox + bw * 0.08, oy + bh * 0.42),
                                 size=(bw * 0.84, bh * 0.16), radius=[dp(12)])

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.touch_start = touch.pos
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.touch_start:
            sx, sy = self.touch_start
            dx, dy = touch.x - sx, touch.y - sy
            self.touch_start = None
            if max(abs(dx), abs(dy)) > dp(18):
                if abs(dx) > abs(dy):
                    self.steer((1, 0) if dx > 0 else (-1, 0))
                else:
                    self.steer((0, 1) if dy > 0 else (0, -1))
                return True
        return super().on_touch_up(touch)


class SnakeApp(App):
    def build(self):
        self.title = "3D Snake"
        root = BoxLayout(orientation="vertical", padding=[dp(12), dp(12), dp(12), dp(10)], spacing=dp(8))

        header = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(8))
        titlebox = BoxLayout(orientation="vertical", spacing=dp(1))
        titlebox.add_widget(Label(text="[b]SNAKE 3D[/b]", markup=True, font_size="23sp",
                                  color=get_color_from_hex("#eafbf2"), halign="left",
                                  valign="middle", size_hint_y=0.66))
        titlebox.add_widget(Label(text="NEON ARCADE", font_size="10sp",
                                  color=get_color_from_hex("#66d99b"), halign="left",
                                  valign="top", size_hint_y=0.34))
        header.add_widget(titlebox)
        self.score_label = Label(text="SCORE  0", bold=True, font_size="18sp",
                                 color=get_color_from_hex("#b7ffd0"), size_hint_x=0.55)
        header.add_widget(self.score_label)
        root.add_widget(header)

        self.board = SnakeBoard()
        self.board.on_score = self.set_score
        self.board.on_state = self.set_state
        root.add_widget(self.board)

        self.state_label = Label(text="Собирай яблоки!", size_hint_y=None, height=dp(26),
                                 color=get_color_from_hex("#a5b9c8"), font_size="13sp")
        root.add_widget(self.state_label)

        controls = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(154), spacing=dp(5))
        row1 = BoxLayout(spacing=dp(5))
        row1.add_widget(Widget())
        row1.add_widget(self.make_button("▲", lambda *_: self.board.steer((0, 1))))
        row1.add_widget(Widget())
        controls.add_widget(row1)
        row2 = BoxLayout(spacing=dp(5))
        row2.add_widget(self.make_button("◀", lambda *_: self.board.steer((-1, 0))))
        row2.add_widget(self.make_button("▼", lambda *_: self.board.steer((0, -1))))
        row2.add_widget(self.make_button("▶", lambda *_: self.board.steer((1, 0))))
        controls.add_widget(row2)
        row3 = BoxLayout(spacing=dp(7))
        self.pause_button = self.make_button("Пауза", self.toggle_pause)
        row3.add_widget(self.pause_button)
        row3.add_widget(self.make_button("Заново", self.restart))
        controls.add_widget(row3)
        root.add_widget(controls)
        return root

    def make_button(self, text, callback):
        btn = Button(text=text, font_size="20sp" if text in ("▲", "▼", "◀", "▶") else "15sp",
                     bold=True, background_normal="", background_down="",
                     background_color=get_color_from_hex("#163a35"),
                     color=get_color_from_hex("#e8fff0"))
        btn.bind(on_release=callback)
        return btn

    def set_score(self, score):
        if hasattr(self, "score_label"):
            self.score_label.text = f"SCORE  {score}"

    def set_state(self, text):
        if hasattr(self, "state_label"):
            self.state_label.text = text

    def toggle_pause(self, *_):
        if self.board.game_over:
            return
        self.board.paused = not self.board.paused
        self.pause_button.text = "Продолжить" if self.board.paused else "Пауза"
        self.set_state("Пауза" if self.board.paused else "Собирай яблоки!")
        self.board.redraw()

    def restart(self, *_):
        self.board.reset()
        self.pause_button.text = "Пауза"

    def on_pause(self):
        return True


if __name__ == "__main__":
    SnakeApp().run()
