import json


def load(names):
    for name in names:
        with open(name + '.json') as f:
            data = f.read().strip()
            globals()[name] = json.loads(data)
