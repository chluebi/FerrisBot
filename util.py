import json

def parse_config(name):
	with open(f'configs/{name}.json', 'r+') as f:
		data = json.load(f)
	return data