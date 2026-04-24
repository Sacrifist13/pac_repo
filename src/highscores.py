import json
from pathlib import Path
import pygame
from .assets_manager import AssetsManager


class HighScoreManager:
    """
    Manages the persistence and display of high scores.

    Provides class methods to read, update, and render the high score
    leaderboard stored in a JSON file. Scores are sorted in descending
    order and capped at the top ten entries.
    """

    @classmethod
    def update_highscores_file(cls, file: str, name: str, score: int) -> None:
        """
        Updates the high score file with a new entry.

        If the file does not exist, it is created with the provided score
        as the first entry. Otherwise, the new score is added or overwrites
        the existing entry for that name. Invalid entries are filtered out,
        and only the top ten scores are retained after sorting.

        Args:
            file (str): Path to the JSON high score file.
            name (str): The player's username to associate with the score.
            score (int): The score value to record.
        """
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
                        k: score_val
                        for k, score_val in highscores_report.items()
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
    def display_score(
        cls,
        file: str,
        screen: pygame.Surface,
        x_pos: int,
        y_pos: int,
        asset_font: AssetsManager,
    ) -> None:
        """
        Renders the high score leaderboard onto the given surface.

        Reads scores from the JSON file and displays each entry as a
        ranked row centered around the provided coordinates. Player names
        are rendered in pink and scores are color-coded green for high
        values and red for low values.

        Args:
            file (str): Path to the JSON high score file.
            screen (pygame.Surface): The surface to render the scores on.
            x_pos (int): The horizontal center point for score alignment.
            y_pos (int): The vertical starting position for the first entry.
            asset_font (AssetsManager): The assets manager providing the
                font used for rendering.
        """
        file_path = Path(file)
        display_score = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                display_score = json.load(f)
        except json.JSONDecodeError:
            print("Error json file don't exist")
            return

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
