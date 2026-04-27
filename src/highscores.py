import json
from pathlib import Path
from typing import Dict


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
    def get_highscore_report(cls, file: str) -> Dict[str, str]:
        """
        Renders the high score leaderboard onto the given surface.

        Reads scores from the JSON file and displays each entry as a
        ranked row centered around the provided coordinates. Player names
        are rendered in pink and scores are color-coded green for high
        values and red for low values.
        """
        file_path = Path(file)

        if not file_path.exists():
            return {}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                highscores_report = json.load(f)
                new_scores_report = dict(
                    sorted(
                        highscores_report.items(),
                        key=lambda item: item[1],
                        reverse=True,
                    )[:10]
                )
                highscore_clean = {
                    key: value
                    for key, value in new_scores_report.items()
                    if str(key).isalnum() and value > 0 and len(key) <= 10
                }

            with open(file_path, "w", encoding="utf-8") as f:

                json.dump(highscore_clean, f, indent=4)

                return highscore_clean

        except Exception:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump({}, f, indent=4)
                    return {}
            except Exception:
                return {}
