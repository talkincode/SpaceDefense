import os 


DISPLAY_WIDTH = 1320
DISPLAY_HEIGHT = 825
GAME_TIME = 300


def get_assets(name):
    assetsDir = os.path.join(os.path.dirname(__file__), 'assets')
    return os.path.join(assetsDir, name)

