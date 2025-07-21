import pyxel
import random
from utils import DISK_HEIGHT

class Sparkle:
    def __init__(self, x, y, color):
        self.x = x + random.randint(-2, 2)
        self.y = y + random.randint(-2, 2)
        self.t = 10
        self.color = color

    def update(self):
        self.t -= 1
        return self.t > 0

    def draw(self):
        if self.t > 0:
            pyxel.pset(self.x, self.y, self.color)

class Ripple:
    def __init__(self, x, y, color, t=10):
        self.x = x
        self.y = y
        self.r = 0
        self.t = t
        self.color = color

    def update(self):
        self.r += 2
        self.t -= 1
        return self.t > 0

    def draw(self):
        if self.t > 0:
            pyxel.circb(self.x, self.y, self.r, self.color)

class MoveAnim:
    def __init__(self, disk, from_pole, to_pole, height_from, height_to, pole_x, pole_y, anim_frames):
        self.disk = disk
        self.from_pole = from_pole
        self.to_pole = to_pole
        self.x0 = pole_x[from_pole]
        self.x1 = pole_x[to_pole]
        self.y0 = pole_y - DISK_HEIGHT * height_from
        self.y1 = pole_y - DISK_HEIGHT * height_to
        self.frame = 0
        self.max_frame = anim_frames

    def update(self):
        self.frame += 1
        return self.frame >= self.max_frame

    def draw(self):
        t = self.frame / self.max_frame
        ease = t * t * (3 - 2 * t)
        x = int(self.x0 + (self.x1 - self.x0) * ease)
        y = int(self.y0 + (self.y1 - self.y0) * (1 - (2 * t - 1) ** 2))
        w = self.disk * 10
        c = 7 + (self.disk % 10)
        pyxel.rect(x - w // 2, y, w, DISK_HEIGHT, c)
        pyxel.rectb(x - w // 2, y, w, DISK_HEIGHT, 1)
