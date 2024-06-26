import random
import pygame

from .my_master import MyMasterFighter
from .config import configmap
from .common import (
    Scene,
    res_manager,
    get_assets,
    Colors,
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT,
)
from .flight_unit import FlightUnit
from .actors import (
    Background,
    Meteor,
    Particle,
    ProgressRect,
    ShockParticle,
)


IS_FULLSCREEN = configmap["fullscreen"]


class StarFetchScene(Scene):

    __name__ = "StarFetchScene"

    def __init__(self, manager, clock):
        super().__init__(manager)
        self.clock = clock

    def on_enter(self, **kwargs):
        self.myf_channel = pygame.mixer.Channel(1)
        self.title_font = pygame.font.Font(None, 30)
        self.subtitle_font = pygame.font.Font(None, 22)
        self.countdown = configmap["game_time"]
        self.my_support_delay = 0
        self.my_score = 0
        self.ufo_score = 0
        self.my_score_step = configmap["my_score_step"]
        self.ufo_score_step = configmap["ufo_score_step"]
        self.task_score = configmap["task_level"]["starfetch"]["target_score"]
        # 可以出动的无人战斗机总数
        self.myf_slave_total = configmap["task_level"]["starfetch"]["slave_total"]
        self.unit_collision_cooldown = configmap["unit_collision_cooldown"]
        self.unit_collision_cooldowns = {}

        self.ufo_limit = configmap["task_level"]["starfetch"]["ufo_slave_limit"]
        self.myf_limit = configmap["myf_slave"]["min_limit"]

        self.myf_master_fire1_active = False
        self.myf_master_fire2_active = False
        self.myf_master_fire3_active = False
        self.myf_master_x_position = 0
        self.myf_master_y_position = 0
        self.my_master_fighter_target_position = pygame.math.Vector2()
        self.using_keyboard = True
        self.using_touch = False
        self.fetch_total = 0
        self.kills = 0

        self.setup_background()
        self.setup_groups()
        self.setup_events()
        self.create_actors()
        self.play_bgm()

    def setup_background(self):
        self.background = Background([0, 0], configmap["background"])
        self.bggroup = pygame.sprite.Group()
        self.bggroup.add(self.background)

    def update_my_socre(self, score_value):
        self.my_score += score_value
        if score_value > 0:
            self.my_master_fighter.upgrade_points += score_value / 5
        if self.my_score < 0:
            self.my_score = 0

    def update_ufo_socre(self, score_value):
        self.ufo_score += score_value
        if self.ufo_score < 0:
            self.ufo_score = 0

    def play_bgm(self):
        """播放背景音乐""" ""
        pygame.mixer.music.load(get_assets(configmap["bgm"]["sound"]))
        pygame.mixer.music.set_volume(configmap["bgm"]["sound_volume"])
        pygame.mixer.music.play(-1)

    def setup_groups(self):
        # 粒子组
        self.particles = pygame.sprite.Group()
        self.shock_particles = pygame.sprite.Group()
        # 我方炮弹组
        self.my_bullets = pygame.sprite.Group()
        # 敌方炮弹组
        self.ufo_bullets = pygame.sprite.Group()
        # 我方飞行单位组
        self.my_flight_units = pygame.sprite.Group()
        # 敌方飞行单位组
        self.ufo_units = pygame.sprite.Group()
        self.layout_units = pygame.sprite.Group()
        self.meteor_group = pygame.sprite.Group()

    def create_actors(self):
        # 创建敌方飞行单位
        self.ufo_master = FlightUnit.get_ufo_slave()
        self.ufo_units.add(self.ufo_master)
        self.my_master_fighter = MyMasterFighter(configmap["myf_master"], scene=self)
        self.my_flight_units.add(self.my_master_fighter)

        self.my_master_upstate = ProgressRect(
            DISPLAY_WIDTH, 4, 0, y=DISPLAY_HEIGHT - 70
        )
        self.layout_units.add(self.my_master_upstate)

    def setup_events(self):
        # 创建一个计时器事件
        self.TIMEREVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.TIMEREVENT, 1000)

        # 创建一个UFO开火计时器事件
        self.UFO_FIRE_TIMEREVENT = pygame.USEREVENT + 2
        pygame.time.set_timer(self.UFO_FIRE_TIMEREVENT, millis=250)

        # UFO Slave 进场事件
        self.SUFO_TIMEREVENT = pygame.USEREVENT + 4
        pygame.time.set_timer(self.SUFO_TIMEREVENT, 3000)

        self.MY_FIGHTER_FIRE_TIMEREVENT = pygame.USEREVENT + 6
        pygame.time.set_timer(self.MY_FIGHTER_FIRE_TIMEREVENT, 250)

        self.SWITCH_BG_TIMEREVENT = pygame.USEREVENT + 7
        pygame.time.set_timer(self.SWITCH_BG_TIMEREVENT, 30000)

        self.METEOR_EVENT = pygame.USEREVENT + 10
        pygame.time.set_timer(self.METEOR_EVENT, 3000)

    def create_hit_particle(self, actor_obj, num):
        for _ in range(int(num)):
            particle = Particle(
                actor_obj.rect.x + actor_obj.rect.width // 2,
                actor_obj.rect.y + 10,
                Colors.white,
            )
            self.particles.add(particle)

    def create_uhit_particle(self, actor_obj, num):
        for _ in range(int(num)):
            particle = Particle(
                actor_obj.rect.x + actor_obj.rect.width // 2,
                actor_obj.rect.y + 10,
                Colors.yellow,
                speed_range=(0.1, 3),
            )
            self.particles.add(particle)

    def create_hit_shock_particle(self, actor_obj, num):
        blast_sound = res_manager.load_sound("sounds/fire_blast.ogg")
        self.myf_channel.play(blast_sound)
        for _ in range(int(num)):
            particle = ShockParticle(
                actor_obj.rect.x + actor_obj.rect.width // 2,
                actor_obj.rect.y + actor_obj.rect.height // 2,
                random.choice([Colors.orange_light, Colors.orange, Colors.yellow]),
                speed=1.5,
            )
            self.shock_particles.add(particle)

    def myf_fire_level1(self):
        """发射1级炮弹"""
        self.my_master_fighter.fire(
            self.my_bullets,
            "level1",
        )
        if self.my_master_fighter.level >= 5:
            self.my_master_fighter.trace_fire(
                self.my_bullets,
                [self.ufo_bullets],
                self.particles,
                "level3",
                trace_fire_delay=32,
            )

    def _proc_on_joyaxis_event(self, event):
        """手柄事件"""
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 0:
                self.myf_master_x_position = event.value
            elif event.axis == 1:
                self.myf_master_y_position = event.value
            # elif event.axis == 4 and event.value > 0.2:

        if event.type == pygame.JOYBUTTONUP:
            if event.button == 0:
                self.myf_master_fire1_active = False

        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:
                # 速射机炮
                self.myf_master_fire1_active = True
            elif event.button == 10:
                # 呼叫资源
                if self.my_support_delay == 0:
                    self._call_my_support()

    def _proc_check_joystick_fire_active(self):
        if self.myf_master_fire1_active:
            self.myf_fire_level1()

    def _proc_update_myf_master_position(self):
        # 这里假设 self.my_master_fighter.move 接受一个速度参数
        # 并根据这个速度连续移动角色
        # 你可能需要根据摇杆位置调整移动速度的实际值
        if abs(self.myf_master_x_position) > 0.1:
            self.my_master_fighter.move(self.myf_master_x_position, 0)
        if abs(self.myf_master_y_position) > 0.1:
            self.my_master_fighter.move(0, self.myf_master_y_position)

    def _proc_on_keydown(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.my_master_fighter.move(-1, 0)  # 向左移动
        if keys[pygame.K_RIGHT]:
            self.my_master_fighter.move(1, 0)  # 向右移动
        if keys[pygame.K_UP]:
            self.my_master_fighter.move(0, -1)  # 向上移动
        if keys[pygame.K_DOWN]:
            self.my_master_fighter.move(0, 1)  # 向下移动
        if keys[pygame.K_1]:
            self.myf_fire_level1()
        if keys[pygame.K_4]:
            if self.my_support_delay == 0:
                self._call_my_support()

        if keys[pygame.K_a]:
            self.auto_game = not self.auto_game
            self.my_master_fighter.reset_speed_x()

        if keys[pygame.K_f]:
            if pygame.display.is_fullscreen():
                self.screen = pygame.display.set_mode(
                    (DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.FULLSCREEN
                )
            else:
                self.screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))

    def _proc_on_event(self, event):
        if event.type == pygame.QUIT:
            self.manager.switch_scene("GameEndScene", title="Game Over")
            return
        elif event.type == self.TIMEREVENT:  # 如果是计时器事件
            self.countdown -= 1  # 倒计时减1
            if self.my_score > 50000:
                self.manager.switch_scene("GameEndScene", title="You Win!")
                return
            if self.my_master_fighter.life_value <= 0:
                self.manager.switch_scene("GameEndScene", title="You Lose!")
                return

            if self.my_support_delay > 0:
                self.my_support_delay -= 1

        elif event.type == self.METEOR_EVENT:
            for _ in range(random.choice([4, 5, 7, 9])):
                meteor = Meteor(
                    random.choice(["meteor_shard", "meteor_core"]), configmap["meteor"]
                )
                self.meteor_group.add(meteor)

        elif event.type == self.UFO_FIRE_TIMEREVENT:
            for ufo in self.ufo_units:
                directions = ["down"]
                if len(self.my_flight_units) > 1:
                    directions = [
                        "down",
                        "down",
                        "left",
                        "down",
                        "right",
                        "down",
                    ]

                ufo.fire(
                    group=self.ufo_bullets,
                    direction=random.choice(directions),
                    target_groups=[self.my_flight_units, self.my_bullets],
                    particle_group=self.particles,
                )

        elif event.type == self.MY_FIGHTER_FIRE_TIMEREVENT:
            for myf in self.my_flight_units:
                if myf.type == "myf_slave":
                    myf.fire(
                        group=self.my_bullets,
                        direction=(
                            "left" if myf.rect.x > DISPLAY_WIDTH // 2 else "right"
                        ),
                        target_groups=[
                            self.ufo_units,
                            self.ufo_bullets,
                        ],
                        particle_group=self.particles,
                    )

        elif event.type == self.SUFO_TIMEREVENT:
            # UFO 自动呼叫支援
            self._auto_ufo_support()

        # elif event.type == pygame.MOUSEMOTION:
        #     # 鼠标移动事件
        #     self.my_master_fighter.rect.centerx = event.pos[0]
        #     self.my_master_fighter.rect.centery = event.pos[1]
        #     self.myf_fire_level1()

        elif event.type == pygame.FINGERDOWN or event.type == pygame.FINGERMOTION:
            self.using_touch = True
            self.my_master_fighter_target_position.x = event.x * DISPLAY_WIDTH
            self.my_master_fighter_target_position.y = (
                event.y * DISPLAY_HEIGHT - self.my_master_fighter.rect.height // 2
            )
            self.myf_fire_level1()
        if event.type == pygame.FINGERUP or event.type == pygame.FINGERDOWN:
            if self.call_support_button.click(event, (event.x, event.y)):
                self._call_my_support()

    def move_fighter_towards_target(self):
        if not self.using_touch:
            return
        # 逐渐移动战斗机到目标位置，使用一个简单的线性插值
        if (
            self.my_master_fighter.rect.centerx
            != self.my_master_fighter_target_position.x
        ):
            self.my_master_fighter.rect.centerx += (
                self.my_master_fighter_target_position.x
                - self.my_master_fighter.rect.centerx
            ) * 0.1
        if (
            self.my_master_fighter.rect.centery
            != self.my_master_fighter_target_position.y
        ):
            self.my_master_fighter.rect.centery += (
                self.my_master_fighter_target_position.y
                - self.my_master_fighter.rect.centery
            ) * 0.1

    def on_ufo_killed(self):
        self.kills += 1

    def _auto_ufo_support(self):
        score_cast = configmap["task_level"]["starfetch"]["ufo_slave_cost"]
        if self.ufo_score >= score_cast and len(self.ufo_units) < self.ufo_limit:
            sufo = FlightUnit.get_ufo_slave()
            sufo.on_killed = self.on_ufo_killed
            self.ufo_score -= score_cast
            if self.ufo_score < 0:
                self.ufo_score = 0
            self.ufo_units.add(sufo)

    def _call_my_support(self):
        score_cast = configmap["myf_slave"]["score_cast"]
        if (
            self.my_score >= score_cast
            and self.myf_slave_total > 0
            and len(self.my_flight_units) - 1 < self.myf_limit
        ):
            self.myf_slave_total -= 1
            self.my_support_delay = 3
            my_support = FlightUnit.get_my_slave_fighter()
            self.update_my_socre(-score_cast)
            self.my_flight_units.add(my_support)

    def check_collision_cooldown(self, obja, objb):
        # 碰撞冷却检测
        collision_key = (min(id(obja), id(objb)), max(id(obja), id(objb)))
        current_time = pygame.time.get_ticks()
        last_collision_time = self.unit_collision_cooldowns.get(collision_key, 0)
        if current_time - last_collision_time > self.unit_collision_cooldown:
            self.unit_collision_cooldowns[collision_key] = current_time
            return True
        return False

    def _proc_on_collisions(self):
        """处理碰撞检测, 伤害值， 分数值更新"""
        # 检测我方炮弹与UFO单位的碰撞
        collisions = pygame.sprite.groupcollide(
            self.my_bullets, self.ufo_units, False, False
        )
        for my_bullet, hit_ufo_units in collisions.items():
            for ufo_unit in hit_ufo_units:
                ufo_unit.hit(my_bullet.damage)
                self.create_hit_particle(ufo_unit, my_bullet.damage * 2)
                self.update_my_socre(my_bullet.damage // self.my_score_step)
                my_bullet.kill()

        # 检测UFO炮弹与我方飞行单位的碰撞
        ucollisions = pygame.sprite.groupcollide(
            self.ufo_bullets, self.my_flight_units, True, False
        )

        for u_bullet, hit_my_units in ucollisions.items():
            for my_unit in hit_my_units:
                my_unit.hit(u_bullet.damage)
                self.create_hit_particle(my_unit, u_bullet.damage)
                self.update_ufo_socre(u_bullet.damage // self.ufo_score_step)

        # 检测我方炮弹与UFO炮弹的碰撞
        mbub_collisions = pygame.sprite.groupcollide(
            self.my_bullets, self.ufo_bullets, True, True
        )
        for myb, ubs in mbub_collisions.items():
            for ub in ubs:
                self.create_hit_particle(ub, 2)

        # 检测我方飞行单位与UFO单位的碰撞
        xcollisions = pygame.sprite.groupcollide(
            self.my_flight_units, self.ufo_units, False, False
        )
        for myf, uflist in xcollisions.items():
            for uf in uflist:
                myf.dodge_fighter(uf)
                uf.dodge_fighter(myf)
                if self.check_collision_cooldown(myf, uf):
                    self.create_uhit_particle(uf, 50)
                    myf.hit(10)
                    uf.hit(10)
                    blast_sound = res_manager.load_sound("sounds/fire_blast.ogg")
                    blast_sound.set_volume(0.8)
                    blast_sound.play()
                    self.update_my_socre(10)
                    self.update_ufo_socre(10)

        # 检测我方飞行单位与陨石核心的碰撞
        mcollisions = pygame.sprite.groupcollide(
            self.my_flight_units, self.meteor_group, False, False
        )
        for myf, mlist in mcollisions.items():
            for met in mlist:
                self.update_my_socre(met.score_value)
                if met.type == "meteor_shard":
                    if self.check_collision_cooldown(myf, met):
                        myf.hit(met.damage)
                        self.create_hit_shock_particle(myf, 30)
                        myf.dodge_fighter(met)
                elif met.type == "meteor_core":
                    self.my_master_fighter.light()
                    starfetch_sound = res_manager.load_sound("sounds/starfetch.ogg")
                    self.myf_channel.play(starfetch_sound)
                    self.fetch_total += 1

                met.kill()

        # 检测我方炮弹与陨石核心的碰撞
        mbcollisions = pygame.sprite.groupcollide(
            self.my_bullets, self.meteor_group, True, False
        )
        for myb, mlist in mbcollisions.items():
            for met in mlist:
                if met.type == "meteor_shard":
                    met.hit(myb.damage)
                    filehit_sound = res_manager.load_sound("sounds/firehit.ogg")
                    filehit_sound.set_volume(0.8)
                    filehit_sound.play()
                    self.create_hit_particle(met, 10)

    def _proc_draw_texts(self, screen):
        #################### 在左下角绘制倒计时
        mins, secs = divmod(self.countdown, 60)
        timer_str = "{:02d}:{:02d}".format(mins, secs)
        countdown_text = self.title_font.render(str(timer_str), True, Colors.white)
        fps_text = self.subtitle_font.render(
            f"FPS:{round(self.clock.get_fps())}", True, Colors.white
        )
        screen.blit(
            countdown_text, (10, screen.get_height() - countdown_text.get_height() - 36)
        )
        screen.blit(fps_text, (10, screen.get_height() - fps_text.get_height() - 10))

        #################### 在中间显示战斗机 HP
        fighter_life_text = self.title_font.render(
            f"OUR/{round(self.my_master_fighter.level)} : {round(self.my_master_fighter.life_value)} <> SCORE: {round(self.my_score)}/{self.task_score}",
            True,
            Colors.red,
        )
        screen.blit(
            fighter_life_text,
            (
                100,
                screen.get_height() - fighter_life_text.get_height() - 36,
            ),
        )

        fighter_recharge_text = self.subtitle_font.render(
            f"Shield: {round(self.my_master_fighter.shield_value)}", True, Colors.white
        )
        screen.blit(
            fighter_recharge_text,
            (
                100,
                screen.get_height() - fighter_recharge_text.get_height() - 10,
            ),
        )

        status_text = self.subtitle_font.render(
            f"Acquired: {self.fetch_total}     Kills: {self.kills}", True, Colors.white
        )
        screen.blit(
            status_text,
            (
                200,
                screen.get_height() - status_text.get_height() - 10,
            ),
        )

    def update(self):

        # 检测键盘
        self._proc_on_keydown()
        self._proc_check_joystick_fire_active()
        self._proc_update_myf_master_position()
        self.move_fighter_towards_target()

        # 碰撞检测
        self._proc_on_collisions()

        # 自动游戏
        # if self.auto_game:
        #     self.my_master_fighter.auto_move()

        # 更新精灵组
        self.particles.update()
        self.my_bullets.update()
        self.ufo_bullets.update()
        self.shock_particles.update()
        self.my_flight_units.update()
        self.ufo_units.update()
        self.my_master_upstate.update(
            round(self.my_master_fighter.upgrade_points),
            round(self.my_master_fighter.level * self.my_master_fighter.upgrade_cast),
        )
        self.meteor_group.update()

    def draw(self, screen):
        # 绘制背景
        self.background.update()
        screen.blit(
            self.background.image,
            (self.background.rect.x, self.background.rect.y),
        )
        screen.blit(
            self.background.image,
            (
                self.background.rect.x,
                self.background.rect.y - self.background.rect.height,
            ),
        )
        # 绘制精灵组
        self.my_flight_units.draw(screen)
        for unit in self.my_flight_units:
            unit.draw_health_bar(screen)

        self.ufo_units.draw(screen)
        for unit in self.ufo_units:
            unit.draw_health_bar(screen)

        self.my_bullets.draw(screen)
        self.ufo_bullets.draw(screen)

        self.meteor_group.draw(screen)

        pygame.draw.rect(screen, (0, 0, 0), (0, DISPLAY_HEIGHT - 70, DISPLAY_WIDTH, 70))
        self._proc_draw_texts(screen)

        self.layout_units.draw(screen)
        self.particles.draw(screen)
        self.shock_particles.draw(screen)

    def handle_events(self, events):
        for event in events:
            self._proc_on_event(event)
            self._proc_on_joyaxis_event(event)
