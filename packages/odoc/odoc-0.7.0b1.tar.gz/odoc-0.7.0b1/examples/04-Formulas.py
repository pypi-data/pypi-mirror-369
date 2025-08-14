#! /usr/bin/env python3

import datetime
from decimal import Decimal

from odoc import *


def generate_doc():

    doc = Calc()
    generate_sheets(doc)
    doc.save("04-Formulas.ods")


def generate_sheets(doc):

    sheet1 = doc['Sheet 1']
    sheet2 = doc['Sheet 2']

    sheet1[1, 1] = ['A', 'B']
    sheet1[2, 1] = [3, 5]

    # Formulas are entered as strings starting with =
    # Use ';' to separate function arguments !
    sheet1[::2, 1] = '= sum(B3; C3)'

    # To enter a string starting with '=', it needs to be preceded by "'"
    sheet1[::1, 1] = "'= not a formula"

    '''
    Addressing is facilitated by the cell-functions 'address' and 'full_address'
    'address' produces a sheet-local address, without the sheet name
    'full_address' includes the sheet name
    The functions take one string argument, which specifies whether to generate an absolute ('$') or
    relative ('_') address.
    The format of the specifier string is:
        '<row0><col0><row1><col0>' for local addresses and
        '<sheet><row0><col0><row1><col0>' for full addresses

    The default is '$$$$$'.   If the specifier is shorter than needed, it is padded with '_'.
    To generate an all relative address ('_____') pass None.
    NOTE: in the spreadsheet application cell are addressed in Column-Row pairs, e.g.
        B1 for row=0 and column=1 so sheet1[0,1].address('$_') results in 'B$1' (and not '$B1')
    '''

    sheet1[::2, 1] = sheet1[:].address()
    sheet1[::1, 1] = sheet1[:].address('$')
    sheet1[::1, 1] = sheet1[:].address('_$')
    sheet1[::1, 1] = sheet1[:].address(None)
    sheet1[::1, 1] = sheet1[:].full_address()
    sheet1[::1, 1] = sheet1[:].full_address('$_$')
    sheet1[::1, 1] = sheet1[:].full_address(None)

    # works also for ranges
    sheet1[::1, 1] = sheet1[:,1:5].address()

    sheet1[::2, 1] = f'= sum({sheet1[2, 1:2].address()})'

    # Named cells and ranges can be created by assigning the name
    # the the 'name' or 'local_name' cell-attribute
    # 'local_name's are only valid in the sheet where the cell is located

    sheet1[2,1].local_name = 'Cell_A'
    sheet1[2,2].local_name = 'Cell_B'

    sheet1[2,1:2].name = 'Cells_AB'

    sheet1[::2, 1] = f'= sum(Cell_A; Cell_B)'
    sheet1[::1, 1] = f'= sum(Cells_AB)'

    # Array functions are created by assigning a function to a range

    # When entering arrays, '|' needs to be used as row-separator and ';' as
    # column-separator, even though the spreadsheet-application might render them
    # using different characters. (See settings dialog Tools > Options > LibreOffice Calc > Formula)

    sheet1.last_row += 2
    lr = sheet1.last_row
    sheet1[lr:lr+1, 1:3] = '={1;2;3|4;5;6}'

    # NOTE: ':2:2' 'last-used notation', add 2 and then build a range of 3 rows
    # i.e. the equivalent of lr = sheet1.last_row; lr+=2; sheet1[lr:lr+2] = ...
    sheet1[:2:3, 1] = '={1|2|3}'

    # NOTE: last-used only stores the start of the last used range, so '2' in necessary to
    # recreate the last used range
    sheet1[:2:, 2] = f'={sheet1[:2:,1].address()} + 10'


if __name__ == '__main__':
    generate_doc()
