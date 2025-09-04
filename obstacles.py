import pygame
import random

class Obstacle:
    def __init__(self, x_world, image_list, scale_factor=0.4):
        img_path = random.choice(image_list)
        image = pygame.image.load(img_path).convert_alpha()

        # Scale proportionally
        new_w = int(image.get_width() * scale_factor)
        new_h = int(image.get_height() * scale_factor)
        self.image = pygame.transform.scale(image, (new_w, new_h))

        # World position (for camera movement)
        self.x_world = x_world
        self.y_world = 0  # will be set in update()
        self.rect = self.image.get_rect()

    def update(self, terrain):
        # Position the bottom of the obstacle on the ground
        ground_y = terrain.get_ground_y(self.x_world)
        self.y_world = ground_y
        self.rect.midbottom = (self.x_world, ground_y)

    def draw(self, screen, camera_x):
        # Render slightly "buried" in ground for visual depth
        screen_x = self.x_world - camera_x
        screen_y = self.y_world + 8  # bury by 8 pixels
        screen.blit(self.image, (screen_x - self.rect.width // 2, screen_y - self.rect.height))


