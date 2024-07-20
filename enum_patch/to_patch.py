"""
Get the structures with enum field

for every structure with enum field, extract the Serialize function pseudo code and output it

"""
import json
import re

try:
    with open('_structs.json', 'r') as file:
        data = json.load(file)
except FileNotFoundError:
    print("Error: '_structs.json' file not found.")
    exit(1)
except json.JSONDecodeError:
    print("Error: Invalid JSON in '_structs.json'.")
    exit(1)

to_patch = []

def check_etz(value):
    if isinstance(value, str):
        return re.match(r'ETz.*', value)
    elif isinstance(value, list):
        return any(check_etz(item) for item in value)
    elif isinstance(value, dict):
        return any(check_etz(v) for v in value.values())
    return False

for k, v in data.items():
    if check_etz(v):
        to_patch.append(k)

print(to_patch)
