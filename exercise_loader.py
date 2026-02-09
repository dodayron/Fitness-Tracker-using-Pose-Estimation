import json
from exercise import Exercise

def load_exercise(name):
    with open("exercises.json", "r") as f:
        configs = json.load(f)

    if name not in configs:
        raise ValueError(f"Unknown exercise: {name}")

    return Exercise(configs[name])
