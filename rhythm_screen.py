"""
Osu!mania but in pygame
Kind of finished? In a way?

Author: fran :^)
Version: 5-3-2026
"""
# TODO i separated all the classes but still no settinngs....
import pygame
import string

import metadata
import classes
import settings
import visuals

class Game:
    def __init__(self):
        # regular pygame init
        pygame.init()
        pygame.mixer.init()
        self.song_list = metadata.load_songs() # Name + Diff : [Osu, Mp3] (paths)

        self.SCREEN_WIDTH = 720
        self.SCREEN_HEIGHT = 600
        self.CAPTION = "pygame!mania by fran :^)"
        pygame.display.set_caption(self.CAPTION)
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.FPS = 60
        self.running = True
        self.clock = pygame.time.Clock()

        # STAGE
        self.START = 0
        self.CHOOSING_SONG = 1
        self.PLAYING = 2
        self.FINISH = 3
        self.SETTINGS = 4
        self.STAGE = self.START

        self.FONT_RL = pygame.font.Font(None, 96)
        self.FONT_LG = pygame.font.Font(None, 64)
        self.FONT_MD = pygame.font.Font(None, 48)
        self.FONT_SM = pygame.font.Font(None, 32)
        self.FONT_RS = pygame.font.Font(None, 24)
        self.FONT_TN = pygame.font.Font(None, 18)

        # COLORS
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREY = (128, 128, 128)
        self.RED = (255, 0, 0)
        self.ORANGE = (255, 165, 0)
        self.BLUE = (0, 0, 255)
        self.GREEN = (0, 255, 0)
        self.YELLOW = (255, 255, 0)
        self.PURPLE = (128, 0, 128)

        self.SCORE_COLORS = {
            "perfect": self.PURPLE,
            "great": self.GREEN,
            "good": self.BLUE,
            "okay": self.YELLOW,
            "bad": self.ORANGE,
            "miss": self.RED
        }
        self.LETTER_SCORES = {
            60: ("D", self.RED),
            70: ("C", self.ORANGE),
            80: ("B", self.YELLOW),
            90: ("A", self.GREEN),
            95: ("S", self.PURPLE),
            98: ("SS", self.WHITE)
        }

        # TIMING
        self.TIMING_WINDOW = {
            # ms: [Message, Score]
            20: ("perfect", 100),
            50: ("great", 80),
            70: ("good", 60),
            90: ("okay", 40),
            110: ("bad", 20),
            140: ("miss", 0)
        }

        # Column numbers are an entirely different system I don't particularly care to cater to
        self.settings = settings.Settings()
        self.player = classes.Player()

        # in between state. Hitbox will change depending on up_scroll. (either 100 or height - 100)
        self.current_song = None
        self.song_index = 0
        self.settings_index = 0

        self.scroll_box = None
        self.hit_box = None
        self.column_notes = None
        self.note_size = self.settings.default_note_size

        # GAME SETTINGS that the script changes, not player
        self.start_time = 0
        self.current_time = -1
        self.time_left = -1

        self.messages = [] # So...
        self.glow = "" # I hear strings are more memory efficient than lists
        self.title_fade = 255
        self.select_debounce = 0
        self.play_debounce = 3000

    def calculate_letter_score(self):
        max_score = self.current_song.note_amount * 100
        try:
            accuracy = (self.player.score / max_score) * 100
        except ZeroDivisionError:
            accuracy = 0
        for percent, (letter, color) in self.LETTER_SCORES.items():
            if accuracy < percent:
                return accuracy, letter, color
        return accuracy, "SS", self.WHITE

    def update_layout(self):
        self.scroll_box = pygame.Rect(self.SCREEN_WIDTH // 2 - (self.settings.scroll_size * self.settings.scroll_zoom) // 2,
                                      0,
                                      self.settings.scroll_size * self.settings.scroll_zoom, self.SCREEN_HEIGHT)
        self.note_size = (self.settings.default_note_size * (self.settings.columns / self.settings.default_columns) *
                          (self.settings.scroll_size * self.settings.scroll_zoom / self.settings.scroll_size))
        hit_box_h = 100 if self.settings.up_scroll else self.SCREEN_HEIGHT - 100
        self.hit_box = pygame.Rect(self.scroll_box.x, hit_box_h, self.scroll_box.width, self.note_size)

    def fill_columns(self, beats):
        self.column_notes = [[] for _ in range(int(self.settings.columns))]
        for note in beats:
            self.column_notes[note.col].append(note)

    def reset_game(self):
        self.messages.clear()
        self.glow = ""
        self.current_song = None
        self.player.reset_stats()

    def new_game(self): # aka new_game
        self.update_layout()
        self.reset_game()

        selected = self.song_list[self.song_index]
        osu, audio, img = selected["osu"], selected["audio"], selected["img"]
        self.current_song = classes.Song(osu, audio, img)

        self.settings.columns = self.current_song.columns
        self.fill_columns(self.current_song.beatmap)
        self.title_fade = 255
        self.time_left = self.current_song.length
        self.start_time = pygame.time.get_ticks() + self.play_debounce

    def hit_note(self, col):
        # should i look for nearest note?
        self.glow = str(set(self.glow + str(col)))

        notes = self.column_notes[col]
        if not notes:
            return
        note = notes[0]

        delay = abs(self.current_time - note.time)

        for ms, (msg, points) in self.TIMING_WINDOW.items():
            if delay <= ms:
                if note.is_hold():
                    note.holding = True # so if its within time and you hold it, wait until release !
                    return
                color = self.SCORE_COLORS[msg]

                self.messages.append(visuals.Msg(msg, color))

                self.player.score += points
                setattr(self.player, msg, getattr(self.player, msg, 0) + 1)

                notes.pop(0)
                self.current_song.beatmap.remove(note)

                return

    def release_note(self, col):
        self.glow = self.glow.replace(str(col), "")

        note = None
        for n in self.column_notes[col]:
            if n.holding:
                note = n
                break
        if not note: return

        delay = abs(self.current_time - note.end)

        for ms, (msg, points) in self.TIMING_WINDOW.items():
            if delay <= ms:
                color = self.SCORE_COLORS[msg]

                self.messages.append(visuals.Msg(msg, color))
                self.player.score += points

                self.column_notes[col].remove(note)
                self.current_song.beatmap.remove(note)

                return

    def process_input(self):
        for event in pygame.event.get():
            key = getattr(event, "key", None)
            unicode = getattr(event, "unicode", None)

            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                # Could probably make this a keybinds dictionary\
                if self.STAGE == self.START or self.STAGE == self.FINISH:
                    if key == pygame.K_RETURN:
                        self.reset_game()
                        self.STAGE = self.CHOOSING_SONG

                elif self.STAGE == self.CHOOSING_SONG:
                    if key == pygame.K_RETURN:
                        self.STAGE = self.PLAYING
                        self.new_game()
                    elif key == pygame.K_ESCAPE:
                        self.STAGE = self.SETTINGS

                elif self.STAGE == self.PLAYING and self.current_song:
                    if key in self.settings.keybinds:
                        col = self.settings.keybinds.index(key)
                        self.hit_note(col)

                    elif key == pygame.K_ESCAPE:
                        self.current_time = self.current_song.length + 1
                        self.current_song.end()
                        self.STAGE = self.FINISH

                elif self.STAGE == self.SETTINGS:
                    option = self.settings.options[self.settings_index]
                    attr = getattr(self.settings, option["key"])

                    if key == pygame.K_RETURN:
                        #self.settings.editing = not self.settings.editing # wait whats the point of this
                        self.STAGE = self.CHOOSING_SONG

                    elif key in [pygame.K_UP, pygame.K_DOWN]:
                        if option["type"] in [int, float]:
                            if key == pygame.K_UP:
                                new_val = min(option["max"], attr + option["step"])
                            else:
                                new_val = max(option["min"], attr - option["step"])
                            setattr(self.settings, option["key"], new_val)

                    elif key == pygame.K_SPACE:
                        if option["type"] is bool:
                            setattr(self.settings, option["key"], not attr)
                        elif option["type"] is list:
                            new_index = (option["editing"] + 1) % 4
                            option["editing"] = new_index

                    elif unicode and unicode in string.ascii_lowercase and option["key"] == "keybinds":
                        new_list = self.settings.keybinds[:]
                        new_list[option["editing"]] = key
                        self.settings.keybinds = new_list

                    elif key == pygame.K_BACKSPACE:
                        self.settings.editing = False
                        self.STAGE = self.CHOOSING_SONG

            elif event.type == pygame.KEYUP:
                if self.STAGE == self.PLAYING and self.current_song:
                    if key in self.settings.keybinds:
                        col = self.settings.keybinds.index(key)
                        self.release_note(col)

        keys = pygame.key.get_pressed()
        if self.select_debounce == 0:
            self.select_debounce = 7 # magic number
            if self.STAGE == self.CHOOSING_SONG:
                if keys[pygame.K_UP]:
                    self.song_index = max(0, self.song_index - 1)
                elif keys[pygame.K_DOWN]:
                    self.song_index = min(len(self.song_list) - 1, self.song_index + 1)
            elif self.STAGE == self.SETTINGS:
                if keys[pygame.K_LEFT]:
                    self.settings_index = max(0, self.settings_index - 1)
                elif keys[pygame.K_RIGHT]:
                    self.settings_index = min(len(self.settings.options) - 1, self.settings_index + 1)


    def detect_misses(self):
        for col in range(int(self.settings.columns)):
            notes = self.column_notes[col]

            if not notes:
                continue

            note = notes[0]

            missed_hit = self.current_time - note.time > max(self.TIMING_WINDOW.keys())
            if note.is_hold():
                if note.holding:
                    missed_hit = self.current_time - note.end > max(self.TIMING_WINDOW.keys())

            if missed_hit:
                self.messages.append(visuals.Msg("miss", self.SCORE_COLORS["miss"]))
                self.player.miss += 1

                notes.pop(0)
                self.current_song.beatmap.remove(note)

    def update_msgs(self):
        for msg in self.messages:
            msg.update()
            if msg.alpha < 0:
                self.messages.remove(msg)

    def detect_finish(self):
        if self.STAGE == self.PLAYING:
            if self.current_time >= self.current_song.length:
                self.current_song.end()
                self.STAGE = self.FINISH

    def update_debounces(self):
        # Take a shot for every mini method in this script
        self.current_time = -1
        self.time_left = -1
        self.select_debounce = max(0, self.select_debounce - 1)

    def update(self):
        # This would kill a victorian child.
        # self.current_time = pygame.time.get_ticks() - self.start_time if self.current_song and self.current_song.playing else -1

        if self.STAGE == self.PLAYING:
            now = pygame.time.get_ticks()
            self.current_time = now - self.start_time
            if self.current_song and self.current_song.playing:
                self.time_left = self.current_song.length - self.current_time
                self.detect_misses()
                self.update_msgs()
                self.detect_finish()
            elif now >= self.start_time:
                self.current_song.play()
        else:
            self.update_debounces()

    def render(self):
        self.screen.fill(self.GREY)
        if self.STAGE == self.START:
            visuals.draw_start_screen(self)
        elif self.STAGE == self.CHOOSING_SONG:
            visuals.draw_song_list(self)
        elif self.STAGE == self.SETTINGS:
            visuals.draw_settings(self)
        elif self.STAGE == self.PLAYING:
            visuals.draw_scroll_box(self)
            visuals.draw_notes(self)
            visuals.draw_hit_box(self)
            visuals.draw_messages(self)
            visuals.draw_time_left(self)
            if self.title_fade > 0:
                visuals.draw_song_title(self)
        elif self.STAGE == self.FINISH:
            visuals.draw_score_screen(self)

    def run(self):
        while self.running:
            self.process_input()
            self.update()
            self.render()

            pygame.display.flip()
            self.clock.tick(self.FPS)

        pygame.quit()
