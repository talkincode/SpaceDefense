# coding:utf-8

import pygame
import random
import math
import os
from concurrent.futures import ThreadPoolExecutor
from threading import RLock
from spacedefense import DISPLAY_WIDTH, DISPLAY_HEIGHT, GAME_TIME, get_assets
from spacedefense.roles import (
    UFORole,
    MyRole,
    Particle,
    Fighter,
    Bullet,
    XStripe,
    YStripe,
    UfoBullet,
)


class GameTask1(object):

    # 0: 未进场 1: 进场
    STAGE_FIGHT_PRE = 1
    STAGE_FIGHT_START = 2
    STAGE_FIGHT_INTERIM = 3
    STAGE_FIGHT_ANGRY = 4
    STAGE_FIGHT_END = 5

    def __init__(self):
        self.taskpool = ThreadPoolExecutor(max_workers=3)
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.set_reserved(1)
        self.chorus_channel = pygame.mixer.Channel(0)
        self.screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.title_font = pygame.font.Font(None, size=64)
        self.game_win = False
        self.countdown = GAME_TIME
        # 发射延迟计数器
        self.fire_delay = 0
        # 爆炸效果粒子
        self.particles = []
        # 炮弹
        self.bullets = []
        # UFO炮弹
        self.ufo_bullets = []

        # 支援单位是否进入战场
        self.is_sufo = False
        self.is_sfighter = False

        # 背景光栅
        self.is_xbg = True
        self.is_ybg = False
        self.is_girdbg = False
        self.stage_fight = GameTask1.STAGE_FIGHT_PRE

        # 主游戏循环
        self.running = True
        self.set_events()
        self.load_images()
        self.load_sounds()
        self.create_roles()
        self.create_stripes()

    def load_sounds(self):
        # 加载声音文件
        self.sufo_join_sound = pygame.mixer.Sound(get_assets("sufo_join.mp3"))
        self.sfighter_join_sound = pygame.mixer.Sound(get_assets("sfighter_join.mp3"))
        # 加载发射声音
        self.sound_fire = pygame.mixer.Sound(get_assets("fire.mp3"))
        self.sound_ufire = pygame.mixer.Sound(get_assets("ufire.mp3"))
        self.sound_fire.set_volume(0.3)
        self.sound_ufire.set_volume(0.3)
        # 加载发射命中声音
        self.sound_fire_blast = pygame.mixer.Sound(get_assets("fire_blast.mp3"))
        self.sound_firehit = pygame.mixer.Sound(get_assets("firehit.mp3"))
        self.sound_firehit.set_volume(0.5)
        self.sound_ufirehit = pygame.mixer.Sound(get_assets("ufirehit.mp3"))
        self.sound_ufirehit.set_volume(0.6)
        self.sound_ufirehit = pygame.mixer.Sound(get_assets("ufirehit.mp3"))
        # 事件声音
        self.sound_stage_start = pygame.mixer.Sound(get_assets("stage_start.mp3"))
        self.sound_stage_mid = pygame.mixer.Sound(get_assets("stage_mid.mp3"))
        self.sound_stage_angry = pygame.mixer.Sound(get_assets("stage_angry.mp3"))
        self.sound_stage_end_win = pygame.mixer.Sound(get_assets("stage_end_win.mp3"))
        self.sound_stage_end_loss = pygame.mixer.Sound(get_assets("stage_end_loss.mp3"))

    def load_images(self):
        # UFO图片
        self.ufo_image = pygame.image.load(get_assets("ufo.png"))
        self.ufo_loss_image = pygame.image.load(get_assets("ufo_loss.png"))
        self.sufo_image = pygame.image.load(get_assets("sufo.png"))
        # 战斗机图片
        self.fighter_image = pygame.image.load(get_assets("fighter.png"))
        self.fighter_loss_image = pygame.image.load(get_assets("fighter_loss.png"))
        self.sfighter_image = pygame.image.load(get_assets("sfighter.png"))
        self.stage_pre_image = pygame.image.load(get_assets("stage_pre.png"))

    def create_roles(self):
        # 创建飞船
        self.ufo = UFORole("UFO", 5000, self.ufo_image)
        self.sufo = UFORole("SUFO", 500, self.sufo_image)

        # 创建战斗机
        self.fighter = Fighter("Fighter", 1500, self.fighter_image)
        self.sfighter = MyRole("SFighter", 700, self.sfighter_image)

    def create_stripes(self):
        self.xstripes = [
            XStripe(i * 30, (255, 255, 255) if i % 2 == 0 else (0, 0, 0))
            for i in range(100)
        ]
        self.ystripes = [
            YStripe(i * 30, (0, 0, 0) if i % 2 == 0 else (255, 255, 255))
            for i in range(100)
        ]
        self.gird_bg_image = pygame.image.load(get_assets("vgird.png")).convert()
        self.gird_ng_rect = self.gird_bg_image.get_rect()
        self.gird_bg_y = 0

    def play_bgm(self):
        pygame.mixer.music.load(get_assets("bgm1.mp3"))
        pygame.mixer.music.play(-1)

    def set_events(self):
        # 创建一个计时器事件
        self.TIMEREVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.TIMEREVENT, 1000)  # 1000毫秒（1秒）触发一次

        # 创建一个UFO计时器事件
        self.UFO_TIMEREVENT = pygame.USEREVENT + 2
        pygame.time.set_timer(self.UFO_TIMEREVENT, 500)  # 800毫秒触发一次
        self.XUFO_TIMEREVENT = pygame.USEREVENT + 3
        pygame.time.set_timer(self.XUFO_TIMEREVENT, 200)
        # 创建一个UFO计时器事件
        self.SUFO_TIMEREVENT = pygame.USEREVENT + 4
        pygame.time.set_timer(self.SUFO_TIMEREVENT, 1000)

        self.SWITCH_BG_TIMEREVENT = pygame.USEREVENT + 5
        pygame.time.set_timer(self.SWITCH_BG_TIMEREVENT, 30000)

        self.STAGE_STATE_EVENT = pygame.USEREVENT + 10

    def switch_stripes(self):
        if self.is_xbg:
            self.is_xbg = False
            self.is_ybg = True
            self.is_girdbg = False
        elif self.is_ybg:
            self.is_xbg = False
            self.is_ybg = False
            self.is_girdbg = True
        elif self.is_girdbg:
            self.is_xbg = True
            self.is_ybg = False
            self.is_girdbg = False

    def change_stage_event(self, event):
        if event.state == GameTask1.STAGE_FIGHT_INTERIM:
            self.stage_fight = GameTask1.STAGE_FIGHT_INTERIM
            self.chorus_channel.play(self.sound_stage_mid)
        elif event.state == GameTask1.STAGE_FIGHT_ANGRY:
            self.stage_fight = GameTask1.STAGE_FIGHT_ANGRY
            self.chorus_channel.play(self.sound_stage_angry)

    def _add_particles(self, obj, num):
        for _ in range(num):  # 创建粒子
            dx = random.uniform(-1, 1)  # 粒子的水平速度
            dy = random.uniform(-1, 1)  # 粒子的垂直速度
            self.particles.append(Particle(obj.x + 30, obj.y + 30, dx, dy))

    def _proc_on_keydown(self):
        keys = pygame.key.get_pressed()

        # 我方支援战斗机进场
        if keys[pygame.K_3] and not self.is_sfighter and self.countdown <= 240:
            if self.sfighter.get_life_value() > 0:
                self.chorus_channel.play(self.sfighter_join_sound)
                self.is_sfighter = True
            elif self.countdown <= 60:
                self.sfighter.reset()
                self.chorus_channel.play(self.sfighter_join_sound)
                self.is_sfighter = True

        if keys[pygame.K_LEFT]:
            self.fighter.move(-1)  # 向左移动
        if keys[pygame.K_RIGHT]:
            self.fighter.move(1)  # 向右移动
        if keys[pygame.K_x]:
            self.is_xbg = True
            self.is_ybg = False
            self.is_girdbg = False
        if keys[pygame.K_y]:
            self.is_xbg = False
            self.is_ybg = True
            self.is_girdbg = False
        if keys[pygame.K_g]:
            self.is_xbg = False
            self.is_ybg = False
            self.is_girdbg = True
        if self.fire_delay == 0:  # 只有当发射延迟计数器为0时，才允许发射新的炮弹
            if keys[pygame.K_1]:
                self.bullets.append(
                    Bullet(self.fighter.x, self.fighter.y, False)
                )  # 发射小号炮弹
                self.sound_fire.play()
                self.fire_delay = 10  # 设置发射延迟计数器为30
            if keys[pygame.K_2]:
                self.bullets.append(
                    Bullet(self.fighter.x, self.fighter.y, True)
                )  # 发射大型炮弹
                self.sound_fire.play()
                self.fire_delay = 20  # 设置发射延迟计数器为60

    def _proc_on_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == self.TIMEREVENT:  # 如果是计时器事件
            self.countdown -= 1  # 倒计时减1
            if self.countdown < 1:  # 如果倒计时结束，重置为10
                self.running = False
        elif event.type == self.UFO_TIMEREVENT:
            self.ufo_bullets.append(
                UfoBullet(self.ufo.x + self.ufo.width // 2, self.ufo.y + 50)
            )
            self.sound_ufire.play()
        elif event.type == self.XUFO_TIMEREVENT:
            if self.countdown <= 60:
                self.ufo_bullets.append(
                    UfoBullet(self.ufo.x + self.ufo.width // 2, self.ufo.y + 50)
                )
        elif event.type == self.SUFO_TIMEREVENT:
            if self.is_sufo:
                self.ufo_bullets.append(
                    UfoBullet(self.sufo.x + self.sufo.width // 2, self.sufo.y + 50)
                )
        elif event.type == self.SWITCH_BG_TIMEREVENT:
            self.switch_stripes()
        elif event.type == self.STAGE_STATE_EVENT:
            self.change_stage_event(event)

    def _proc_check_role_lifetime(self):
        if self.ufo.life_value <= 0 and self.fighter.life_value > 0:
            self.game_win = True
            self.ufo.image = self.ufo_loss_image
            self.running = False
        elif self.fighter.life_value <= 0:
            self.game_win = False
            self.fighter.image = self.fighter_loss_image
            self.running = False

        if (
            self.ufo.get_life_value() <= 4000
            and self.sufo.get_life_value() > 0
            and not self.is_sufo
        ):
            self.chorus_channel.play(self.sufo_join_sound)
            self.is_sufo = True

        if self.is_sufo and self.sufo.get_life_value() <= 0:
            self.is_sufo = False

        if self.sfighter.get_life_value() <= 0:
            self.is_sfighter = False

    def _proc_fill_stripe(self):
        if self.is_xbg:
            # 绘制背景光栅
            for xstripe in self.xstripes:
                xstripe.move()
            self.screen.fill((0, 0, 0))  # 用黑色填充屏幕
            for stripe in self.xstripes:
                pygame.draw.rect(
                    self.screen, stripe.color, (stripe.x, 0, 50, DISPLAY_HEIGHT)
                )
        elif self.is_ybg:
            for ystripe in self.ystripes:
                ystripe.move()
            self.screen.fill((0, 0, 0))  # 用黑色填充屏幕
            for stripe in self.ystripes:
                pygame.draw.rect(
                    self.screen, stripe.color, (0, stripe.y, DISPLAY_WIDTH, 50)
                )
        elif self.is_girdbg:
            self.gird_bg_y += 1
            if self.gird_bg_y >= self.gird_ng_rect.height:
                self.gird_bg_y = 0
            self.screen.blit(self.gird_bg_image, (0, self.gird_bg_y))
            self.screen.blit(
                self.gird_bg_image, (0, self.gird_bg_y - self.gird_ng_rect.height)
            )

    def _proc_draw_bullets(self):
        # 我方炮弹
        for bullet in self.bullets:
            bullet.move()
            # 绘制炮弹
            pygame.draw.circle(
                self.screen,
                (255, 0, 0),
                (int(bullet.x + 30), int(bullet.y)),
                bullet.radius,
            )

            if bullet.check_collision(self.ufo):
                # self.sound_firehit.play()  # 播放碰撞声音
                self.sound_firehit.play()
                self.ufo.life_value -= 15 if bullet.is_big else 5
                self.bullets.remove(bullet)
                pnum = 50 if bullet.is_big else 30
                self._add_particles(self.ufo, pnum)

            if bullet.check_collision(self.sufo):
                self.sound_firehit.play()  # 播放碰撞声音
                self.sufo.life_value -= 15 if bullet.is_big else 5
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                pnum = 50 if bullet.is_big else 30
                self._add_particles(self.sufo, pnum)

    def _proc_draw_ufo_bullets(self):
        ############# 敌方炮弹
        for ubullet in self.ufo_bullets:
            ubullet.move()
            pygame.draw.circle(
                self.screen,
                (255, 255, 0),
                (int(ubullet.x), int(ubullet.y)),
                ubullet.radius,
            )
            if ubullet.check_collision(self.fighter):
                self.sound_ufirehit.play()
                self.fighter.life_value -= 10
                self.ufo_bullets.remove(ubullet)
                self._add_particles(self.fighter, 50)
            if self.is_sfighter and ubullet.check_collision(self.sfighter):
                self.sound_ufirehit.play()
                self.sfighter.life_value -= 10
                if ubullet in self.ufo_bullets:
                    self.ufo_bullets.remove(ubullet)
                self._add_particles(self.sfighter, 50)

    def _proc_draw_particles(self):
        # 在游戏循环中移动和绘制粒子
        for particle in self.particles[:]:
            # 使用切片来复制列表，这样就可以在遍历过程中修改列表
            particle.move()
            particle.draw(self.screen)
            if particle.lifetime <= 0:  # 如果粒子的生命周期已经结束
                self.particles.remove(particle)  # 从列表中移除粒子

    def _proc_check_sfighter(self):
        ############# 支援战斗机战斗伤害
        if (
            self.is_sfighter
            and self.sfighter.get_life_value() > 0
            and self.sfighter.check_collision(self.ufo)
        ):
            self.sound_fire_blast.play()
            self.ufo.life_value -= 1
            self.sfighter.life_value -= 1
            self._add_particles(self.ufo, 50)

        if (
            self.is_sfighter
            and self.sfighter.get_life_value() > 0
            and self.is_sufo
            and self.sfighter.check_collision(self.sufo)
        ):
            self.sound_fire_blast.play()
            self.sufo.life_value -= 1
            self.sfighter.life_value -= 1
            self._add_particles(self.sufo, 50)

    def _proc_draw_texts(self):
        #################### 在左下角绘制倒计时
        mins, secs = divmod(self.countdown, 60)
        timer_str = "{:02d}:{:02d}".format(mins, secs)
        countdown_text = self.title_font.render(str(timer_str), True, (255, 0, 0))
        self.screen.blit(
            countdown_text,
            (20, self.screen.get_height() - countdown_text.get_height() - 20),
        )

        #################### 在中间显示战斗机 HP
        fighter_life_text = self.title_font.render(
            f"Fighter: {self.fighter.get_life_value()}", True, (255, 0, 0)
        )
        self.screen.blit(
            fighter_life_text,
            (
                self.screen.get_width() / 2,
                self.screen.get_height() - fighter_life_text.get_height() - 80,
            ),
        )

        #################### 在中间显示战斗机 HP
        sfighter_life_text = self.title_font.render(
            f"Fighter-2: {self.sfighter.get_life_value()}", True, (255, 0, 0)
        )  # 创建分数文本
        self.screen.blit(
            sfighter_life_text,
            (
                self.screen.get_width() / 2,
                self.screen.get_height() - sfighter_life_text.get_height() - 20,
            ),
        )

        #################### 在右下角显示UFO HP
        ufo_life_text = self.title_font.render(
            f"UFO: {self.ufo.get_life_value()}", True, (255, 0, 0)
        )  # 创建分数文本
        self.screen.blit(
            ufo_life_text,
            (
                self.screen.get_width() - ufo_life_text.get_width() - 20,
                self.screen.get_height() - ufo_life_text.get_height() - 80,
            ),
        )
        #################### 在右下角显示SUFO HP
        sufo_life_text = self.title_font.render(
            f"UFO-2: {self.sufo.get_life_value()}", True, (255, 0, 0)
        )  # 创建分数文本
        self.screen.blit(
            sufo_life_text,
            (
                self.screen.get_width() - sufo_life_text.get_width() - 20,
                self.screen.get_height() - sufo_life_text.get_height() - 20,
            ),
        )
    
    def _proc_check_stage(self):
        """检查游戏阶段"""
        if (
            self.countdown <= 240
            and self.stage_fight == GameTask1.STAGE_FIGHT_START
        ):
            pygame.event.post(
                pygame.event.Event(
                    self.STAGE_STATE_EVENT, state=GameTask1.STAGE_FIGHT_INTERIM
                )
            )
        elif (
            self.countdown <= 62
            and self.stage_fight == GameTask1.STAGE_FIGHT_INTERIM
        ):
            pygame.event.post(
                pygame.event.Event(
                    self.STAGE_STATE_EVENT, state=GameTask1.STAGE_FIGHT_ANGRY
                )
            )
    

    def game_pre(self):
        pygame.mixer.music.load(get_assets("stage_pre.mp3"))
        pygame.mixer.music.play()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                break
            
            for _ in range(10):  # 创建粒子
                dx = random.uniform(-1, 1)  # 粒子的水平速度
                dy = random.uniform(-1, 1)  # 粒子的垂直速度
                self.particles.append(Particle(420, 260, dx, dy))
                
            self.screen.blit(self.stage_pre_image, (0, 0))
            
            for particle in self.particles[:]:
                # 使用切片来复制列表，这样就可以在遍历过程中修改列表
                particle.move()
                particle.draw(self.screen)
                if particle.lifetime <= 0:  # 如果粒子的生命周期已经结束
                    self.particles.remove(particle)  # 从列表中移除粒子
            
            pygame.display.flip()
            
        self.particles.clear()

    #######################################################
    ## start game
    #######################################################
    def start_game(self):
        """开始游戏"""
        self.game_pre()
        self.chorus_channel.play(self.sound_stage_start)
        self.stage_fight = GameTask1.STAGE_FIGHT_START
        self.running = True
        self.play_bgm()
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                self._proc_on_event(event)

            self._proc_check_role_lifetime()

            self._proc_check_stage()

            # UFO进场， 移动UFO
            self.ufo.move()
            if self.is_sufo:
                self.sufo.move()
            if self.is_sfighter:
                self.sfighter.move()

            # 处理键盘输入
            self._proc_on_keydown()

            # 在每个游戏循环中减少发射延迟计数器的值
            if self.fire_delay > 0:
                self.fire_delay -= 1

            self._proc_fill_stripe()

            self._proc_draw_particles()

            self._proc_draw_bullets()

            self._proc_check_sfighter()

            self._proc_draw_ufo_bullets()

            if self.is_sufo:
                self.screen.blit(
                    self.sufo.image, (self.sufo.x, self.sufo.y)
                )  # 绘制飞船

            if self.is_sfighter:
                self.screen.blit(
                    self.sfighter.image, (self.sfighter.x, self.sfighter.y)
                )

            # 绘制UFO
            self.screen.blit(self.ufo.image, (self.ufo.x, self.ufo.y))
            # 绘制战斗机
            self.screen.blit(self.fighter.image, (self.fighter.x, self.fighter.y))

            self._proc_draw_texts()

            pygame.display.flip()  # 更新显示
            clock.tick(120)

        self.game_stop()

    def game_stop(self):
        """游戏结束画面"""
        game_font = pygame.font.Font(None, 200)
        if self.game_win:
            # 如果游戏胜利，显示胜利文本
            text = game_font.render("You Win!", True, (255, 0, 0))
            textpos = text.get_rect(
                centerx=self.screen.get_width() / 2,
                centery=self.screen.get_height() / 2,
            )
            self.screen.blit(text, textpos)
            self.chorus_channel.play(self.sound_stage_end_win)
        else:
            # 如果游戏失败，显示失败文本
            text = game_font.render("Game Over!", True, (0, 0, 255))
            textpos = text.get_rect(
                centerx=self.screen.get_width() / 2,
                centery=self.screen.get_height() / 2,
            )
            self.screen.blit(text, textpos)
            self.chorus_channel.play(self.sound_stage_end_loss)

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


def main():
    task = GameTask1()
    task.start_game()


if __name__ == "__main__":
    main()
