import pygame
import random
import math
from settings import HEIGHT


class Terrain:
    def __init__(self):
        self.segment_width = 40
        self.segment_count = 100
        self.amplitude = 60
        self.wavelength = 20
        self.base_y = 400
        self.segments = []
        self.generate_segments()

    def generate_segments(self):
        self.segments.clear()
        for i in range(self.segment_count):
            x = i * self.segment_width
            y = self.base_y + self.amplitude * math.sin(i / self.wavelength)
            self.segments.append((x, y))

    def update(self, player_x):
        # Add new segments if player moves forward
        last_x = self.segments[-1][0]
        while last_x - player_x < 1000:
            i = len(self.segments)
            x = self.segments[-1][0] + self.segment_width
            y = self.base_y + self.amplitude * math.sin(i / self.wavelength + random.uniform(-0.2, 0.2))
            self.segments.append((x, y))
            last_x = x

        # Remove segments behind the player
        while self.segments and self.segments[1][0] < player_x - 500:
            self.segments.pop(0)

    def draw(self, screen, camera_offset_x):
        points = [(x - camera_offset_x, y) for (x, y) in self.segments]
        pygame.draw.lines(screen, (70, 200, 50), False, points, 8)

    def get_ground_y(self, x):
        for i in range(len(self.segments) - 1):
            x1, y1 = self.segments[i]
            x2, y2 = self.segments[i + 1]
            if x1 <= x <= x2:
                t = (x - x1) / (x2 - x1)
                return y1 + (y2 - y1) * t
        return HEIGHT  # fallback if out of bounds
