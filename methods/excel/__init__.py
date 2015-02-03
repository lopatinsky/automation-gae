# coding:utf-8
__author__ = 'dvpermyakov'

import lxml.html
import pyExcelerator
from datetime import datetime


def send_excel_file(request_handler, name, template_name, **values):
    values['btn_type'] = 'xls'
    html_body = request_handler.jinja2.render_template('mt/' + template_name, **values)
    page = lxml.html.fromstring(html_body)
    book = pyExcelerator.Workbook()
    sheet = book.add_sheet(name)
    for i, tr in enumerate(page.xpath("body/table")[0].findall("tr")):
        for j, td in enumerate(tr.getchildren()):
            if td.text:
                sheet.write(i, j, u''.join(td.text))

    request_handler.response.headers['Content-Type'] = 'application/ms-excel'
    request_handler.response.headers['Content-Transfer-Encoding'] = 'Binary'
    request_handler.response.headers['Content-disposition'] = 'attachment; filename="%s-%s.xls"' % (datetime.now().date(), name)
    book.save(request_handler.response.out)