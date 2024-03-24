import os 


DISPLAY_WIDTH = 1600
DISPLAY_HEIGHT = 900
GAME_TIME = 300


def get_assets(name):
    assetsDir = os.path.join(os.path.dirname(__file__), 'assets')
    return os.path.join(assetsDir, name)

