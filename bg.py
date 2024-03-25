import pygame
import os

# 初始化 Pygame
pygame.init()

# 设置屏幕
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Moving Background")

# 加载背景图片
background_image = pygame.image.load("spacedefense/assets/vgird.png").convert()
background_rect = background_image.get_rect()

# 设置背景初始位置
background_y = 0

# 游戏循环
running = True
clock = pygame.time.Clock()

while running:
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 更新背景位置
    background_y += 1
    if background_y >= background_rect.height:
        background_y = 0

    # 绘制背景
    screen.blit(background_image, (0, background_y))
    screen.blit(background_image, (0, background_y - background_rect.height))

    # 更新显示
    pygame.display.flip()
    clock.tick(60)

# 退出游戏
pygame.quit()
