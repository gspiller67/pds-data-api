import json

def load_secrets(path="secrets.json"):
    with open(path, "r") as f:
        return json.load(f) 