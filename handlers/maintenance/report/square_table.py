__author__ = 'dvpermyakov'

from datetime import datetime
from ..base import BaseHandler
from models import JsonStorage
from methods.excel import send_excel_file


class SquareTableHandler(BaseHandler):
    def get(self):
        square = JsonStorage.get("square_table")
        chosen_btn_type = self.request.get("button")
        if not square:
            self.response.write("Report not ready")
        else:
            for row in square:
                for cell in row:
                    cell["begin"] = datetime.fromtimestamp(cell["begin"])
                    cell["end"] = datetime.fromtimestamp(cell["end"])
            if chosen_btn_type == "xls":
                send_excel_file(self, 'square_table', 'reported_square_table.html', square=square)
            else:
                self.render('reported_square_table.html', square=square)
