import sys
from src.game_engine import GameEngine

if __name__ == "__main__":
    try:
        game = GameEngine()
        game.run()
    except Exception as e:
        print(
            f"\n❌ [ERROR] {e}\n",
            file=sys.stderr,
        )
