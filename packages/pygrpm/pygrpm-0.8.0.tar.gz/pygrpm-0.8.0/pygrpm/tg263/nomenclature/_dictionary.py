# coding: utf-8
# author: Pierre-Luc Asselin

"""Import json TG263 dictionary to readable format"""
import json
import re
from pathlib import Path

FILEPATH = Path(__file__).parent / "./tg263.json"

# read file
with open(FILEPATH, "r", encoding="utf-8") as fh:
    data = fh.read()

# Get rid of metadatas, keeping only the dictionary
library_in_json = re.search(re.compile(r"\[.*\]", re.DOTALL), data)

# parse file
ALLOWED_STRUCTURES = json.loads(library_in_json.group(0))
