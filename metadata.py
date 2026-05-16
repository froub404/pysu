from classes import Note
from pathlib import Path

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
                    return ''.join(line.split(":")[1:])

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

def load_songs():
    # i shouldve made this a list lwk
    song_list = [] # basically Song Title (can be the same song, different difficulty) : [Osu file, Mp3]

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
                song_list.append({
                    "title": name + " " + difficulty,
                    "osu": osu,
                    "audio": audio,
                    "img": img
                })
            except Exception as e:
                print(f"Couldn't load {name}: {e}")

    return song_list