import pygame
import random
import math
from spacedefense import DISPLAY_WIDTH, DISPLAY_HEIGHT


class UFORole:
    """外星人飞船"""

    def __init__(self, name: str, hp: int, image_obj: any):
        self.name = name
        self.life_value = hp
        self.x = random.randint(0, DISPLAY_WIDTH - 30)  # 随机初始化x坐标
        self.y = 30  # 将球的y坐标设置为固定值
        self.speed_x = random.randint(-3, 3)  # 在x方向上设置随机速度
        self.speed_y = random.randint(-3, 3)  # 在y方向上设置随机速度
        self.image = image_obj  # 加载图片
        self.width = self.image.get_width()  # 获取图片的宽度
        
    def get_life_value(self):
        if self.life_value < 0:
            return 0
        return self.life_value

    def move(self):
        self.x += self.speed_x  # 水平移动球
        self.y += self.speed_y  # 垂直移动球

        if self.x < 50:  # 如果球超出屏幕左边范围，反转x方向的速度
            self.speed_x = abs(random.randint(-3, 4))
        elif self.x > DISPLAY_WIDTH - 200:  # 如果球超出屏幕右边范围，反转x方向的速度
            self.speed_x = -abs(random.randint(-3, 4))

        if self.y < 50:  # 如果球超出屏幕上边范围，反转y方向的速度
            self.speed_y = abs(random.randint(-2, 2))
        elif self.y > 500:  # 如果球超出屏幕下边范围，反转y方向的速度
            self.speed_y = -abs(random.randint(-2, 2))


class MyRole:
    """我方支援单位"""

    def __init__(self,name: str, hp: int, image_obj: any):
        self.name = name
        self.life_value = hp
        self.x = random.randint(0, DISPLAY_WIDTH - 30)  # 随机初始化x坐标
        self.y = 30  # 将球的y坐标设置为固定值
        self.speed_x = random.randint(-3, 3)  # 在x方向上设置随机速度
        self.speed_y = random.randint(-3, 3)  # 在y方向上设置随机速度
        self.image = image_obj  # 加载图片
        self.width = self.image.get_width()  # 获取图片的宽度
    
    def get_life_value(self):
        if self.life_value < 0:
            return 0
        return self.life_value

    def move(self):
        self.x += self.speed_x  # 水平移动球
        self.y += self.speed_y  # 垂直移动球

        if self.x < 50:  # 如果球超出屏幕左边范围，反转x方向的速度
            self.speed_x = abs(random.randint(-3, 3))
        elif self.x > DISPLAY_WIDTH - 30:  # 如果球超出屏幕右边范围，反转x方向的速度
            self.speed_x = -abs(random.randint(-3, 3))

        if self.y < 50:  # 如果球超出屏幕上边范围，反转y方向的速度
            self.speed_y = abs(random.randint(-2, 2))
        elif self.y > DISPLAY_HEIGHT - 300:  # 如果球超出屏幕下边范围，反转y方向的速度
            self.speed_y = -abs(random.randint(-2, 2))

    def check_collision(self, role_obj):
        distance = math.sqrt((self.x - role_obj.x) ** 2 + (self.y - role_obj.y) ** 2)
        cvalue = role_obj.width//2 + self.width//2
        # 如果飞船的距离小于它们的直径之和，那么它们就发生了碰撞
        if distance < cvalue:
            return True
        return False



class Particle:
    """粒子类,爆炸效果的粒子"""

    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.lifetime = 100  # 粒子的生命周期

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1  # 每一帧减少生命周期

    def draw(self, screen):
        pygame.draw.circle(
            screen, (255, 255, 0), (int(self.x), int(self.y)), 3
        )  # 使用黄色绘制粒子


class Fighter:
    """玩家战斗机类"""

    def __init__(self, name: str, hp: int, image_obj: any):
        self.name = name
        self.life_value = hp  # 设置生命值
        self.x = DISPLAY_WIDTH // 2  # 初始化x坐标
        self.y = DISPLAY_HEIGHT - 200  # 将塔的y坐标设置为固定值
        self.speed_x = 6  # 在x方向上设置速度
        self.image = image_obj  # 加载图片
        self.width = self.image.get_width()  # 获取图片的宽度
        
    def get_life_value(self):
        if self.life_value < 0:
            return 0
        return self.life_value

    def move(self, dx):
        new_x = self.x + dx * self.speed_x
        if 100 <= new_x <= DISPLAY_WIDTH - 100:
            self.x = new_x


class UfoBullet:
    """Ufo子弹类"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 14
        self.speed_y = 2

    def move(self):
        self.y += self.speed_y

    def check_collision(self, role_obj):
        distance = math.sqrt((self.x - role_obj.x) ** 2 + (self.y - role_obj.y) ** 2)
        cvalue = role_obj.width//2 + self.radius
        # 如果炮弹和飞船的距离小于它们的直径之和，那么它们就发生了碰撞
        if distance < cvalue:
            return True
        return False


class Bullet:
    """子弹类"""

    def __init__(self, x, y, is_big):
        self.x = x
        self.y = y
        self.radius = 14 if is_big else 8
        self.is_big = is_big
        self.speed_y = -8 if is_big else -6

    def move(self):
        self.y += self.speed_y

    def check_collision(self, role_obj):
        distance = math.sqrt((self.x - role_obj.x) ** 2 + (self.y - role_obj.y) ** 2)
        cvalue = role_obj.width//2 + self.radius
        # 如果炮弹和飞船的距离小于它们的直径之和，那么它们就发生了碰撞
        if distance < cvalue:
            return True
        return False

class HBullet:
    """子弹类"""

    def __init__(self, x, y, is_big):
        self.x = x
        self.y = y
        self.radius = 6
        self.speed_x = 6

    def move(self):
        self.x += self.speed_x

    def check_collision(self, role_obj):
        distance = math.sqrt((self.x - role_obj.x) ** 2 + (self.y - role_obj.y) ** 2)
        cvalue = role_obj.width//2 + self.radius
        # 如果炮弹和飞船的距离小于它们的直径之和，那么它们就发生了碰撞
        if distance < cvalue:
            return True
        return False


# 创建表示条纹的类
class Stripe:
    def __init__(self, x, color):
        self.x = x  # 设置条纹的x坐标
        self.speed = 1  # 设置条纹的速度
        self.color = color  # 设置条纹的颜色

    def move(self):
        self.x -= self.speed  # 水平移动条纹
        if self.x < -100:  # 如果条纹超出屏幕范围，重置其位置
            self.x = 1600
