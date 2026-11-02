"""Read the public EU client identifier from an official My Coffee Lounge APK."""
import argparse
from pathlib import Path
import re
import subprocess

APP_PACKAGE = "com.delonghigroup.daedalus"
KEY_NAME = "com.delonghigroup.identity_kit.API_KEY"


def client_id(tree):
    if not re.search(r'^\s*A: package="' + re.escape(APP_PACKAGE) + r'"', tree, re.M):
        raise ValueError("This is not the My Coffee Lounge app.")
    attribute = r'^\s*A: (?:http://schemas\.android\.com/apk/res/)?android:'
    pattern = (attribute + r'name\([^)]*\)="' + re.escape(KEY_NAME) + r'"[^\n]*\n'
               + attribute + r'value\([^)]*\)="([^"]+)"')
    values = set(re.findall(pattern, tree, re.M))
    if len(values) != 1:
        raise ValueError("The app does not contain one matching client identifier.")
    value = values.pop()
    if not value or value.startswith("@"):
        raise ValueError("This app build does not expose the expected literal client ID.")
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    parser.add_argument("--aapt2", default="aapt2")
    args = parser.parse_args()
    tree = subprocess.check_output(
        [args.aapt2, "dump", "xmltree", str(args.apk), "--file", "AndroidManifest.xml"],
        text=True, encoding="utf-8",
    )
    print(client_id(tree))
