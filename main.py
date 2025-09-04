import pygame
from settings import *
from player import Player
from particles import ParticleSystem
from obstacles import Obstacle
from clouds import Cloud
import random

# Init
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Boarder Stunt X")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Georgia", 30)

# Sound files
menu_music_path = "assets/images/soudeffects/menusound.mp3"
enter_game_sfx = pygame.mixer.Sound("assets/images/soudeffects/enterGame.mp3")
select_sfx = pygame.mixer.Sound("assets/images/soudeffects/select.mp3")
game_music_path = "assets/images/soudeffects/GameBackground.mp3"
jump_sfx = pygame.mixer.Sound("assets/images/soudeffects/jump.mp3")
obstacle_crash_sfx = pygame.mixer.Sound("assets/images/soudeffects/obstacleCrash.mp3")
land_head_sfx = pygame.mixer.Sound("assets/images/soudeffects/landOnHead.mp3")

# Volumes
for s in [select_sfx, enter_game_sfx, jump_sfx, obstacle_crash_sfx, land_head_sfx]:
    s.set_volume(0.5)

def play_music(path, volume=0.4, loop=-1):
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loop)
    except Exception as e:
        print("Music load/play failed:", e)

def stop_music():
    pygame.mixer.music.stop()

# Game State
game_state = "menu"
selected_bike = "Dino"
selected_level = "desert"

# Images
desert_obstacles = [
    "assets/images/cactus1.png",
    "assets/images/cactus2.png"
]
autumn_obstacles = [
    "assets/images/fence.png",
    "assets/images/fenceIron.png"
]
cloud_images = [
    "assets/images/cloud1.png",
    "assets/images/cloud3.png",
    "assets/images/cloud4.png"
]

GROUND_OFFSET_Y = 120

desert_bg = pygame.transform.scale(
    pygame.image.load("assets/images/levels/backgroundColorDesert.png"), (WIDTH, HEIGHT)
)
city_bg = pygame.transform.scale(
    pygame.image.load("assets/images/levels/backgroundColorFall.png"), (WIDTH, HEIGHT)
)

ground_desert = pygame.image.load("assets/images/hills.png").convert_alpha()
ground_autumn = pygame.image.load("assets/images/groundLayer1.png").convert_alpha()

desert_particles = ParticleSystem((194, 178, 128))
autumn_particles = ParticleSystem((183, 101, 38))

# Lists
obstacles = []
last_obstacle_x = 800
clouds = []
last_cloud_x = 0

player = Player(selected_bike)
camera_offset_x = 0
_current_music = None

def ensure_menu_music():
    global _current_music
    if _current_music != "menu":
        play_music(menu_music_path, volume=0.35, loop=-1)
        _current_music = "menu"

def ensure_game_music():
    global _current_music
    if _current_music != "game":
        play_music(game_music_path, volume=0.35, loop=-1)
        _current_music = "game"

def stop_current_music():
    global _current_music
    stop_music()
    _current_music = None

# Terrain from image
def get_ground_y_from_image(x_world, ground_img):
    ground_width = ground_img.get_width()
    img_x = int(x_world % ground_width)
    for img_y in range(ground_img.get_height()):
        if ground_img.get_at((img_x, img_y)).a > 0:
            return HEIGHT - ground_img.get_height() + GROUND_OFFSET_Y + img_y
    return HEIGHT

class ImageTerrain:
    def __init__(self, ground_img):
        self.ground_img = ground_img
    def get_ground_y(self, x_world):
        return get_ground_y_from_image(x_world, self.ground_img)

# Menu drawing
def draw_menu(screen, font, selected_bike, selected_level):
    bg = desert_bg if selected_level == "desert" else city_bg
    screen.blit(bg, (0, 0))
    title = font.render("Boarder Stunt X", True, (0, 0, 0))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
    screen.blit(font.render(f"Board: {selected_bike}", True, (0, 0, 0)), (100, 200))
    screen.blit(font.render(f"Level: {selected_level}", True, (0, 0, 0)), (100, 260))
    screen.blit(font.render("Press B to switch board", True, (0, 0, 0)), (100, 340))
    screen.blit(font.render("Press L to switch Map", True, (0, 0, 0)), (100, 380))
    screen.blit(font.render("Press ENTER to Play", True, (0, 0, 0)), (100, 420))
    preview = Player(selected_bike)
    preview.rect.x = WIDTH // 2 - 40
    preview.rect.bottom = HEIGHT - 100
    preview.angle = 0
    preview.draw(screen, camera_offset_x=0)

ensure_menu_music()

running = True
crash_sound_played = False

