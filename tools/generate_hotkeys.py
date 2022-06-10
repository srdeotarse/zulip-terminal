#!/usr/bin/env python3
from collections import defaultdict
from pathlib import Path, PurePath
from typing import Dict, List, Tuple

from zulipterminal.config.keys import HELP_CATEGORIES, KEY_BINDINGS


OUTPUT_FILE = Path(__file__).resolve().parent.parent / "docs" / "hotkeys.md"
SCRIPT_NAME = PurePath(__file__).name


def main() -> None:
    generate_hotkeys_file()


def generate_hotkeys_file() -> None:
    """
    Generate hotkeys.md in docs folder based on help text description and shortcut key combinations in config/keys.py file
    """
    categories = read_help_categories()
    with open(OUTPUT_FILE, "w") as mdFile:
        mdFile.write(
            f"<!--- Generated automatically by tools/{SCRIPT_NAME} -->\n"
            "<!--- Do not modify -->\n\n# Hot Keys\n"
        )
        for action in HELP_CATEGORIES.keys():
            mdFile.write(
                f"## {HELP_CATEGORIES[action]}\n"
                "|Command|Key Combination|\n"
                "| :--- | :---: |\n"
            )
            for help_text, key_combinations_list in categories[action]:
                various_key_combinations = various_key_combination(
                    key_combinations_list
                )
                mdFile.write(f"|{help_text}|{various_key_combinations}|\n")
            mdFile.write("\n")
    print(f"Hot Keys list saved in {OUTPUT_FILE}")


def read_help_categories() -> Dict[str, List[Tuple[str, List[str]]]]:
    """
    Get all help categories from keys.py
    """
    categories = defaultdict(list)
    for item in KEY_BINDINGS.values():
        categories[item["key_category"]].append((item["help_text"], item["keys"]))
    return categories


def various_key_combination(key_combinations_list: List[str]) -> str:
    """
    Returns list of key combinations.
    """
    various_key_combinations = " / ".join(
        [
            " + ".join([f"<kbd>{key}</kbd>" for key in key_combination.split()])
            for key_combination in key_combinations_list
        ]
    )
    return various_key_combinations


if __name__ == "__main__":
    main()
