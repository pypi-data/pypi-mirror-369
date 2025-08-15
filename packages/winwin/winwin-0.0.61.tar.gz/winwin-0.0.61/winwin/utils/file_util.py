import yaml


def read_yaml(yaml_url: str):
    with open(yaml_url, encoding="utf-8") as yaml_file:
        return yaml.load(yaml_file, Loader=yaml.SafeLoader)