while running:
    screen.fill(BG_COLOR)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if game_state == "menu":
                if event.key == pygame.K_b:
                    selected_bike = "Frogie" if selected_bike == "Dino" else "Dino"
                    select_sfx.play()
                if event.key == pygame.K_l:
                    selected_level = "autumn" if selected_level == "desert" else "desert"
                    select_sfx.play()
                if event.key == pygame.K_RETURN:
                    enter_game_sfx.play()
                    ensure_game_music()
                    player = Player(selected_bike)
                    obstacles.clear()
                    clouds.clear()
                    last_obstacle_x = player.rect.centerx + 300
                    last_cloud_x = player.rect.centerx + 300
                    crash_sound_played = False
                    image_terrain = ImageTerrain(ground_desert if selected_level == "desert" else ground_autumn)
                    x_pos = player.rect.centerx + WIDTH + 350
                    end_pos = x_pos + 600
                    while x_pos < end_pos:
                        img_list = desert_obstacles if selected_level == "desert" else autumn_obstacles
                        scale = 0.3
                        obstacles.append(Obstacle(x_pos, img_list, scale))
                        x_pos += random.randint(800, 1300)
                    start_x = player.rect.centerx + WIDTH + 200
                    for _ in range(8):
                        cloud_y = random.randint(50, 200)
                        speed = random.uniform(0.3, 0.8)
                        clouds.append(Cloud(cloud_images, start_x, cloud_y, speed))
                        start_x += 350
                    game_state = "play"

            elif game_state == "play":
                if event.key == pygame.K_SPACE:
                    if player.on_ground and not player.crashed:
                        jump_sfx.play()
                if event.key == pygame.K_r and player.crashed:
                    game_state = "menu"
                    stop_current_music()
                    ensure_menu_music()

    if game_state == "menu":
        ensure_menu_music()
        draw_menu(screen, font, selected_bike, selected_level)

    elif game_state == "play":
        camera_offset_x = player.rect.centerx - WIDTH // 2

        if selected_level == "desert":
            screen.blit(desert_bg, (0, 0))
            desert_particles.update_and_draw(screen, camera_offset_x)
            ground_img = ground_desert
        else:
            screen.blit(city_bg, (0, 0))
            autumn_particles.update_and_draw(screen, camera_offset_x)
            ground_img = ground_autumn

        ground_height = ground_img.get_height()
        tile_w = ground_img.get_width()
        ground_start_x = int(camera_offset_x // tile_w) * tile_w - tile_w
        image_terrain = ImageTerrain(ground_img)

        for cloud in clouds:
            cloud.update()
        if player.rect.centerx > last_cloud_x - WIDTH:
            cloud_y = random.randint(50, 200)
            speed = random.uniform(0.3, 0.8)
            clouds.append(Cloud(cloud_images, last_cloud_x, cloud_y, speed))
            last_cloud_x += 350
        for cloud in clouds:
            cloud.draw(screen, camera_offset_x)

        for obs in obstacles[:]:
            obs.update(image_terrain)
            obs.draw(screen, camera_offset_x)

        for x in range(ground_start_x, ground_start_x + WIDTH + tile_w * 2, tile_w):
            screen.blit(ground_img, (x - camera_offset_x, HEIGHT - ground_height + GROUND_OFFSET_Y))

        if player.on_ground and abs(player.vel_x) > 2:
            px, py = player.rect.centerx, player.rect.bottom - 5
            if selected_level == "desert":
                desert_particles.emit(px, py)
            else:
                autumn_particles.emit(px, py)

        if abs(player.vel_x) > 0.5:
            spawn_trigger_x = last_obstacle_x - WIDTH * 0.5
            if player.rect.centerx > spawn_trigger_x:
                gap = random.randint(800, 1300)
                obs_x = last_obstacle_x + gap
                img_list = desert_obstacles if selected_level == "desert" else autumn_obstacles
                scale = 0.3
                obstacles.append(Obstacle(obs_x, img_list, scale))
                last_obstacle_x = obs_x

        player.update(image_terrain, obstacles)
        player.draw(screen, camera_offset_x)

        if player.crashed and not crash_sound_played:
            hit_obstacle = False
            for obs in obstacles:
                if player.rect.colliderect(obs.rect):
                    hit_obstacle = True
                    break
            if hit_obstacle:
                obstacle_crash_sfx.play()
            else:
                land_head_sfx.play()
            stop_current_music()
            crash_sound_played = True

        # HUD
        screen.blit(font.render(f"Score: {player.score}", True, (0, 0, 0)), (20, 20))
        dist_text = font.render(f"Distance: {int(player.distance // 10)} m", True, (0, 0, 0))
        screen.blit(dist_text, (20, 55))

        if player.crashed:
            crash_text = font.render("Game Over! Press R to Restart", True, (255, 0, 0))
            screen.blit(crash_text, (WIDTH // 2 - crash_text.get_width() // 2, HEIGHT // 2 - 40))

            # Final stats
            final_score_text = font.render(f"Final Score: {player.score}", True, (0, 0, 0))
            final_dist_text = font.render(f"Total Distance: {int(player.distance // 10)} m", True, (0, 0, 0))

            screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2 + 10))
            screen.blit(final_dist_text, (WIDTH // 2 - final_dist_text.get_width() // 2, HEIGHT // 2 + 45))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
