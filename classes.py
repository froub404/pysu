"""
Osu!mania but in pygame

Author: fran :^)
Version: 4-27-2026
"""
# so i am an idiot.
import pygame
from pathlib import Path
pygame.mixer.init()

def get_meta_item(file, heading, name):
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_diff = False

    for line in lines:
        line = line.strip()

        if line == heading:
            in_diff = True
            continue

        if in_diff:
            if line.startswith("["):
                break

            if line.startswith(name):
                try:
                    return float(line.split(":")[1])
                except ValueError:
                    return line.split(":")[1]

    return None

def get_bpm(file):
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_timing = False

    for line in lines:
        line = line.strip()

        if line == "[TimingPoints]":
            in_timing = True
            continue

        if in_timing:
            if line.startswith("["):
                break

            meta = line.split(",")

            if len(meta) < 7:
                continue

            beat_length = float(meta[1])
            uninherited = int(meta[6])

            if uninherited == 1:
                return 60000 / beat_length

    for line in lines:
        if line.strip() and not line.startswith("["):
            meta = line.split(",")
            if len(meta) > 1:
                try:
                    return 60000 / float(meta[1])
                except TypeError:
                    continue

    return None

def load_meta(file, notes):
    # This would kill a victorian child
    # length = meta.split("[HitObjects]\n")[1].splitlines()[-1].split(",")[5].split(":")[0].strip()

    length = max(note.end if note.end else note.time for note in notes)
    bpm = get_bpm(file)
    difficulty = get_meta_item(file, "[Difficulty]", "OverallDifficulty")
    columns = get_meta_item(file, "[Difficulty]", "CircleSize")
    author = get_meta_item(file, "[Metadata]", "Artist")
    title = get_meta_item(file, "[Metadata]", "Title")

    return {'length': length, 'bpm': bpm,
            'difficulty': difficulty, 'columns': columns,
            'author': author, 'title': title}

def load_notes(file, col_count=4, col_size=512):
    with open(file, 'r', encoding="utf-8") as f:
        beatmap = f.read().split("[HitObjects]\n")[1].splitlines()

    notes = []

    # 200, 88, 88072, 1, 0, blah blah blah
    # x, y, time, type, hit sound, object params
    for line in beatmap:
        meta = [line.strip().casefold() for line in line.split(",")]

        x = int(meta[0])
        time = int(meta[2])
        typ_raw = int(meta[3])

        col = int(x / (col_size / col_count))

        is_hold = typ_raw & 128

        if is_hold:
            end_time = int(meta[5].split(":")[0])
            notes.append(Note(col, time, 128, end_time))
        else:
            notes.append(Note(col, time, 1))

    return sorted(notes, key=lambda note: note.time)

class Note:
    def __init__(self, col, time, typ, end=None):
        self.col = col
        self.time = time
        self.typ = typ  # 1 = tap, 128 = hold
        self.end = end

        self.holding = False

    def get_y(self, current_time, scroll_speed, upscroll=False):
        y = (self.time - current_time) * scroll_speed
        return y if upscroll else -y

    def get_end_y(self, current_time, scroll_speed, upscroll=False):
        if self.end:
            y = (self.end - current_time) * scroll_speed
            return y if upscroll else -y
        return 0

    def is_hold(self):
        return self.end is not None
    
def load_songs():
    song_list = {} # basically Song Title (can be the same song, different difficulty) : [Osu file, Mp3]

    for song_folder in Path('songs').iterdir():
        if not song_folder.is_dir():
            continue
        name = song_folder.stem
        audio = next(song_folder.glob('*.mp3'), None)
        img = next(song_folder.glob('*.png'), None)
        if not img: img = next(song_folder.glob('*.jpg'), None) # fixme I kind of dont need, you can just change jpg/jpeg --> png in file explorer :^
        for file in song_folder.glob('*.osu'):
            osu = f"songs/{song_folder.name}/{file.name}"
            difficulty = "[" + file.stem.split("[")[1].split("]")[0] + "]"
            try:
                song_list[name + " " + difficulty] = [osu, audio, img]
            except Exception as e:
                print(f"Couldn't load {name}: {e}")

    return song_list

class Song:
    def __init__(self, file, mp3, img=None):
        self.playing = False # idk
        self.beatmap = load_notes(file)
        self.song_mp3 = mp3
        self.album_cover = img

        info = load_meta(file, self.beatmap)
        self.length = info['length']
        self.bpm = info['bpm']
        self.difficulty = info['difficulty']
        self.columns = info['columns']
        self.author = info['author']
        self.title = info['title']

        self.note_amount = len(self.beatmap)

    def play(self):
        self.playing = True
        pygame.mixer.music.load(self.song_mp3)
        pygame.mixer.music.play()
        return pygame.time.get_ticks()
    
    def end(self):
        self.playing = False
        self.beatmap.clear()
        pygame.mixer.music.stop()

class Msg:
    def __init__(self, text, color):
        self.text = text
        self.color = color
        self.dx = 0
        self.dy = 0
        self.alpha = 255

    def update(self):
        # fixme Magic numbers. You better catch meeee
        self.dx += 3
        self.dy += 4
        self.alpha -= 10

class Player:
    def __init__(self):
        self.keybinds = [pygame.K_q, pygame.K_w, pygame.K_o, pygame.K_p]
        self.score = 0

        self.perfect = 0
        self.great = 0
        self.good = 0
        self.okay = 0
        self.bad = 0
        self.miss = 0

    def reset_stats(self):
        self.score = 0

        self.perfect = 0
        self.great = 0
        self.good = 0
        self.okay = 0
        self.bad = 0
        self.miss = 0

class Settings:
    def __init__(self, game):
        self.column_colors = (game.RED, game.BLUE, game.GREEN, game.YELLOW, game.ORANGE, game.PURPLE)
        self.scroll_size = 340
        self.note_size = 70
        self.up_scroll = False
        self.columns = 4
        self.scroll_rate = 0.84
        self.scroll_multiplier = 1 # Not exactly note speed but more like a zoom