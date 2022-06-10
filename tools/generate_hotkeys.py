#!/usr/bin/env python3
import argparse
import re
from collections import defaultdict
from pathlib import Path, PurePath
from typing import Dict, List, Tuple

from zulipterminal.config.keys import HELP_CATEGORIES, KEY_BINDINGS


OUTPUT_FILE = Path(__file__).resolve().parent.parent / "docs" / "hotkeys.md"
SCRIPT_NAME = PurePath(__file__).name

# Exclude keys from duplicate keys checking
KEYS_TO_EXCLUDE = ["q", "e", "m", "r"]


def main(check_only: bool = False) -> None:
    if check_only:
        lint_hotkeys_file()
    else:
        generate_hotkeys_file()


def lint_hotkeys_file() -> None:
    """
    First compare existing hotkeys file, if in sync then lint for key description and key duplication.
    """
    hotkeys_file_string = get_hotkeys_file_string()
    if compare_hotkeys_file(hotkeys_file_string):
        # To lint keys description and duplicate keys
        error_flag = 0
        help_text_style = re.compile(r"^[a-zA-Z\s/()',&@#:_-]*$")
        categories = read_help_categories()
        for action in HELP_CATEGORIES.keys():
            check_duplicate_keys_list: List[str] = []
            for help_text, key_combinations_list in categories[action]:
                check_duplicate_keys_list.extend(key_combinations_list)
                various_key_combinations = various_key_combination(
                    key_combinations_list
                )
                # Check description style
                if not re.match(help_text_style, help_text):
                    various_key_combinations = various_key_combinations.replace(
                        "<kbd>", ""
                    )
                    various_key_combinations = various_key_combinations.replace(
                        "</kbd>", ""
                    )
                    print(
                        f"Description - ({help_text}) for key combination - [{various_key_combinations}] should contain only alphabets, spaces and special characters except ."
                    )
                    error_flag = 1
            # Check key combination duplication
            check_duplicate_keys_list = [
                key for key in check_duplicate_keys_list if key not in KEYS_TO_EXCLUDE
            ]
            duplicate_keys = [
                key
                for key in check_duplicate_keys_list
                if check_duplicate_keys_list.count(key) > 1
            ]
            if len(duplicate_keys) != 0:
                print(
                    f"Duplicate key combination for keys {duplicate_keys} for category ({HELP_CATEGORIES[action]}) detected"
                )
                error_flag = 1
        if error_flag == 1:
            print(
                "After resolving above errors, Run './tools/generate_hotkeys' to update hotkeys."
            )
            print("Again run './tools/generate_hotkeys --check-only' to lint hotkeys.")
        exit(error_flag)
    else:
        print("Run './tools/generate_hotkeys' to update the hot keys")


def generate_hotkeys_file() -> None:
    """
    Generate hotkeys.md in docs folder based on help text description and shortcut key combinations in config/keys.py file
    """
    hotkeys_file_string = get_hotkeys_file_string()
    compare_hotkeys_file(hotkeys_file_string)
    with open(OUTPUT_FILE, "w") as mdFile:
        mdFile.write(hotkeys_file_string)
        print(f"Hot Keys list saved in {OUTPUT_FILE}")


def get_hotkeys_file_string() -> str:
    """
    Get existing hotkeys.md in docs folder as string based on help text description and shortcut key combinations in config/keys.py file
    """
    categories = read_help_categories()
    hotkeys_file_string = f"<!--- Generated automatically by tools/{SCRIPT_NAME} -->\n<!--- Do not modify -->\n\n# Hot Keys\n"
    for action in HELP_CATEGORIES.keys():
        hotkeys_file_string += (
            f"## {HELP_CATEGORIES[action]}\n"
            "|Command|Key Combination|\n"
            "| :--- | :---: |\n"
        )
        for help_text, key_combinations_list in categories[action]:
            various_key_combinations = various_key_combination(key_combinations_list)
            hotkeys_file_string += f"|{help_text}|{various_key_combinations}|\n"
        hotkeys_file_string += "\n"
    return hotkeys_file_string


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


def compare_hotkeys_file(hotkeys_file_string: str) -> bool:
    if hotkeys_file_string == open(OUTPUT_FILE).read():
        print("Hot Keys already in sync with config/keys.py")
        return True
    else:
        print("Hot Keys not in sync with config/keys.py")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lint and generate hotkeys")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Lint hotkeys file for key description and key duplication from keys file",
    )
    args = parser.parse_args()
    main(args.check_only)
