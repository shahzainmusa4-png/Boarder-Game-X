import pygame
import random

class Cloud:
    def __init__(self, image_paths, x, y, speed):
        self.images = [pygame.image.load(path).convert_alpha() for path in image_paths]
        img = random.choice(self.images)  # pick one of the 3
        scale_factor = random.uniform(0.4, 0.7)
        self.image = pygame.transform.scale(
            img,
            (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor))
        )
        self.rect = self.image.get_rect()
        self.world_x = x
        self.world_y = y
        self.speed = speed

    def update(self):
        self.world_x -= self.speed  # drift left

    def draw(self, screen, camera_x):
        screen_x = self.world_x - camera_x * 0.5  # parallax
        screen.blit(self.image, (screen_x, self.world_y))

