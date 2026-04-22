import json
from pathlib import Path


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
                    highscores_report[name] = score
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

            highscores_report[name] = score

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(highscores_report, f, indent=4)

class Highscore: