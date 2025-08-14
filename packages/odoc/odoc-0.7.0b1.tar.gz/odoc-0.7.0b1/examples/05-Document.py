#! /usr/bin/env python3

import datetime
from decimal import Decimal

from odoc import *


def generate_doc():

    doc = Calc()
    generate_sheets(doc)

    # --- meta data, will show up under File -> Properties
    doc.creation_date = datetime.datetime(1799,2,1,23,59)

    doc.title = '05-Document'
    doc.subject = 'Document meta data'
    doc.comment = 'Sample document\n\nCan have multiple lines.\n'
    # keywords __must__ be a list of strings, not a single string !
    doc.keywords = ['document', 'meta data', 'stuff']

    doc.contributor = 'Contributor'
    doc.coverage = 'Coverage'
    doc.identifier = 'Identifier'
    doc.publisher = 'Publisher'
    doc.relation = 'Relation'
    doc.source = 'Source'
    doc.type_ = 'Type'
    doc.rights = 'Rights'

    doc.add_user_data('meta number', 42)
    doc.add_user_data('meta string', 'hello world')
    doc.add_user_data('meta date', datetime.date(2025, 3, 27))
    doc.add_user_data('meta datetime', datetime.datetime(2025, 3, 27, 13, 20))
    # LibreOffice renders bool as 'yes/no'
    doc.add_user_data('meta boolean', False)

    #--- some settings ----
    doc.active_sheet = 'Sheet 2'    # the active sheet on load
    doc.rowcol_headers = True       # default: True
    doc.sheet_tabs = True           # default: True

    doc.show_notes = True           # default: True

    doc.show_page_breaks = False    # default: False
    doc.show_zero_values = True     # default: True - if False, 0 value cells will be shown empty

    doc.load_readonly = False       # default: False
    doc.shared = False              # default False

    doc.formula_bar_height = 3      # default: 1
    doc.show_formula_marks = True   # default: False - shows a formula marker in formla cells

    doc.value_highlight = True      # default: False - shows different value types in different colors

    doc.save("05-Document.ods")


def generate_sheets(doc):

    sheet1 = doc['Sheet 1']

    sheet2 = doc['Sheet 2']

    sheet2.cursor_col = 3       # position of the cursor on load
    sheet2.cursor_row = 3

    sheet2.view_first_col = 2   # top-left most cell in the sheet viewport
    sheet2.view_first_row = 2

    sheet2.zoom = 120
    sheet2.show_grid = True


if __name__ == '__main__':
    generate_doc()
