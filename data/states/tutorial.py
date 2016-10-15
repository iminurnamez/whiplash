from random import choice

import pygame as pg

from .. import tools, prepare
from ..components.animation import Animation, Task
from ..components.labels import Label
from ..components.snakes import Snake, Chain, Remnant


class Tutorial(tools._State):
    w, h = prepare.SCREEN_RECT.size
    x_points = list(range(-200, -100)) + list(range(w + 100, w + 200))
    y_points = list(range(-200, -100)) + list(range(h + 100, h + 200))
    colors = [(255, 170, 0), (170, 255, 0), (170, 0, 255),
                (255, 0, 170), (0, 255, 170), (0, 170, 255)]
    bg_color = pg.Color("black")
    snake_sound = prepare.SFX["snake"]

    def __init__(self):
        super(Tutorial, self).__init__()
        self.num_nodes = 500
        self.num_snakes = 25

    def add_snake(self):
        """Add a new enemy snake."""
        self.snake_sound.play()
        c = self.color
        x = choice(self.x_points)
        y = choice(self.y_points)
        num_nodes = 150
        snake = Snake((x, y), num_nodes, c, self.snake_speed)
        self.snakes.append(snake)

    def startup(self, persistent):
        self.persist = persistent
        self.player = self.persist["player"]
        self.music_handler = self.persist["music handler"]
        self.animations = pg.sprite.Group()
        pos = prepare.SCREEN_RECT.center
        self.mousex, self.mousey = pos
        self.snake_speed = 3
        self.snakes = []

        task = Task(self.add_snake, 10000, self.num_snakes)
        task2 = Task(self.speed_up, 20000, 15)
        self.color_freq = self.music_handler.bpm[self.music_handler.current_song]
        self.color_flipper = Task(self.change_colors, self.color_freq, -1)
        self.animations.add(task, task2, self.color_flipper)
        self.player_snake = Chain(prepare.SCREEN_RECT.center, 100,
                                               pg.Color("white"))
        self.remnants = []
        self.score = 0
        self.score_label = Label(
                "{}".format(self.score), {"topleft": (0, 0)},
                text_color="white", font_size=32,
                font_path=prepare.FONTS["Taurus-Mono-Outline-Bold"])
        self.bonus_timer = 0
        self.bonus = 1
        self.bonus_label = None
        self.last = None
        self.color = choice(self.colors)
        self.player_color_offset = 0
        self.player_color_frequency = 100
        self.player_color_timer = 0
        
        self.mousex, self.mousey = prepare.SCREEN_RECT.center
        self.make_mouse_moves()
        
    def make_mouse_moves(self):
        mouse_moves = [
                ((100, 100), 1000),
                ((500, 600), 2000),
                ((1000, 500), 2000),
                ((300, 300), 2000)]
        delay_ = 0       
        for dest, dur in mouse_moves:
            ani = Animation(mousex=dest[0], mousey=dest[1], delay=delay_,
                                    duration=dur, round_values=True)
            ani.start(self)
            self.animations.add(ani)
            delay_ += dur

    def add_instruction(self, label, fade_time):
        self.instruction = label
        
    def make_instructions(self):
        instructions = [
                ("Use the mouse to move your snake", 250, 2000),
                ("You gain points while at full length", 5000, 2000)]
        for text, start, dur in instructions:
            label = Label(text, {"center": prepare.SCREEN_RECT.center})
            task = Task(self.add_instruction, start, args=(label, dur))
            self.animations.add(task)            
                

    def speed_up(self):
        """Increase enemy snakes' speed."""
        self.snake_speed -= .1

    def change_colors(self):
        """Choose random color for snakes."""
        colors = [x for x in self.colors if x != self.color]
        color = choice(colors)
        self.color = color
        for s in self.snakes:
            s.chain.color = color

    def set_color_frequency(self, amt):
        """Recurring task to change snake colors every amt milliseconds."""
        self.color_freq = amt
        self.color_flipper.kill()
        self.color_flipper = Task(self.change_colors, self.color_freq, -1)
        self.animations.add(self.color_flipper)

    def get_event(self,event):
        """Handle events passed by the state engine."""
        if event.type == pg.QUIT:
            self.quit = True
            pg.mouse.set_visible(True)
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
                pg.mouse.set_visible(True)
            elif event.key == pg.K_SPACE:
                self.music_handler.next_song()

    def score_points(self, dt):
        """
        Increase player score if player snake is at full length. Score
        is based on current bonus, number of enemy snakes and dt.
        Score label text is updated to reflect new score.
        """
        pts = 0
        if len(self.player_snake.nodes) >= self.num_nodes:
            num_snakes = 1 + len(self.snakes)
            bonus = self.bonus
            self.bonus_timer += dt
            self.bonus = 1 + self.bonus_timer // 20000 #x1 multiplier every 20 seconds
            if self.bonus > bonus:
                prepare.SFX["bonus"].play()
                self.make_bonus_label(self.bonus)
            pts = dt * bonus * num_snakes * .08
        else:
            self.bonus_timer = 0

        self.score += pts
        text = "{}".format(int(self.score))
        self.score_label.set_text(text)

    def make_bonus_label(self, text):
        """Create a label, fade it in then use animation callback to fade out."""
        self.bonus_label = Label(
                text, {"center": prepare.SCREEN_RECT.center},
                text_color=choice(self.colors), font_size=64, alpha=1,
                font_path=prepare.FONTS["Taurus-Mono-Outline-Regular"])
        ani = Animation(alpha=254, duration=1000, round_values=True)
        ani.callback = self.fade_bonus_label
        ani.start(self.bonus_label)
        self.animations.add(ani)

    def fade_bonus_label(self):
        """Fade out bonus label."""
        ani = Animation(alpha=0, duration=1500, round_values=True)
        ani.start(self.bonus_label)
        self.animations.add(ani)

    def to_high_scores(self):
        """Exit to high scores screen."""
        self.done = True
        self.player.add_score(self.score)
        self.player.save()
        self.persist["last score"] = self.score
        self.next = "HIGH_SCORES"

    def update(self, dt):
        print(self.mousex, self.mousey)
        self.animations.update(dt)
        pg.mouse.set_pos((self.mousex, self.mousey))
        #Change how often enemy snakes change color based on
        #beats per minute of current song
        self.music_handler.update()
        bpm = self.music_handler.current_bpm
        if self.color_freq != bpm:
            self.set_color_frequency(bpm)
        
        self.player_color_timer += dt
        freq = self.color_freq // 2**(self.bonus - 1)
        if self.player_color_timer > freq:
            self.player_color_timer -= freq
            self.player_color_offset -= 1
            self.player_color_offset = self.player_color_offset % len(self.colors)

        self.score_points(dt)
        if self.player_snake.dead:
            self.to_high_scores()
        elif len(self.player_snake.nodes) < self.num_nodes:
            self.player_snake.add_node()
        self.player_snake.update((self.mousex, self.mousey))

        for snake in self.snakes:
            snake.update(dt, prepare.SCREEN_RECT)
        snake_points = set(p for s in self.snakes for p in s.chain.points)
        p_points = set((int(node.pos[0]), int(node.pos[1]))
                              for node in self.player_snake.nodes)
        collisions = p_points & snake_points
        if collisions:
            pieces = self.player_snake.snip(collisions)
            for p in pieces:
                remnant = Remnant(p)
                ani = Animation(alpha=0, duration=2000, round_values=True)
                ani.start(remnant)
                self.animations.add(ani)
                self.remnants.append(remnant)

        for rem in self.remnants:
            rem.update()
        self.remnants = [r for r in self.remnants if r.alpha > 0]
        if self.bonus_label:
            self.bonus_label.update_text()
            if self.bonus_label.alpha < 1:
                self.bonus_label = None

    def draw_player(self, surface):
        """
        Draw player "snake". If at full length, the snake is
        divided into 5 colored sections. Colors are cycled in time with the
        music. If snake is not at full length, the snake is colored gray (the
        lower the length, the darker the gray.
        """
        num_nodes = len(self.player_snake.nodes)
        if num_nodes >= self.num_nodes:
            pairs = []
            num_sections = 5
            section_length, remainder = divmod(self.num_nodes, num_sections)
            off = self.player_color_offset
            for i in range(num_sections):
                start = i * section_length
                end = start + section_length
                section = self.player_snake.points[start:end]
                color = self.colors[(i + off) % len(self.colors)]
                pairs.append((section, color))
            for sec, col in pairs:
                for point in sec:
                    pg.draw.circle(surface, col, point, 2)
        else:
            lerp_val = num_nodes / float(self.num_nodes)
            color = tools.lerp((50, 50, 50), (255, 255, 255), lerp_val)
            self.player_snake.color = color
            self.player_snake.draw(surface)

    def draw(self, surface):
        """Draw everything to the screen."""
        surface.fill(self.bg_color)
        for r in self.remnants:
            r.draw(surface)
        for snake in self.snakes:
            snake.draw(surface)
        self.draw_player(surface)
        self.score_label.draw(surface)
        if self.bonus_label:
            self.bonus_label.draw(surface)