import os
import json


class Player(object):
    def __init__(self, player_info):
        self.high_scores = player_info["high scores"]
        
    def add_score(self, score):
        if len(self.high_scores) > 9:
            low = min(self.high_scores)
            if score <= low:
                return
        self.high_scores.append(score)
        
    def save(self):
        info = {"high scores": self.high_scores}
        player_file = os.path.join("resources", "player_save.json")
        with open(player_file, "w") as f:
            json.dump(info, f)