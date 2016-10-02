from itertools import cycle
from random import choice
import pygame as pg

from .. import tools, prepare
from ..components.labels import Label, Blinker
from ..components.animation import Task


class HighScores(tools._State):
    def __init__(self):
        super(HighScores, self).__init__()
        
    def startup(self, persistent):
        self.persist = persistent
        player = self.persist["player"]
        last_score = self.persist["last score"]
        self.music_handler = self.persist["music handler"]
        scores = sorted(player.high_scores, reverse=True)
        self.labels = pg.sprite.Group()
        self.animations = pg.sprite.Group()
        
        font = "Taurus-Mono-Outline-Regular"
        titles = []
        colors = [(255, 170, 0),(170, 255, 0),(170, 0, 255),
                       (255, 0, 170),(0, 255, 170),(0, 170, 255)]
        for color in colors:
            label = Label("High Scores", {"midtop": prepare.SCREEN_RECT.midtop},
                                text_color=color, font_size=64,
                                font_path=prepare.FONTS[font])
            titles.append(label)
        self.titles = cycle(titles)
        self.title = next(self.titles)          
        cx = prepare.SCREEN_RECT.centerx
        
        for s, top in zip(scores[:10], range(100, 700, 55)):
            text = "{}".format(int(s))
            pos = {"midtop": (cx, top)}
            if s == last_score:
                Blinker(text, pos, 500, self.labels,font_size=48,
                          text_color=choice(colors), font_path=prepare.FONTS[font])
            else:
                Label("{}".format(int(s)), {"midtop": (cx, top)}, self.labels,
                         font_size=48, text_color=choice(colors),
                         font_path=prepare.FONTS[font])
        task = Task(self.next_color, 110, -1)
        self.animations.add(task)
        self.last_click = None
        midbottom = (cx, prepare.SCREEN_RECT.bottom - 10)
        Blinker("Press SPACE to play again", {"midbottom": midbottom}, 750,
                  self.labels, font_size=24, text_color="white",
                  font_path=prepare.FONTS[font])
                   
    def next_color(self):
        self.title = next(self.titles)
        
    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
            elif event.key == pg.K_SPACE:
                self.done = True
                self.next = "GAMEPLAY"                
        elif event.type == pg.MOUSEBUTTONUP:
            now = pg.time.get_ticks()
            if self.last_click is not None:
                span = now - self.last_click
            self.last_click = now
        
    def update(self, dt):
        self.animations.update(dt)
        self.labels.update(dt)
        self.music_handler.update()
        
    def draw(self, surface):
        surface.fill(pg.Color("black"))
        self.title.draw(surface)
        self.labels.draw(surface)