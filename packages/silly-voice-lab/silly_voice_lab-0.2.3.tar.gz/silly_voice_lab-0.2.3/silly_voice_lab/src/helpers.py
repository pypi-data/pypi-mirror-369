#! /usr/bin/env python3

import os
from pathlib import Path
from pprint import pprint
import configparser

import yaml

from silly_voice_lab.src.models import  Configuration, Group, Character

BASE_DIR = os.getcwd()



def dprint(CONF: Configuration, *args, **kwargs) -> None:
    if CONF.debug:
        print(*args, **kwargs)

def dpprint(CONF: Configuration, *args, **kwargs) -> None:
    if CONF.debug:
        pprint(*args, **kwargs)


def get_config(file_name: str="dialogues.cfg") -> Configuration:
    config_file = Path(Path(BASE_DIR), Path(file_name))
    if not os.path.exists(Path(config_file)):
        print("No config file found, initialize a project first with the command 'init'")
        exit(0)
        return Configuration()
    print(f"Config file '{file_name}' loading...")
    try:
        config = configparser.ConfigParser()
        config.read(config_file)

        output_folder = config["folders"]["output_folder"]
        input_folder = config["folders"]["input_folder"]
        elevenlabs_api_key = config["secrets"]["elevenlabs_api_key"]
        debug = config["app"]["debug"] == "1"
        converter = config["app"]["converter"]
        female_voice_id = config["dev"]["female_voice_id"]
        male_voice_id = config["dev"]["male_voice_id"]


        configuration = Configuration(
            output_folder=output_folder,
            input_folder=input_folder,
            elevenlabs_api_key=elevenlabs_api_key,
            debug=debug,
            converter=converter,
            female_voice_id=female_voice_id,
            male_voice_id=male_voice_id,
        )
    except Exception as e:
        print(f"Error reading the config file: {e}")
        exit(0)
    return configuration

def get_groups(CONFIG) -> list[Group]:
    groups = []
    folder_path = Path(Path(BASE_DIR), Path(CONFIG.input_folder))
    for file in folder_path.glob("*.yaml"):
        dprint(CONFIG, f"\nReading {file.name} ...")

        with open(Path(Path(folder_path), Path(file.name)), "r", encoding="utf-8") as f:
            casting = yaml.safe_load(f)
            for group in casting:
                grp = Group(**group)
                grp.characters = [Character(**char) for char in grp.characters]
                groups.append(grp)
    return groups
