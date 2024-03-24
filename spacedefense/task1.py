import pygame
import random
import math
import os
from spacedefense import DISPLAY_WIDTH, DISPLAY_HEIGHT, GAME_TIME, get_assets
from spacedefense.roles import (
    UFORole,
    MyRole,
    Particle,
    Fighter,
    Bullet,
    Stripe,
    UfoBullet,
)


def main():
    # 初始化pygame
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(get_assets("bgm1.mp3"))
    pygame.mixer.music.play(-1)  # -1表示无限循环

    game_win = False

    # 设置窗口大小
    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))

    # 加载声音文件
    sound_fire = pygame.mixer.Sound(get_assets("fire.mp3"))  # 加载发射声音
    sound_firehit = pygame.mixer.Sound(get_assets("firehit.wav"))  # 加载发射命中声音
    sound_sufo_join = pygame.mixer.Sound(get_assets("sufo_join.mp3"))  # 加载UFO进场声音

    font = pygame.font.Font(None, size=64)  # None表示使用pygame默认字体，36是字体大小
    # 创建一个计时器事件
    TIMEREVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(TIMEREVENT, 1000)  # 1000毫秒（1秒）触发一次

    # 创建一个UFO计时器事件
    UFO_TIMEREVENT = pygame.USEREVENT + 2
    pygame.time.set_timer(UFO_TIMEREVENT, 800)  # 800毫秒触发一次

    # 创建一个UFO计时器事件
    SUFO_TIMEREVENT = pygame.USEREVENT + 3
    pygame.time.set_timer(SUFO_TIMEREVENT, 2000)  # 600毫秒触发一次

    # 初始化倒计时
    countdown = GAME_TIME

    # 发射延迟计数器
    fire_delay = 0

    # UFO图片
    ufo_image = pygame.image.load(get_assets("ufo.png"))
    ufo_loss_image = pygame.image.load(get_assets("ufo_loss.png"))
    sufo_image = pygame.image.load(get_assets("sufo.png"))
    # 战斗机图片
    fighter_image = pygame.image.load(get_assets("fighter.png"))
    fighter_loss_image = pygame.image.load(get_assets("fighter_loss.png"))
    sfighter_image = pygame.image.load(get_assets("sfighter.png"))

    # 爆炸效果粒子
    particles = []
    # 炮弹
    bullets = []
    # UFO炮弹
    ufo_bullets = []

    def add_particles(obj, num):
        for _ in range(num):  # 创建粒子
            dx = random.uniform(-1, 1)  # 粒子的水平速度
            dy = random.uniform(-1, 1)  # 粒子的垂直速度
            particles.append(Particle(obj.x + 30, obj.y + 30, dx, dy))

    # 创建飞船
    ufo = UFORole("UFO", 2000, ufo_image)
    sufo = UFORole("SUFO", 500, sufo_image)

    # 创建战斗机
    fighter = Fighter("Fighter", 500, fighter_image)
    sfighter = MyRole("SFighter", 500, sfighter_image)

    stripes = [
        Stripe(i * 20, (255, 255, 255) if i % 2 == 0 else (0, 0, 0))
        for i in range(10000)
    ]

    is_sufo = False
    is_sfighter = False

    # 主游戏循环
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == TIMEREVENT:  # 如果是计时器事件
                countdown -= 1  # 倒计时减1
                if countdown < 1:  # 如果倒计时结束，重置为10
                    running = False
            elif event.type == UFO_TIMEREVENT:
                ufo_bullets.append(UfoBullet(ufo.x + ufo.width // 2, ufo.y + 50))
            elif event.type == SUFO_TIMEREVENT:
                if is_sufo:
                    ufo_bullets.append(UfoBullet(sufo.x + sufo.width // 2, sufo.y + 50))

        if ufo.life_value <= 0 and fighter.life_value > 0:
            game_win = True
            ufo.image = ufo_loss_image
            running = False
        elif fighter.life_value <= 0:
            game_win = False
            fighter.image = fighter_loss_image
            running = False

        if ufo.get_life_value() <= 1500 and sufo.get_life_value() > 0 and not is_sufo:
            sound_sufo_join.play()
            is_sufo = True

        if sufo.get_life_value() <= 0:
            is_sufo = False

        if sfighter.get_life_value() <= 0:
            is_sfighter = False

        # UFO进场， 移动UFO
        ufo.move()
        if is_sufo:
            sufo.move()
        if is_sfighter:
            sfighter.move()

        # 处理键盘输入
        keys = pygame.key.get_pressed()
        if keys[pygame.K_3] and not is_sfighter and sfighter.get_life_value() > 0:
            is_sfighter = True
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            fighter.move(-1)  # 向左移动
        if keys[pygame.K_RIGHT]:
            fighter.move(1)  # 向右移动
        if fire_delay == 0:  # 只有当发射延迟计数器为0时，才允许发射新的炮弹
            if keys[pygame.K_1]:
                bullets.append(Bullet(fighter.x, fighter.y, False))  # 发射小号炮弹
                sound_fire.play()  # 播放发射声音
                fire_delay = 10  # 设置发射延迟计数器为30
            if keys[pygame.K_2]:
                bullets.append(Bullet(fighter.x, fighter.y, True))  # 发射大型炮弹
                sound_fire.play()  # 播放发射声音
                fire_delay = 25  # 设置发射延迟计数器为60

        # 在每个游戏循环中减少发射延迟计数器的值
        if fire_delay > 0:
            fire_delay -= 1

        # 绘制背景光栅
        for stripe in stripes:
            stripe.move()

        screen.fill((0, 0, 0))  # 用黑色填充屏幕
        for stripe in stripes:
            pygame.draw.rect(
                screen, stripe.color, (stripe.x, 0, 50, 768)
            )  # 绘制每个条纹

        # 在游戏循环中移动和绘制粒子
        for particle in particles[:]:
            # 使用切片来复制列表，这样就可以在遍历过程中修改列表
            particle.move()
            particle.draw(screen)
            if particle.lifetime <= 0:  # 如果粒子的生命周期已经结束
                particles.remove(particle)  # 从列表中移除粒子

        # 我方炮弹
        for bullet in bullets:
            bullet.move()
            # 绘制炮弹
            pygame.draw.circle(
                screen, (255, 0, 0), (int(bullet.x + 30), int(bullet.y)), bullet.radius
            )

            if bullet.check_collision(ufo):
                sound_firehit.play()  # 播放碰撞声音
                ufo.life_value -= 10 if bullet.is_big else 2
                bullets.remove(bullet)
                pnum = 50 if bullet.is_big else 30
                add_particles(ufo, pnum)

            if bullet.check_collision(sufo):
                sound_firehit.play()  # 播放碰撞声音
                sufo.life_value -= 10 if bullet.is_big else 2
                if bullet in bullets:
                    bullets.remove(bullet)
                pnum = 50 if bullet.is_big else 30
                add_particles(sufo, pnum)
        
        ############# 支援战斗机战斗伤害
        if (
            is_sfighter
            and sfighter.get_life_value() > 0
            and sfighter.check_collision(ufo)
        ):
            sound_firehit.play()
            ufo.life_value -= 1
            sfighter.life_value -= 1
            add_particles(ufo, 50)

        if (
            is_sfighter
            and sfighter.get_life_value() > 0
            and is_sufo
            and sfighter.check_collision(sufo)
        ):
            sound_firehit.play()
            sufo.life_value -= 1
            sfighter.life_value -= 1
            add_particles(sufo, 50)

        ############# 敌方炮弹
        for ubullet in ufo_bullets:
            ubullet.move()
            pygame.draw.circle(
                screen, (255, 255, 0), (int(ubullet.x), int(ubullet.y)), ubullet.radius
            )
            if ubullet.check_collision(fighter):
                sound_firehit.play()
                fighter.life_value -= 10
                ufo_bullets.remove(ubullet)
                add_particles(fighter, 50)
            if is_sfighter and ubullet.check_collision(sfighter):
                sound_firehit.play()
                sfighter.life_value -= 10
                if ubullet in ufo_bullets:
                    ufo_bullets.remove(ubullet)
                add_particles(sfighter, 50)

        if is_sufo:
            screen.blit(sufo.image, (sufo.x, sufo.y))  # 绘制飞船

        if is_sfighter:
            screen.blit(sfighter.image, (sfighter.x, sfighter.y))

        screen.blit(ufo.image, (ufo.x, ufo.y))  # 绘制飞船
        screen.blit(fighter.image, (fighter.x, fighter.y))  # 绘制战斗机

        #################### 在左下角绘制倒计时
        mins, secs = divmod(countdown, 60)
        timer_str = "{:02d}:{:02d}".format(mins, secs)
        countdown_text = font.render(
            str(timer_str), True, (255, 255, 255)
        )  # 创建倒计时文本
        screen.blit(
            countdown_text, (20, screen.get_height() - countdown_text.get_height() - 20)
        )  # 绘制倒计时文本

        #################### 在中间显示战斗机 HP
        fighter_life_text = font.render(
            f"Fighter: {fighter.get_life_value()}", True, (255, 255, 255)
        )  # 创建分数文本
        screen.blit(
            fighter_life_text,
            (
                screen.get_width() / 2,
                screen.get_height() - fighter_life_text.get_height() - 20,
            ),
        )  # 绘制分数文本

        #################### 在右下角显示UFO HP
        ufo_life_text = font.render(
            f"UFO: {ufo.get_life_value()}", True, (255, 255, 255)
        )  # 创建分数文本
        screen.blit(
            ufo_life_text,
            (
                screen.get_width() - ufo_life_text.get_width() - 20,
                screen.get_height() - ufo_life_text.get_height() - 20,
            ),
        )  # 绘制分数文本

        pygame.display.flip()  # 更新显示

    ########################################################
    game_font = pygame.font.Font(None, 200)  # 创建一个字体对象
    if game_win:
        # 如果游戏胜利，显示胜利文本
        text = game_font.render("You Win!", True, (255, 0, 0))
        textpos = text.get_rect(
            centerx=screen.get_width() / 2, centery=screen.get_height() / 2
        )
        screen.blit(text, textpos)
    else:
        # 如果游戏失败，显示失败文本
        text = game_font.render("Game Over!", True, (0, 255, 0))
        textpos = text.get_rect(
            centerx=screen.get_width() / 2, centery=screen.get_height() / 2
        )
        screen.blit(text, textpos)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            pygame.quit()
            return

        pygame.display.flip()


if __name__ == "__main__":
    main()
