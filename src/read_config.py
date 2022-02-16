import os

import yaml


def parseconfig() -> object:
    """

    :return: object.

    A function parses the `config.yml` file.
    """
    current_dir = os.path.dirname(__file__)
    with open(f"{current_dir}/config.yml", "r") as config_file:
        data = yaml.load(config_file, Loader=yaml.FullLoader)
    return data


config_data = parseconfig()
model_parameters = config_data["model_parameters"]
model_input = config_data["model_input"]
