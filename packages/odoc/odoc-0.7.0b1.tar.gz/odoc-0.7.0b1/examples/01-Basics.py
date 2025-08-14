#! /usr/bin/env python3

import datetime
from decimal import Decimal

from odoc import *


def generate_doc():

    doc = Calc()                # Create a document object
    generate_sheet_1(doc)
    generate_sheet_2(doc)
    generate_sheet_3(doc)
    doc.save("01-Basics.ods")  # finally save the object to a file


def generate_sheet_1(doc):

    sheet = doc['Sheet 1']      # Create a sheet in the document
                                # Sheets cannot be renamed or deleted, once created,
                                # The order of the sheets cannot be changed

    sheet[0,0] = 'Basics'       # Cell-content is simply assigned to cells
                                # The type of the python-object assigned to the cell determines
                                # what type of cell is created
                                # Cells are addressed by [row, column] starting at 0.

    sheet[2,0] = 'This is text'
    sheet[3,0] = 2.0
    sheet[3,1] = 'plus'
    sheet[3,2] = 3.0
    sheet[3,4] = 'equals'
    sheet[3,5] = f'= {sheet[3,0].address()} + {sheet[3,2].address()}'
                                # formulas are strings, which start with '='

    sheet[4,0] = Decimal("3.2") # Decimal, float and int objects are accepted as numeric values

    sheet[5,0] = False
    sheet[5,1] = bool(11)
    sheet[5,2] = 'Booleans'

    sheet[6,0] = Percent(0.15)  # Use the Percent-object to enter percentage values,
                                # This will show up as '15%' in the spreadsheet

    sheet[10,0] = 'Today is'
    sheet[10,1] = datetime.date.today()
    sheet[11,0] = 'Today is'
    sheet[11,1] = datetime.datetime.now()
    sheet[12,0] = 'The time is'
    now = datetime.datetime.now()
    sheet[12,1] = datetime.time(now.hour, now.minute, now.second)

    sheet[14,0] = HyperLink('A hyperlink to libreoffice.org', 'https://libreoffice.org')

    # The assignment-mechanism channels assignments according to python-object type
    # So the following first asigns content (a string) and then an annotation.  The
    # annotation does not overwrite the content in this case.
    sheet[16,0] = 'This cell has a note'
    sheet[16,0] = Note('This is the note')

    # Including images is possible by assigning an Image object to an anchor cell
    # The anchor cell can of course still hold standard content
    '''
        Image(path, width=None, height=None, memitype=None,
            z_index=None, x=None, y=None, background=False, text=None)

        path: path the the image file
        width, height: in css length units, e.g. '15mm' or '20px'
                width and height are optional only if the Pillow-library is installed.
        mimetype: mimetype of the image, optional only if the Pillow-library is installed
        z_index; where to place the image in z-diretion
        x,y: offset from the upper left corner of the anchor cell in css length units.
    '''
    sheet[18,0] = 'This is an image anchor cell'
    sheet[18,0] = Image('Image.jpeg', x='5mm', y='2mm', background=True)


def generate_sheet_2(doc):

    sheet2 = doc['Sheet 2']

    # The python slice-operator is used to address ranges
    # Note, however, that the addressing is end-inclusive, i.e. a range 0:2 covers 3 cells (0,1, and 2)

    sheet2[1, 1:6] = 1
    sheet2[3:6, 1] = 2
    sheet2[3:6, 3:6] = 3

    # Lists can be used to place content im multiple cells at once.
    # Lists _cannot_ be used with ranges
    # To skip a cell, the an ellipsis '...' is used.  This is not the same as using None.
    # None would delete the cell content
    # The elements of a list will be places along a row, starting with the
    # anchor cell.
    # A list within a list, will be placed along the column - further nesting of lists is not
    # supported.

    sheet2[8,1] = ['Col 1', 'Col 2', ..., ['Col 3/ Row 1', 'Col 3/ Row 2', 'Col 3/ Row 3'], 'Col 4']

    # Merging cells is done by calling the 'merge' function on a cell-range

    sheet2[13, 1:4].merge()
    sheet2[13, 1] = 'Merged columns'
    sheet2[13, 1].bgcolor = 'darksalmon'

    sheet2[14:16, 1].merge()
    sheet2[14, 1] = 'Rows'
    sheet2[14, 1].bgcolor = 'linen'

    sheet2[14:16, 2:4].merge()
    sheet2[14,2] = 'Rows and columns'
    sheet2[14,2].bgcolor = 'paleturquoise'


def generate_sheet_3(doc):

    sheet3 = doc['Sheet 3']

    sheet3[0,0] = 'Columns B and C hidden'
    sheet3[1,0] = 'Row 3 hidden'

    sheet3.col[1:2].hide()
    sheet3.row[2].hide()

    # Un-hide the sheet with 'Sheet > Show Sheet...' in LibreOffice
    sheet4 = doc['Hidden Sheet']
    sheet4[0,0] = 'This sheet is (no longer) hidden'
    sheet4.hide()


if __name__ == '__main__':
    generate_doc()
