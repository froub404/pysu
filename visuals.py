"""
version 5-3-2026
"""

import pygame

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
        
def ms_to_mins(ms):
    length = ms / 1000
    mins = int(length // 60)
    secs = "{:02d}".format(int(length % 60))

    return mins, secs
        
def dim_color(rgb, dim=0.5):
    r, g, b = rgb
    return tuple(map(lambda x:x*dim, [r, g, b]))

def wrap_text(text, font, max_w):
    if font.size(text)[0] <= max_w:
        return [text]

    lines = []
    words = text.split(" ")
    current_line = ""
    for word in words[::-1]:
        if font.size(word)[0] > max_w:
            lines.append(word)
            continue

        new_line = word + " " + current_line
        if font.size(new_line)[0] > max_w:
            lines.append(current_line.strip())
            current_line = word + " "
        else:
            current_line = new_line
    if current_line: lines.append(current_line.strip())

    return list(reversed(lines))

# START SCREEN
def draw_start_screen(game):
    start_txt = game.FONT_LG.render("Press enter to start :^)", True, game.BLACK)
    game.screen.blit(start_txt, start_txt.get_rect(center=(game.SCREEN_WIDTH // 2, game.SCREEN_HEIGHT // 2)))

# SELECTION SCREEN
def draw_song_list(game):
    # "Name Diff" : [Osu, Mp3] Dont really need the meta
    txt = game.FONT_SM.render("Press ESC to change settings", True, game.BLUE)
    game.screen.blit(txt, txt.get_rect(bottomleft=(0, game.SCREEN_HEIGHT)))

    for i, song in enumerate(game.song_list):
        bw, bh = 300, 100
        dy = 0
        if i == game.song_index:
            bw *= 1.5
        else:
            dy = (i - game.song_index) * bh
        bx, by = game.SCREEN_WIDTH - bw, (game.SCREEN_HEIGHT // 2 - bh // 2) + dy # default for chosen

        pygame.draw.rect(game.screen, game.BLUE, (bx, by, bw, bh))
        pygame.draw.rect(game.screen, dim_color(game.BLUE), (bx, by, bw, bh), 5) # outline? if its cute

        start_y = by
        padding = 10
        lines = wrap_text(song["title"], game.FONT_SM, bw - padding)
        for line in lines:
            display_txt = game.FONT_SM.render(line, True, game.WHITE)
            display_rect = display_txt.get_rect(topleft=(bx + padding, start_y + padding))
            game.screen.blit(display_txt, display_rect)
            start_y += display_rect.h + padding

def draw_keybind_selection(game, option, bounds):
    # i dont think i will have more lists
    space = bounds.w * 0.4
    inc = space // len(game.settings.keybinds)
    x = bounds.centerx - space // 2
    for i, key in enumerate(game.settings.keybinds):
        txt = game.FONT_LG.render(pygame.key.name(key).upper(), True, game.WHITE)
        rect = txt.get_rect()
        rect.midleft = (x, bounds.centery)
        game.screen.blit(txt, rect)
        if i == option["editing"]:
            pygame.draw.lines(game.screen, game.WHITE, False, ((rect.left, rect.bottom + 5), (rect.left, rect.bottom + 10), (rect.right, rect.bottom + 10), (rect.right, rect.bottom + 5)), 3)

        x += inc

def draw_int_selection(game, option, bounds):
    # since basically all int/float settings work the same
    setting_value = game.FONT_LG.render(str(round(getattr(game.settings, option["key"]), 2)), True, game.WHITE)
    setting_rect = setting_value.get_rect()
    setting_rect.center = bounds.center
    game.screen.blit(setting_value, setting_rect)

    # rects are more memory efficient than text rendering. so...
    # its just very crowded.
    pygame.draw.rect(game.screen, game.WHITE, (setting_rect.left - 50, setting_rect.centery - 20, 40, 40))
    pygame.draw.rect(game.screen, game.BLACK, (setting_rect.left - 50, setting_rect.centery - 20, 40, 40), 3)
    pygame.draw.line(game.screen, game.BLACK, (setting_rect.left - 45, setting_rect.centery), (setting_rect.left - 15, setting_rect.centery), 4)

    pygame.draw.rect(game.screen, game.WHITE, (setting_rect.right + 10, setting_rect.centery - 20, 40, 40))
    pygame.draw.rect(game.screen, game.BLACK, (setting_rect.right + 10, setting_rect.centery - 20, 40, 40), 3)
    pygame.draw.line(game.screen, game.BLACK, (setting_rect.right + 15, setting_rect.centery),
                     (setting_rect.right + 45, setting_rect.centery), 4)
    pygame.draw.line(game.screen, game.BLACK, (setting_rect.right + 30, setting_rect.centery - 15),
                     (setting_rect.right + 30, setting_rect.centery + 15), 4)

def draw_bool_selection(game, option, bounds):
    val = getattr(game.settings, option["key"])
    bool_txt = game.FONT_MD.render(str(val), True, game.GREEN if val else game.RED, game.WHITE)
    game.screen.blit(bool_txt, bool_txt.get_rect(center=bounds.center))

def draw_settings(game):
    settings = game.settings
    option = settings.options[game.settings_index]
    settings_box = pygame.Rect(0, 0, game.SCREEN_WIDTH // 2, game.SCREEN_HEIGHT)

    pygame.draw.rect(game.screen, game.BLUE, settings_box)
    pygame.draw.rect(game.screen, dim_color(game.BLUE), settings_box, 3)
    pygame.draw.lines(game.screen, game.WHITE, False, ((settings_box.right - 30, settings_box.centery - 10), (settings_box.right - 20, settings_box.centery), (settings_box.right - 30, settings_box.centery + 10)), 5)

    settings_txt = game.FONT_MD.render("Settings", True, game.WHITE)
    game.screen.blit(settings_txt, settings_txt.get_rect(midtop=(settings_box.centerx, settings_box.top + 10)))
    instructions = ("Press up/down to increase/decrease", "Press space to toggle true/false", "Press space to change a keybind")
    txt = ""

    # they all work the same so its fine probably
    setting_name = game.FONT_MD.render(option["name"], True, game.WHITE)
    game.screen.blit(setting_name, setting_name.get_rect(center=(settings_box.centerx, settings_box.centery - 100)))

    if option["type"] is list:
        draw_keybind_selection(game, option, settings_box)
        txt = game.FONT_TN.render(instructions[2], True, game.WHITE)
    elif option["type"] in [int, float]:
        draw_int_selection(game, option, settings_box)
        txt = game.FONT_TN.render(instructions[0], True, game.WHITE)
    elif option["type"] is bool:
        draw_bool_selection(game, option, settings_box)
        txt = game.FONT_TN.render(instructions[1], True, game.WHITE)

    if txt: game.screen.blit(txt, txt.get_rect(midtop=(settings_box.centerx, settings_box.top + 50))) # magic number ;)
    txt = game.FONT_SM.render("Press ENTER to save", True, game.WHITE)
    game.screen.blit(txt, txt.get_rect(center=(settings_box.centerx, settings_box.bottom - 100)))

# PLAYING SCREEN
def draw_song_title(game):
    if game.title_fade > 0:
        game.title_fade = max(0, game.title_fade - 3)

        title = game.current_song.title
        difficulty = game.current_song.difficulty
        mins, secs = ms_to_mins(game.current_song.length)
        author = game.current_song.author
        full_credits = f"{title} [{difficulty}] by {author} ({mins}:{secs})"

        txt_height = game.FONT_MD.get_height()
        lines = wrap_text(full_credits, game.FONT_MD, 400)
        space = txt_height * len(lines)
        y = game.SCREEN_HEIGHT//2 - space//2
        padding = 5
        for line in lines:
            txt = game.FONT_MD.render(line, True, game.RED)
            txt.set_alpha(game.title_fade)
            txt_rect = txt.get_rect()
            txt_rect.topleft = (game.SCREEN_WIDTH//2 - txt_rect.w//2, y)
            game.screen.blit(txt, txt_rect)
            y += txt_height + padding

def draw_hit_box(game):
    # make them glow when hit?
    col_width = game.hit_box.width / game.settings.columns

    for col in range(int(game.settings.columns)):
        x = game.hit_box.x + col * col_width + (col_width - game.note_size) / 2
        y = game.hit_box.centery - game.note_size / 2
        #pygame.draw.rect(game.screen, game.WHITE, game.hit_box, 3)
        pygame.draw.ellipse(game.screen,
                            dim_color(game.settings.column_colors[col]),(x, y, game.note_size, game.note_size))
        if str(col) in game.glow:
            pygame.draw.ellipse(game.screen, game.WHITE, (x, y, game.note_size, game.note_size), 3)

def draw_scroll_box(game):
    # will have to be 0 alpha for now. ugh
    pygame.draw.rect(game.screen, game.BLACK, game.scroll_box)
    for col in range(int(game.settings.columns + 1)):
        x = game.scroll_box.x + col * (game.scroll_box.width // game.settings.columns)
        pygame.draw.line(game.screen, game.WHITE, (x, 0), (x, game.scroll_box.height), 5)

def draw_notes(game):
    # FIXME not sure how to fix upscroll
    for note in game.current_song.beatmap:
        bx = game.scroll_box.left
        bw = game.scroll_box.width

        col_width = bw / game.settings.columns
        x = bx + (note.col * col_width) + (col_width - game.note_size) / 2
        y = game.hit_box.centery + note.get_y(game.current_time, game.settings.scroll_rate, game.settings.up_scroll)

        if (y < -10 or y > game.SCREEN_HEIGHT + 10) and not note.is_hold():
            continue # will this help with lag?

        # for hold notes
        if note.is_hold():
            end_y = game.hit_box.centery + note.get_end_y(game.current_time, game.settings.scroll_rate, game.settings.up_scroll)

            if (end_y > game.SCREEN_HEIGHT + 10 and not game.settings.up_scroll) or (end_y < -10 and game.settings.up_scroll):
                continue

            top = min(y, end_y)
            bottom = max(y, end_y)
            hold_x = bx + (note.col * col_width) + (col_width - game.note_size*0.9) / 2
            cap = min(0, game.hit_box.bottom - bottom)
            pygame.draw.rect(
                game.screen,
                dim_color(game.settings.column_colors[note.col]),
                (int(hold_x), int(top), game.note_size * 0.9, int(bottom - top) + cap)
            )

            pygame.draw.ellipse(
                game.screen,
                dim_color(game.settings.column_colors[note.col]),
                (int(hold_x), int(end_y - game.note_size // 2), game.note_size * 0.9, game.note_size)
            )

        if not note.holding:
            cap = 0
        else:
            cap = min(0, game.hit_box.bottom - (y + game.note_size // 2))
        pygame.draw.ellipse(
            game.screen,
            game.settings.column_colors[note.col],
            [int(x), int(y - game.note_size // 2), game.note_size, game.note_size + cap])

def draw_messages(game):
    sx, sy = (game.scroll_box.x - 50, game.hit_box.y)
    for msg in game.messages:
        if msg.alpha < 0:
            game.messages.remove(msg)
        else:
            txt = game.FONT_MD.render(msg.text.capitalize(), True, msg.color).convert_alpha()
            txt.set_alpha(msg.alpha)

            game.screen.blit(txt, txt.get_rect(center=(sx - msg.dx, sy - msg.dy)))

def draw_time_left(game):
    mins, secs = ms_to_mins(game.time_left)
    txt = game.FONT_SM.render(f"Time Left: {mins}:{secs}", True, game.BLACK)
    game.screen.blit(txt, txt.get_rect(topright=(game.SCREEN_WIDTH - 10, game.SCREEN_HEIGHT - 40)))

# SCORE / END SCREEN
def draw_score_screen(game):
    # todo wow this is so ugly
    # todo this could be split up but i am genuinely about to pass out so goodnight
    accuracy, letter, color = game.calculate_letter_score()

    clear_msg = "Song Cleared :D" if accuracy >= 80 else "Song Finished :/"
    txt = game.FONT_RL.render(clear_msg, True, game.BLUE)
    game.screen.blit(txt, txt.get_rect(topleft=(20, 20)))
    padding = 5
    start_y = txt.get_rect(topleft=(20, 20)).bottom + padding

    for msg, color in game.SCORE_COLORS.items():
        count = getattr(game.player, msg, 0)
        txt = game.FONT_LG.render(f"{msg.capitalize()}: {count}", True, dim_color(color, 0.9))
        game.screen.blit(txt, txt.get_rect(topleft=(20, start_y)))
        start_y += txt.get_rect(topleft=(20, start_y)).height + padding

    txt = game.FONT_RL.render(f"SCORE: {letter}", True, color)
    txt_rect = txt.get_rect()
    txt_rect.topright = (game.SCREEN_WIDTH - 20, game.SCREEN_HEIGHT // 2 + 10)
    game.screen.blit(txt, txt_rect)
    txt = game.FONT_LG.render(f"Accuracy: {round(accuracy, 3)}% - {game.player.score}", True, color)
    game.screen.blit(txt, txt.get_rect(topright=(game.SCREEN_WIDTH - 20, game.SCREEN_HEIGHT // 2 + txt_rect.height + 10)))

    txt = game.FONT_MD.render("Press Enter to return to selection screen", True, game.BLUE)
    game.screen.blit(txt, txt.get_rect(topright=(game.SCREEN_WIDTH - 20, game.SCREEN_HEIGHT - 50)))