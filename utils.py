import pyxel

SCREEN_W = 256
SCREEN_H = 256
DISK_HEIGHT = 8
POLE_W = 10
POLE_H = 80
SND_SUCC = 60
SND_FAIL = 61
SND_CLEAR = 62
SE_CH = 3
BGM = 0

def get_anim_frames(num_disks):
    min_frames = 2
    max_frames = 12
    return max(min_frames, max_frames - (num_disks - 3))  # 3→12, ..., 7→8