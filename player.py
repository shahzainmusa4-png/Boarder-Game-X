import pygame
from settings import *

class Player:
    def __init__(self, bike_choice="Dino"):
        if bike_choice == "Frogie":
            self.image = pygame.image.load("assets/images/cars/Snowboarder Frog.png").convert_alpha()
        else:
            self.image = pygame.image.load("assets/images/cars/Snowboarding Dino.png").convert_alpha()

        self.image = pygame.transform.scale(self.image, (95, 90))
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 300

        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.angle = 0
        self.angular_velocity = 0

        self.total_rotation = 0
        self.previous_angle = 0
        self.score = 0
        self.distance = 0
        self.crashed = False

        self._score_popups = []  # (text, x, y, timer)

    def add_score(self, points, text_x, text_y):
        """Add score and create popup."""
        self.score += points
        self._score_popups.append([f"+{points}", text_x, text_y, 60])

    def update(self, terrain, obstacles=[]):
        keys = pygame.key.get_pressed()

        if self.crashed:
            self.vel_y += GRAVITY
            self.rect.y += self.vel_y
            self.rect.x += self.vel_x
            self.angle += 5
            return

        # Horizontal control
        if self.on_ground:
            if keys[pygame.K_RIGHT]:
                self.vel_x += 0.55
            if keys[pygame.K_LEFT]:
                self.vel_x -= 0.33

        # Rotation in air
        if not self.on_ground:
            if keys[pygame.K_a]:
                self.angular_velocity += 0.2
            if keys[pygame.K_d]:
                self.angular_velocity -= 0.2

        # Clamp
        self.vel_x = max(min(self.vel_x, 7), -5)
        self.angular_velocity = max(min(self.angular_velocity, 8), -8)

        # Move horizontally
        self.rect.x += self.vel_x
        self.distance += abs(self.vel_x)

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -10.5
            self.on_ground = False

        # Gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # Rotation
        if not self.on_ground:
            self.angle += self.angular_velocity
            self.angular_velocity *= 0.985
        else:
            if abs(self.angular_velocity) > 5:
                self.crashed = True
            else:
                self.angle = 0
                self.angular_velocity = 0

        # Friction
        if self.on_ground:
            self.vel_x *= 0.90
        else:
            self.vel_x *= 0.99

        # Reset
        was_on_ground = self.on_ground
        self.on_ground = False

        # Terrain collision
        ground_y = terrain.get_ground_y(self.rect.centerx)
        if self.rect.bottom >= ground_y:
            self.rect.bottom = ground_y
            self.vel_y = 0

            if not was_on_ground:
                landing_angle = abs(self.angle % 360)
                if 95 < landing_angle < 265:
                    self.crashed = True
                else:
                    flips = int(abs(self.total_rotation) // 300)
                    if flips > 0:
                        direction = "Backflip" if self.total_rotation > 0 else "Frontflip"
                        points = flips * (100 if direction == "Backflip" else 50)
                        self.add_score(points, self.rect.centerx, self.rect.top)
                    self.total_rotation = 0
                    self.previous_angle = 0

            self.on_ground = True

            if not self.crashed:
                if self.angle > 0:
                    self.angle -= min(self.angle, 4)
                elif self.angle < 0:
                    self.angle += min(abs(self.angle), 4)

        # Obstacle check
        for obs in obstacles:
            if self.rect.colliderect(obs.rect):
                self.crashed = True
            elif not hasattr(obs, "jumped_over"):
                # Player passes obstacle while above it
                if self.rect.left > obs.rect.right and self.rect.bottom < obs.rect.top:
                    obs.jumped_over = True
                    self.add_score(250, self.rect.centerx, self.rect.top - 30)

        # Track flips
        if not self.on_ground:
            rotation_change = self.angle - self.previous_angle
            self.total_rotation += rotation_change
            self.previous_angle = self.angle

        # Popups
        for popup in self._score_popups:
            popup[2] -= 1
            popup[3] -= 1
        self._score_popups = [p for p in self._score_popups if p[3] > 0]

    def draw(self, screen, camera_offset_x):
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        new_rect = rotated_image.get_rect(center=(self.rect.centerx - camera_offset_x, self.rect.centery))
        screen.blit(rotated_image, new_rect)

        # Popups
        font = pygame.font.SysFont(None, 28)
        for text, x, y, _ in self._score_popups:
            img = font.render(text, True, (0, 0, 206))
            screen.blit(img, (x - camera_offset_x, y))
