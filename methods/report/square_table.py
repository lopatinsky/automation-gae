__author__ = 'dvpermyakov'

from datetime import datetime
from models.storages import JsonStorage


def get():
    square = JsonStorage.get("square_table")
    if square:
        for row in square:
            for cell in row:
                cell["begin"] = datetime.fromtimestamp(cell["begin"])
                cell["end"] = datetime.fromtimestamp(cell["end"])
        return square
