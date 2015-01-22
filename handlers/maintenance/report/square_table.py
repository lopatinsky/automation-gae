__author__ = 'dvpermyakov'

from datetime import datetime
from ..base import BaseHandler
from models import JsonStorage


class SquareTableHandler(BaseHandler):
    def get(self):
        square = JsonStorage.get("square_table")
        if not square:
            self.response.write("Report not ready")
        else:
            for row in square:
                for cell in row:
                    cell["begin"] = datetime.fromtimestamp(cell["begin"])
                    cell["end"] = datetime.fromtimestamp(cell["end"])
            self.render('reported_square_table.html', square=square)
