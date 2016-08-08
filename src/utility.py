import yaml
from entity import Warranty, DellAsset

def load_yaml_config(config_path):
	with open(config_path, "r") as value:
		return yaml.load(value)


def save_entity_csv(dell_asset_L, output_path):
	with open(output_path, 'w') as output:
		for dell in dell_asset_L:
			output.write(str(dell) + "\n")

