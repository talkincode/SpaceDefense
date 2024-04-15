import pygame
import math
from pygame.locals import *

# 初始化Pygame
pygame.init()

# 设置屏幕大小
width, height = 800, 600
screen = pygame.display.set_mode((width, height))

# 定义颜色
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# 太阳系中心（屏幕中心）
sun_pos = (width // 2, height // 2)

# 加载太阳和行星图像
sun_image = pygame.image.load('sun.png')
planet_images = [
    pygame.image.load('mercury.png'),
    pygame.image.load('venus.png'),
    # 加载其他行星图片
]

class Planet(pygame.sprite.Sprite):
    def __init__(self, image, orbit_size, orbit_speed, distance_from_sun):
        super().__init__()
        self.original_image = image
        self.image = image
        self.rect = self.image.get_rect()
        self.orbit_size = orbit_size
        self.orbit_speed = orbit_speed
        self.distance_from_sun = distance_from_sun
        self.angle = 0

    def update(self):
        # 更新行星位置
        self.angle = (self.angle + self.orbit_speed) % 360
        self.rect.centerx = sun_pos[0] + math.cos(math.radians(self.angle)) * self.distance_from_sun
        self.rect.centery = sun_pos[1] + math.sin(math.radians(self.angle)) * self.orbit_size

        # 根据距离太阳的远近调整大小
        distance = math.sqrt((self.rect.centerx - sun_pos[0]) ** 2 + (self.rect.centery - sun_pos[1]) ** 2)
        scale = max(0.4, 1 - (distance / (width // 2)))
        width = int(self.original_image.get_width() * scale)
        height = int(self.original_image.get_height() * scale)
        self.image = pygame.transform.scale(self.original_image, (width, height))

# 创建行星实例
planets = pygame.sprite.Group(
    Planet(planet_images[0], 40, 0.2, 100),
    Planet(planet_images[1], 60, 0.1, 150),
    # 添加其他行星实例
)

clock = pygame.time.Clock()

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    screen.fill((0, 0, 0))
    screen.blit(sun_image, sun_image.get_rect(center=sun_pos))
    planets.update()
    planets.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
