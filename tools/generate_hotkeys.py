#!/usr/bin/env python3
import re
import sys
from collections import defaultdict
from pathlib import Path, PurePath
from typing import Dict, List, Tuple

from zulipterminal.config.keys import HELP_CATEGORIES, KEY_BINDINGS


KEYS_FILE = (
    Path(__file__).resolve().parent.parent / "zulipterminal" / "config" / "keys.py"
)
KEYS_FILE_NAME = KEYS_FILE.name
OUTPUT_FILE = Path(__file__).resolve().parent.parent / "docs" / "hotkeys.md"
OUTPUT_FILE_NAME = OUTPUT_FILE.name
SCRIPT_NAME = PurePath(__file__).name
HELP_TEXT_STYLE = re.compile(r"^[a-zA-Z /()',&@#:_-]*$")


def main() -> None:
    generate_hotkeys_file()


def lint_hotkeys_file() -> None:
    """
    Lint KEYS_FILE for key description, then compare if in sync with
    existing OUTPUT_FILE
    """
    hotkeys_file_string = get_hotkeys_file_string()
    # To lint keys description
    error_flag = 0
    categories = read_help_categories()
    for action in HELP_CATEGORIES.keys():
        for help_text, key_combinations_list in categories[action]:
            various_key_combinations = " / ".join(key_combinations_list)
            # Check description style
            if not re.match(HELP_TEXT_STYLE, help_text):
                print(
                    f"Description - ({help_text}) for key combination - [{various_key_combinations}]\n"
                    "It should contain only alphabets, spaces and special characters except ."
                )
                error_flag = 1
    if error_flag == 1:
        print(f"Rerun this command after resolving errors in config/{KEYS_FILE_NAME}")
    else:
        print("No hotkeys linting errors")
        if not output_file_matches_string(hotkeys_file_string):
            print(f"Run './tools/{SCRIPT_NAME}' to update {OUTPUT_FILE_NAME} file")
            error_flag = 1
    sys.exit(error_flag)


def generate_hotkeys_file() -> None:
    """
    Generate OUTPUT_FILE based on help text description and
    shortcut key combinations in KEYS_FILE
    """
    hotkeys_file_string = get_hotkeys_file_string()
    output_file_matches_string(hotkeys_file_string)
    write_hotkeys_file(hotkeys_file_string)
    print(f"Hot Keys list saved in {OUTPUT_FILE}")


def get_hotkeys_file_string() -> str:
    """
    Construct string in form for output to OUTPUT_FILE based on help text
    description and shortcut key combinations in KEYS_FILE
    """
    categories = read_help_categories()
    hotkeys_file_string = (
        f"<!--- Generated automatically by tools/{SCRIPT_NAME} -->\n"
        "<!--- Do not modify -->\n\n# Hot Keys\n"
    )
    for action in HELP_CATEGORIES.keys():
        hotkeys_file_string += (
            f"## {HELP_CATEGORIES[action]}\n"
            "|Command|Key Combination|\n"
            "| :--- | :---: |\n"
        )
        for help_text, key_combinations_list in categories[action]:
            various_key_combinations = " / ".join(
                [
                    " + ".join([f"<kbd>{key}</kbd>" for key in key_combination.split()])
                    for key_combination in key_combinations_list
                ]
            )
            hotkeys_file_string += f"|{help_text}|{various_key_combinations}|\n"
        hotkeys_file_string += "\n"
    return hotkeys_file_string


def output_file_matches_string(hotkeys_file_string: str) -> bool:
    if hotkeys_file_string == open(OUTPUT_FILE).read():
        print(f"{OUTPUT_FILE_NAME} file already in sync with config/{KEYS_FILE_NAME}")
        return True
    else:
        print(f"{OUTPUT_FILE_NAME} file not in sync with config/{KEYS_FILE_NAME}")
        return False


def read_help_categories() -> Dict[str, List[Tuple[str, List[str]]]]:
    """
    Get all help categories from KEYS_FILE
    """
    categories = defaultdict(list)
    for item in KEY_BINDINGS.values():
        categories[item["key_category"]].append((item["help_text"], item["keys"]))
    return categories


def write_hotkeys_file(hotkeys_file_string: str) -> None:
    """
    Write hotkeys_file_string variable once to OUTPUT_FILE
    """
    with open(OUTPUT_FILE, "w") as mdFile:
        mdFile.write(hotkeys_file_string)


if __name__ == "__main__":
    main()
