import random
import pygame
from .common import Scene, Colors, get_assets


class GameStartScene(Scene):

    __name__ = "GameStartScene"

    def __init__(self, manager):
        super().__init__(manager)


    def on_enter(self, **kwargs):
        self.next_scene = kwargs.get("next_scene", "StarFetchScene")  
        self.title_font = pygame.font.Font(get_assets("Imprint-MT-Shadow-2.ttf"), size=96)
        self.title_text_surface = self.title_font.render(
            "SpaceDefense", True, Colors.orange
        )
        self.title_text_rect = self.title_text_surface.get_rect(center=(360, 300))
        
        self.font = pygame.font.Font(get_assets("Imprint-MT-Shadow-2.ttf"), size=32)
        self.text_surface = self.font.render(
            "Press space key to start", True, (255, 255, 255)
        )
        self.text_rect = self.text_surface.get_rect(center=(360, 400))     

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.manager.switch_scene(self.next_scene)
                    return
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 15:
                    self.manager.switch_scene(self.next_scene)
                    return
            elif event.type == pygame.FINGERDOWN or event.type == pygame.FINGERMOTION:
                self.manager.switch_scene(self.next_scene, using_touch=True)
                return

    def update(self):
        pass

    def draw(self, screen):
        screen.fill((0, 0, 0))
        # Generate small stars as white or light grey dots
        for _ in range(10):  # Adjust the range for more or fewer stars
            star_color = random.choice([(255, 255, 255), (200, 200, 200)])  # White or light grey
            star_position = (random.randint(0, 1280), random.randint(0, 720))  # Assuming screen size of 1280x720
            pygame.draw.circle(screen, star_color, star_position, random.randint(1, 3))
        
        # Optionally, add some larger stars or distant galaxies as bigger circles with different colors
        for _ in range(5):  # Adjust for more or fewer larger stars/galaxies
            galaxy_color = random.choice([(255, 255, 0), (0, 255, 255), (255, 0, 0)])  # Yellow, Cyan, Red
            galaxy_position = (random.randint(0, 1280), random.randint(0, 720))
            pygame.draw.circle(screen, galaxy_color, galaxy_position, random.randint(3, 9))
            
        screen.blit(self.title_text_surface, self.title_text_rect)
        screen.blit(self.text_surface, self.text_rect)


    def on_exit(self, **kwargs):
        pass





class GameEndScene(Scene):

    __name__ = "GameEndScene"

    def __init__(self, manager):
        super().__init__(manager)

    def on_enter(self, **kwargs):
        self.title = kwargs.get("title", "Game Over")
        self.next_scene = kwargs.get("next_scene", "GameStartScene")
        self.title_font = pygame.font.Font(get_assets("Imprint-MT-Shadow-2.ttf"), size=72)
        self.title_text_surface = self.title_font.render(
            self.title, True, Colors.orange
        )
        self.title_text_rect = self.title_text_surface.get_rect(center=(240, 300))
        
        self.font = pygame.font.Font(get_assets("Imprint-MT-Shadow-2.ttf"), size=32)
        self.text_surface = self.font.render(
            "Press space key to next", True, (255, 255, 255)
        )
        self.text_rect = self.text_surface.get_rect(center=(240, 400))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.manager.switch_scene(self.next_scene)
                    return
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 15:
                    self.manager.switch_scene(self.next_scene)
                    return
            elif event.type == pygame.FINGERDOWN or event.type == pygame.FINGERMOTION:
                self.manager.switch_scene(self.next_scene, using_touch=True)
                return

    def update(self):
        pass

    def draw(self, screen):
        screen.fill((0, 0, 0))
        # Generate small stars as white or light grey dots
        for _ in range(10):  # Adjust the range for more or fewer stars
            star_color = random.choice([(255, 255, 255), (200, 200, 200)])  # White or light grey
            star_position = (random.randint(0, 1280), random.randint(0, 720))  # Assuming screen size of 1280x720
            pygame.draw.circle(screen, star_color, star_position, random.randint(1, 3))
        
        # Optionally, add some larger stars or distant galaxies as bigger circles with different colors
        for _ in range(5):  # Adjust for more or fewer larger stars/galaxies
            galaxy_color = random.choice([(255, 255, 0), (0, 255, 255), (255, 0, 0)])  # Yellow, Cyan, Red
            galaxy_position = (random.randint(0, 1280), random.randint(0, 720))
            pygame.draw.circle(screen, galaxy_color, galaxy_position, random.randint(3, 9))
            
        screen.blit(self.title_text_surface, self.title_text_rect)
        screen.blit(self.text_surface, self.text_rect)


    def on_exit(self, **kwargs):
        pass
