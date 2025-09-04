# particles.py

import pygame
import random

class Particle:
    def __init__(self, x, y, color):
        self.pos = [x, y]
        self.vel = [random.uniform(-1, 1), random.uniform(-2, -0.5)]
        self.life = random.randint(15, 25)
        self.color = color
        self.size = random.randint(2, 4)

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.life -= 1
        self.size *= 0.95

    def draw(self, screen, offset_x):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.pos[0] - offset_x), int(self.pos[1])), int(self.size))

class ParticleSystem:
    def __init__(self, color):
        self.particles = []
        self.color = color

    def emit(self, x, y):
        for _ in range(3):  # Number of particles per frame
            self.particles.append(Particle(x, y, self.color))

    def update_and_draw(self, screen, offset_x):
        for particle in self.particles[:]:
            particle.update()
            particle.draw(screen, offset_x)
            if particle.life <= 0:
                self.particles.remove(particle)
