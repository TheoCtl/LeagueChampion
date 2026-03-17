"""
Pokemon League Champion - Pygame Entry Point
"""
from engine import Engine
from game import TitleScene, GameState


def main():
    state = GameState()
    engine = Engine()
    engine.set_scene(TitleScene(state))
    engine.run()


if __name__ == "__main__":
    main()
