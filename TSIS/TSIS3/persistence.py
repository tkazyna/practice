import json
import os

def load_settings():
    if os.path.exists("settings.json"):
        return json.load(open("settings.json"))
    return {"color": "red", "difficulty": "normal", "sound": True}

def save_settings(s):
    json.dump(s, open("settings.json", "w"))

def load_scores():
    if os.path.exists("leaderboard.json"):
        return json.load(open("leaderboard.json"))
    return []

def save_score(name, score, dist, coins):
    data = load_scores()
    data.append({"name": name, "score": score, "dist": dist, "coins": coins})
    data.sort(key=lambda x: x["score"], reverse=True)
    json.dump(data[:10], open("leaderboard.json", "w"))