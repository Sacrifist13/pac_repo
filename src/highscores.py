import json
from pathlib import Path
import pygame
from .assets_manager import AssetsManager


class HighScoreManager:
    @classmethod
    def update_highscores_file(cls, file: str, name: str, score: int) -> None:
        file_path = Path(file)

        if not file_path.exists():
            highscores_report = {name: score}
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(highscores_report, f, indent=4)
        else:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    highscores_report = json.load(f)
                    highscores_report[name] = int(score)
                    highscores_report = {
                        k: score_val for k, score_val in
                        highscores_report.items()
                        if isinstance(score_val, int)
                    }

                    new_scores_report = dict(
                        sorted(
                            highscores_report.items(),
                            key=lambda item: item[1],
                            reverse=True,
                        )[:10]
                    )
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(new_scores_report, f, indent=4)
            except json.JSONDecodeError:
                highscores_report = {}

    @classmethod
    def display_score(cls, file: str,
                      screen: pygame.Surface,
                      x_pos: int,
                      y_pos: int,
                      asset_font: AssetsManager) -> None:
        file_path = Path(file)
        display_score = {}
        try:
            with open(file_path, 'r', encoding="utf-8") as f:
                display_score = json.load(f)
        except json.JSONDecodeError:
            print("Error json file don't exist")
        font_style = asset_font.f_basic
        for i, (id, score) in enumerate(display_score.items()):
            name_color = (255, 20, 147)
            if score < 30:
                score_color = (255, 7, 58)
            else:
                score_color = (44, 255, 5)
            output_name = f"{i + 1}: {id} "
            output_score = f": {score}"
            text = font_style.render(output_name, True, name_color)
            score = font_style.render(output_score, True, score_color)
            text_rect = text.get_rect(midright=(x_pos, y_pos + (i * 25)))
            score_rect = score.get_rect(midleft=(x_pos, y_pos + (i * 25)))
            screen.blit(text, text_rect)
            screen.blit(score, score_rect)
