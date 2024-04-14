import asyncio
import pygame
from .scene_starfetch import StarFetchScene
from .common import SceneManager, res_manager
from .actors import (
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT,
)
from .scenes import GameStartScene, GameEndScene


class AsyncSpaceDefense(object):

    def __init__(self):
        pygame.mixer.pre_init(44100, 16, 2, 4096)
        pygame.init()
        pygame.joystick.init()
        pygame.mixer.init()
        pygame.mixer.set_reserved(2)
        self.screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pygame.display.set_icon(res_manager.load_image("images/icon.png"))
        pygame.display.set_caption("SpaceDefense")

        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()


    #######################################################
    ## start game
    #######################################################
    async def start_game(self):
        """开始游戏"""
        scene_manager = SceneManager()
        start_scene = GameStartScene(scene_manager)
        end_scene = GameEndScene(scene_manager)
        starfetch_scene = StarFetchScene(scene_manager)
        scene_manager.add_scene(start_scene)
        scene_manager.add_scene(end_scene)
        scene_manager.add_scene(starfetch_scene)
        scene_manager.switch_scene(GameStartScene.__name__)

        running = True
        clock = pygame.time.Clock()
        while running:
            if self.joystick:
                clock.tick(120)
            else:
                clock.tick(60)
            scene_manager.handle_events(pygame.event.get())
            scene_manager.update()
            scene_manager.draw(self.screen)
            pygame.display.flip()

            await asyncio.sleep(0)


async def main():
    await AsyncSpaceDefense().start_game()


def run_game():
    try:
        asyncio.run(AsyncSpaceDefense().start_game())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
