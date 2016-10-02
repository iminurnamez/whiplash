import os
from itertools import cycle
from random import choice
import json

import pygame as pg

from .. import tools, prepare
from ..components.animation import Task, Animation
from ..components.labels import Label, Blinker
from ..components.player import Player
from ..components.snakes import Snake
from ..components.music_handler import MusicHandler


class TitleScreen(tools._State):
    def __init__(self):
        super(TitleScreen, self).__init__()
        w, h = prepare.SCREEN_RECT.size
        self.x_points = list(range(-200, -100)) + list(range(w + 100, w + 200))
        self.y_points = list(range(-200, -100)) + list(range(h + 100, h + 200))
        self.colors = [(255, 170, 0), (170, 0, 255), (170, 255, 0), 
                             (0, 170, 255), (255, 0, 170), (0, 255, 170)]
        self.bg_color = pg.Color("black")
        self.color_cycle =  cycle(self.colors)
        self.color = next(self.color_cycle)
        self.cx = prepare.SCREEN_RECT.w + 350
        font = prepare.FONTS["Taurus-Mono-Outline-Regular"]
        self.title = Label("WHIPLASH", {"midleft": (self.cx, prepare.SCREEN_RECT.centery)},
                                 text_color=self.color, font_size=96, font_path=font)
        self.animations = pg.sprite.Group()
        task = Task(self.next_color, 100, -1)
        cx = prepare.SCREEN_RECT.centerx
        ani = Animation(cx=cx, duration=5000, delay=500, transition="out_elastic")
        ani.start(self)
        adder = Task(self.add_snake, 250, 50)
        self.animations.add(task, ani, adder)
        self.snakes = []
        self.music_handler = MusicHandler()
        self.labels = pg.sprite.Group()
        pos = {"midbottom": (cx, prepare.SCREEN_RECT.bottom - 10)}
        Blinker("Press SPACE to play", pos, 750, self.labels, font_size=36,
                   text_color="white", font_path=font)
        
    
    def add_snake(self):
        c = choice(self.colors)
        x = choice(self.x_points)
        y = choice(self.y_points)
        num_nodes = 120
        snake = Snake((x, y), num_nodes, c, 3)            
        self.snakes.append(snake)
        
    def next_color(self):
        self.color = next(self.color_cycle)
        self.title.text_color = pg.Color(*self.color)
        
    def startup(self, persistent):
        self.persist = persistent
        self.music_handler.next_song()
        
    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
            elif event.key == pg.K_SPACE:
                self.done = True
                self.persist["player"] = self.make_player()
                self.persist["music handler"] = self.music_handler
                self.next = "GAMEPLAY"
                
    def load_player(self):
        try:
            player_file = os.path.join("resources", "player_save.json")
            with open(player_file, "r") as f:
                player_info = json.load(f)
        except IOError:
            player_info = {"points": 0,
                                 "level": 1,
                                 "high scores": []}
        return player_info
        
    def make_player(self):
        info = self.load_player()
        return Player(info)                    
        
    def update(self, dt):
        self.labels.update(dt)
        self.animations.update(dt)
        self.title.update_text()
        self.title.rect.centerx = self.cx
        for s in self.snakes:
            s.update(dt, prepare.SCREEN_RECT)
            
    def draw(self, surface):
        surface.fill(pg.Color("black"))
        for s in self.snakes:
            s.draw(surface)
        self.title.draw(surface)
        self.labels.draw(surface)