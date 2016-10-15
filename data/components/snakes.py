from math import pi, hypot, atan2, sin, cos
from random import randint, choice, uniform

import pygame as pg

from .. import prepare
from ..components.angles import get_distance, get_angle, project
from ..components.animation import Animation


class Snake(object):
    """Represents enemy "snakes"."""
    transitions = ["linear"]
    
    def __init__(self, pos, num_nodes, color, speed):
        self.chain = Chain(pos, num_nodes, color)
        self.animations = pg.sprite.Group()
        self.head_x, self.head_y = pos
        self.speed = speed
        
    def move(self, screen_rect):
        """
        Pick a random destination and create an Animation to move
        to the new destination.
        """
        screen_rect = prepare.SCREEN_RECT
        x = randint(-20, screen_rect.w + 20)
        y = randint(-20, screen_rect.h + 20)
        
        dist = get_distance((self.head_x, self.head_y), (x, y))
        dur = int(dist * self.speed)
        ani = Animation(head_x=x, head_y=y, duration=dur, transition=choice(self.transitions))
        ani.start(self)
        self.animations.add(ani)
        
    def update(self, dt, screen_rect):
        self.animations.update(dt)
        self.chain.update((self.head_x, self.head_y))
        if not self.animations:
            self.move(screen_rect)
        
    def draw(self, surface):
        self.chain.draw(surface)
        
        
class Chain(object):
    """
    A chain of nodes. Each node's position is dependent on the
    the position of its parent.
    """
    hurt_sound = prepare.SFX["hurt1"]
    def __init__(self, pos, num_nodes, color):
        self.dead = False
        self.color = color
        self.head = Node(pos, None)
        self.nodes = []
        last_node = self.head
        
        for _ in range(num_nodes):
            pos = last_node.pos[0] - 1, last_node.pos[1]
            node = Node(pos, last_node)
            self.nodes.append(node)
            last_node = node
    
    def add_node(self):
        """Add new node to the end of the chain."""
        parent = self.nodes[-1]
        parent2 = parent.parent
        dx = parent.pos[0] - parent2.pos[0]
        dy = parent.pos[1] - parent2.pos[1]
        pos = parent.pos[0] + dx, parent.pos[1] + dy
        node = Node(pos, parent)
        self.nodes.append(node)
        
    def snip(self, snip_points):
        """
        Used for player snake. At each colliision (snip point), nodes
        are removed from chain. Removed sections of nodes are returned
        to be drawn to the screen.
        """
        positions = [(int(n.pos[0]), int(n.pos[1])) for n in self.nodes]
        indexes = [positions.index(p) for p in snip_points]
        if any((x < 10 for x in indexes)):
            self.dead = True
        remnants = []
        
        for snipdex in sorted(indexes, reverse=True):
            remnant = positions[snipdex:]
            remnants.append(remnant)
            positions = positions[:snipdex]
        self.nodes = self.nodes[:indexes[0]]
        if remnants:
            self.hurt_sound.play()
        return remnants
        
    def update(self, mouse_pos):
        last_pos = self.head.pos
        self.head.pos = mouse_pos
        if last_pos != self.head.pos:
            for node in self.nodes:
                moved = node.update()
                if not moved:
                    break
        self.points = [(int(self.head.pos[0]), int(self.head.pos[1]))]
        self.points.extend([(int(n.pos[0]), int(n.pos[1])) for n in self.nodes])
        
    def draw(self, surface):
        if len(self.points) > 1:
            #pg.draw.lines(surface, self.color, False, self.points, 2)
            for p in self.points:
                pg.draw.circle(surface, self.color, p, 2)
        
class Node(object):
    """Chains are comprised of individual nodes."""
    def __init__(self, pos, parent, length=1):
        self.pos = pos
        self.parent = parent
        self.x_velocity = 0
        self.y_velocity = 0
        self.length = length
        
    def update(self):
        """Adjust node position based on angle to parent node."""
        p = self.parent
        dist = hypot(p.pos[0] - self.pos[0], p.pos[1] - self.pos[1])
        if dist > self.length:
            x, y = self.pos
            x2, y2 = p.pos
            x_dist, y_dist = x2 - x, y2 - y
            angle_to = atan2(-y_dist, x_dist) % (2 * pi)
            distance = dist - self.length
            vecx = cos(angle_to) * distance
            vecy = sin(angle_to) * distance
            self.pos = self.pos[0] + vecx, self.pos[1] - vecy
            return True
        return False
        

class Remnant(object):
    """
    A section of chain that has been removed. Remnants are
    faded out then discarded.
    """
    def __init__(self, points):
        self.alpha = 255
        self.points = points
        x_list = [x[0] for x in points]
        y_list = [x[1] for x in points]
        minx = min(x_list)
        maxx = max(x_list)
        miny = min(y_list)
        maxy = max(y_list)
        w = max(2, abs(maxx - minx))
        h = max(2, abs(maxy - miny))
        surf = pg.Surface((w, h))
        surf.fill(pg.Color("black"))
        surf.set_colorkey(pg.Color("black"))
        adj_pts = [(p[0] - minx, p[1] - miny) for p in points]
        if len(adj_pts) < 2:
            adj_pts = adj_pts * 2
        for adj_pt in adj_pts:
            pg.draw.circle(surf, pg.Color("white"), adj_pt, 3)
        
        surf.set_alpha(self.alpha)
        self.rect = surf.get_rect(topleft=(minx, miny))
        self.image = surf
        
    def update(self):
        self.image.set_alpha(self.alpha)
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)
