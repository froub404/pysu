import pygame # sigh.

class Settings:
    def __init__(self):
        self.default_note_size = 70
        self.default_columns = 4

        self.columns = self.default_columns # this will change based on song
        # do not ask me about the keybinds

        self.keybinds = [pygame.K_q, pygame.K_w, pygame.K_o, pygame.K_p]
        self.scroll_size = 340
        self.up_scroll = False
        self.scroll_rate = 0.84
        self.scroll_zoom = 1.0

        self.column_colors = (
            (255, 0, 0),  # red
            (0, 0, 255),  # blue
            (0, 255, 0),  # green
            (255, 255, 0),  # yellow
            (255, 165, 0),  # orange
            (128, 0, 128),  # purple
        ) # todo be able to change this?

        self.options = [
            {"name": "Keybinds", "key": "keybinds", "type": list, "editing": 0},
            {"name": "Scroll Speed", "key": "scroll_rate", "type": float, "min": 0.5, "max": 2.0, "step": 0.01},
            {"name": "Scroll Size", "key": "scroll_size", "type": int, "min": 250, "max": 400, "step": 10},
            {"name": "Scroll Zoom", "key": "scroll_zoom", "type": float, "min": 0.5, "max": 1.5, "step": 0.1},
            {"name": "Up Scroll", "key": "up_scroll", "type": bool}
        ]