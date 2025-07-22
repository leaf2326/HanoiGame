from utils import *
from effects import Sparkle, Ripple, MoveAnim
import random

class HanoiGame:
    def __init__(self):
        pyxel.init(SCREEN_W, SCREEN_H)
        pyxel.mouse(True)
        self.disk_options = list(range(3, 9))
        self.disk_index = self.disk_options.index(4)
        self.setup_sound()
        self.reset()
        pyxel.run(self.update, self.draw)

    def setup_sound(self):
        pyxel.load("bgm.pyxres")
        self.bgm_on = True
        pyxel.playm(BGM, loop=True)
        pyxel.sound(SND_SUCC).set("c3e3g3c4", "p", "7", "n", 15)
        pyxel.sound(SND_FAIL).set("f3a3d4", "p", "6", "n", 10)
        pyxel.sound(SND_CLEAR).set("g3c4e4g4", "t", "6", "n", 15)
       

    def reset(self):
        self.num_disks = self.disk_options[self.disk_index]
        spacing = SCREEN_W // 5
        self.POLE_X = [spacing, SCREEN_W // 2, SCREEN_W - spacing]
        self.POLE_Y = 180
        self.poles = [list(range(self.num_disks, 0, -1)), [], []]
        self.selected = None
        self.dragging = False
        self.drag_offset_y = 0
        self.invalid_pole = None
        self.hover_invalid_pole = None
        self.sparkles = []
        self.ripples = []
        self.anim = None
        self.auto_moves = []
        self.move_count = 0
        self.min_moves = 2 ** self.num_disks - 1
        self.game_clear = False
        self.clear_timer = 0
        self.invalid_text_timer = 0

    def build_moves(self, n, src, dst, aux):
        if n == 0:
            return
        self.build_moves(n - 1, src, aux, dst)
        self.auto_moves.append((src, dst))
        self.build_moves(n - 1, aux, dst, src)

    def start_auto_solve(self):
        self.auto_moves = []
        self.build_moves(self.num_disks, 0, 2, 1)
        self.anim = None
        self.selected = None
        self.poles = [list(range(self.num_disks, 0, -1)), [], []]
        self.move_count = 0
        self.game_clear = False

    def get_hover_pole(self, mx):
        for i, px in enumerate(self.POLE_X):
            if px - 30 <= mx <= px + 30:
                return i
        return None

    def is_interactive(self, mx, my):
        if self.in_button(mx, my, 8, 8, 32, 8):
            return True
        if self.in_button(mx, my, 48, 8, 32, 8):
            return True
        if self.in_button(mx, my, 88, 8, 12, 8):
            return True
        if self.in_button(mx, my, 104, 8, 12, 8):
            return True
        if self.in_button(mx, my, 128, 8, 32, 8):
            return True
        for i, pole in enumerate(self.poles):
            if not pole:
                continue
            px = self.POLE_X[i]
            top = pole[-1]
            w = top * 10
            x1 = px - w // 2
            x2 = px + w // 2
            y = self.POLE_Y - DISK_HEIGHT * len(pole)
            if x1 <= mx <= x2 and y <= my <= y + DISK_HEIGHT:
                return True
        return False

    def in_button(self, mx, my, x, y, w, h):
        return x <= mx <= x + w and y <= my <= y + h

    def draw_text_centered(self, text, y, col=0, dx=0):
        x = SCREEN_W // 2 - len(text) * 2
        pyxel.text(x+dx, y, text, col)

    def update(self):
        mx, my = pyxel.mouse_x, pyxel.mouse_y

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            color = 10 if self.is_interactive(mx, my) else 1
            t = 10 if self.is_interactive(mx, my) else 7
            self.ripples.append(Ripple(mx, my, color, t))

        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            self.sparkles.append(Sparkle(mx, my, 10))

        self.sparkles = [s for s in self.sparkles if s.update() or s.t > 0]
        self.ripples = [r for r in self.ripples if r.update() or r.t > 0]

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.in_button(mx, my, 8, 8, 32, 8):
                self.reset()
                return
            if self.in_button(mx, my, 48, 8, 32, 8):
                self.start_auto_solve()
                return
            if self.in_button(mx, my, 88, 8, 12, 8) and self.disk_index < len(self.disk_options) - 1:
                self.disk_index += 1
                self.reset()
                return
            if self.in_button(mx, my, 104, 8, 12, 8) and self.disk_index > 0:
                self.disk_index -= 1
                self.reset()
                return
            if self.in_button(mx, my, 128, 8, 32, 8):
                self.bgm_on = not self.bgm_on
                if self.bgm_on:
                    pyxel.playm(BGM, loop=True)
                else:
                    pyxel.stop(0)
                    pyxel.stop(1)
                    pyxel.stop(2)
                return


        if self.anim:
            if self.anim.update():
                self.poles[self.anim.to_pole].append(self.anim.disk)
                self.anim = None
                pyxel.play(SE_CH, SND_SUCC)
            return

        if self.auto_moves and not self.anim:
            from_pole, to_pole = self.auto_moves.pop(0)
            if self.poles[from_pole]:
                disk = self.poles[from_pole].pop()
                h_from = len(self.poles[from_pole]) + 1
                h_to = len(self.poles[to_pole]) + 1
                anim_frames = get_anim_frames(self.num_disks)
                self.anim = MoveAnim(disk, from_pole, to_pole, h_from, h_to, self.POLE_X, self.POLE_Y, anim_frames)
                self.move_count += 1

        # Drag&drop
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            for i, pole in enumerate(self.poles):
                if not pole:
                    continue
                px = self.POLE_X[i]
                top = pole[-1]
                w = top * 10
                x1 = px - w // 2
                x2 = px + w // 2
                y = self.POLE_Y - DISK_HEIGHT * len(pole)
                if x1 <= mx <= x2 and y <= my <= y + DISK_HEIGHT:
                    self.selected = (i, top)
                    self.dragging = True
                    self.drag_offset_y = my - y
                    return

        if self.dragging:
            hover = self.get_hover_pole(mx)
            if hover is not None:
                from_pole, disk = self.selected
                top = self.poles[hover][-1] if self.poles[hover] else 99
                self.hover_invalid_pole = hover if top < disk else None

            if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                self.dragging = False
                to_pole = self.get_hover_pole(mx)
                if to_pole is not None:
                    from_pole, disk = self.selected
                    if not self.poles[to_pole] or self.poles[to_pole][-1] > disk:
                        self.poles[from_pole].pop()
                        self.poles[to_pole].append(disk)
                        self.move_count += 1
                        pyxel.play(SE_CH, SND_SUCC)
                    else:
                        if to_pole != from_pole:
                            self.invalid_pole = to_pole
                            self.invalid_text_timer = 60
                            pyxel.play(SE_CH, SND_FAIL)
                self.selected = None

        if self.invalid_pole and pyxel.frame_count % 30 == 0:
            self.invalid_pole = None

        if not self.auto_moves and not self.anim and len(self.poles[2]) == self.num_disks and not self.game_clear:
            self.game_clear = True
            self.clear_timer = 120
            pyxel.play(SE_CH, SND_CLEAR)

        self.invalid_text_timer = max(0, self.invalid_text_timer - 1)
        self.clear_timer = max(0, self.clear_timer - 1)

    def draw(self):
        pyxel.cls(7)
        self.draw_ui()
        self.draw_poles()
        self.draw_disks()
        if self.anim:
            self.anim.draw()
        self.draw_effects()
        if self.invalid_text_timer > 0:
            self.draw_text_centered("Can't place larger disk!", SCREEN_H - 16, 8)
        if self.game_clear and self.clear_timer > 0:
            self.draw_clear_effect()

    def draw_ui(self):
        pyxel.rect(0, 0, SCREEN_W, 24, 13)
        pyxel.text(10, 2, "Hanoi Tower", 0)
        pyxel.rect(8, 8, 32, 8, 8)
        pyxel.text(12, 9, "Reset", 7)
        pyxel.rect(48, 8, 32, 8, 12)
        pyxel.text(52, 9, "Auto", 7)
        pyxel.rect(88, 8, 12, 8, 5)
        pyxel.text(90, 9, "+", 7)
        pyxel.rect(104, 8, 12, 8, 5)
        pyxel.text(106, 9, "-", 7)
        pyxel.text(SCREEN_W - 64, 4, f"Step: {self.move_count}", 0)
        pyxel.text(SCREEN_W - 64, 12, f"Min: {self.min_moves}", 0)
        pyxel.rect(128, 8, 32, 8, 3)
        pyxel.text(132, 9, "BGM", 7 if self.bgm_on else 5)


    def draw_poles(self):
        for i, px in enumerate(self.POLE_X):
            pyxel.rect(px - POLE_W // 2, self.POLE_Y - POLE_H, POLE_W, POLE_H, 5)
            if self.invalid_pole == i or self.hover_invalid_pole == i:
                pyxel.text(px - 3, self.POLE_Y - POLE_H // 2, "×", 8)

    def draw_disks(self):
        for i, pole in enumerate(self.poles):
            px = self.POLE_X[i]
            for j, disk in enumerate(pole):
                if self.anim and self.anim.disk == disk and self.anim.from_pole == i:
                    continue
                if self.dragging and self.selected and self.selected == (i, disk):
                    continue
                y = self.POLE_Y - DISK_HEIGHT * (j + 1)
                w = disk * 10
                c = 7 + (disk % 10)
                pyxel.rect(px - w // 2, y, w, DISK_HEIGHT, c)
                pyxel.rectb(px - w // 2, y, w, DISK_HEIGHT, 1)

        if self.dragging and self.selected:
            _, disk = self.selected
            w = disk * 10
            y = pyxel.mouse_y - self.drag_offset_y
            c = 7 + (disk % 10)
            pyxel.rect(pyxel.mouse_x - w // 2, y, w, DISK_HEIGHT, c)
            pyxel.rectb(pyxel.mouse_x - w // 2, y, w, DISK_HEIGHT, 1)

        if self.move_count == 0 and not self.auto_moves and not self.anim:
            for j, disk in enumerate(reversed(range(1, self.num_disks + 1))):
                y = self.POLE_Y - DISK_HEIGHT * (j + 1)
                w = disk * 10
                c = 7 + (disk % 10)
                pyxel.dither(0.5)
                pyxel.rect(self.POLE_X[2] - w // 2, y, w, DISK_HEIGHT, c)
                pyxel.dither(1.0)

            # 矢印
            x0, y0 = self.POLE_X[0], self.POLE_Y - POLE_H - 10
            x1, y1 = self.POLE_X[2], self.POLE_Y - POLE_H - 10
            pyxel.line(x0, y0, x1, y1, 8)
            pyxel.tri(x1, y1, x1 - 5, y1 - 3, x1 - 5, y1 + 3, 8)

    def draw_effects(self):
        for s in self.sparkles:
            s.draw()
        for r in self.ripples:
            r.draw()

    def draw_clear_effect(self):
        t = pyxel.frame_count
        msg, msg2 = "CLEAR!", "CONGRATULATIONS!"
        color = t % 16 + 1
        if t % 30 < 5:
            pyxel.cls(7)
        elif t % 30 < 10:
            pyxel.cls(6)
        elif t % 30 < 15:
            pyxel.cls(10)
        else:
            pyxel.cls(7)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                self.draw_text_centered(msg, 100 + dy, 0, dx=dx)
                self.draw_text_centered(msg2, 120 + dy, 0, dx=dx)
        self.draw_text_centered(msg, 100, color)
        self.draw_text_centered(msg2, 120, 12)
        for i, pole in enumerate(self.poles):
            px = self.POLE_X[i]
            for j, disk in enumerate(pole):
                y = self.POLE_Y - DISK_HEIGHT * (j + 1)
                w = disk * 10
                c = (disk + t) % 16
                pyxel.rect(px - w // 2, y, w, DISK_HEIGHT, c)
        if t % 2 == 0:
            for _ in range(3):
                self.sparkles.append(Sparkle(random.randint(0, SCREEN_W), random.randint(30, SCREEN_H), random.randint(1, 15)))
