#! /usr/bin/env python3

from odoc import Calc, NumberStyle


def generate_doc():

    doc = Calc()
    generate_sheet_1(doc)
    doc.save('02-Last-Used-Operator.ods')


def generate_sheet_1(doc):

    sheet1 = doc['Sheet1']

    # Using a row variable to produce spreadsheets, which can later be easily altered is a common
    # pattern.

    row = 1
    sheet1[row,0] = ['Animals', 'Count', ..., 'last_row', 'last_col']
    row += 1
    sheet1[row, 0] = ['Dogs', 5]
    row += 1
    sheet1[row, 0] = ['Cats', 3]
    row += 1
    sheet1[row, 0] = ['Turtles', 28]

    # odoc re-(mis-)uses the slice operator as 'last-used-coordinate' operator.

    sheet1[::, 0] = 'Small turtles'

    '''
    '::' addresses the row used in the last cell-assignment. In this case replacing 'Turtles' with
    'Small turtles'.   The structure of the '::' operator is :<rel-range>:<inc>.
    <rel-range> is used to construct a relative range, based on the last used coordinate.
    <inc> increases or decreases the last used coordinate, _before_ the coordinate is used.
    '''

    sheet1[::1, 0] = ['Sheep', 2]
    sheet1[::, 3] = [sheet1.last_row, sheet1.last_col]
    sheet1[::1, 0] = ['Donkeys', 10]
    sheet1[::, 3] = [sheet1.last_row, sheet1.last_col]
    sheet1[::1, 0] = ['Bees', 22345]
    sheet1[::, 3] = [sheet1.last_row, sheet1.last_col]

    # skip a row
    sheet1[::2, 0] = 'Total'
    sheet1[::, 3] = [sheet1.last_row, sheet1.last_col]


    '''
    NOTE that using the relative range operator a value of for example '2' will result
    in 3 elements. I.e. the code below will write 4 lines, as the range is [last_row:last_row + 3]
    '''

    # move the last used row two down
    sheet1.last_row += 2
    sheet1[:3:, 0] = 'four lines'

    '''
    The values of sheet.last_row and sheet_lost.col are only updated, when cells a referenced for
    assignments.  So for example the call sheet[10,10].address(), will not update the last used
    coordinates.  If ranges are assigned to, last_row and last_col will be set to the start
    of the range.
    '''

    # As a special case sheet[::, ::] might be abbreviated to sheet[::]
    sheet1[::] = 'The first of'

    # or even more concise ':', both '::' and ':' resolve to the same python slice(None, None, None)
    sheet1[:] = 'The first of'

    '''
    last_row and last_col are only updated when a cell is assigned a value.  They are not updated
    if values are assigned to cell-styles
    '''

    sheet1[20,1] = 'Cell value'     # this will set last_row == 20, last_col == 1
    row20 = [sheet1.last_row, sheet1.last_col]

    sheet1[21,2].bold = True        # nothing updated, still last_row == 20, last_col == 1
    row21 = [sheet1.last_row, sheet1.last_col]

    addr = sheet1[22,3].address()     # nothing updated, still last_row == 20, last_col == 1
    row22 = [sheet1.last_row, sheet1.last_col]

    sheet1[23,2] = NumberStyle(precision=2)    # This has updated last_row == 23, last_col==2
    row23 = [sheet1.last_row, sheet1.last_col]

    sheet1[20,3] = row20
    sheet1[21,3] = row21
    sheet1[22,3] = row22
    sheet1[23,3] = row23

    # somtimes it is necessary to set last_row or last_col manually
    sheet1.last_row = 26
    sheet1.last_col = 1
    sheet1[:] = 'Manually set last_row and last_col'


if __name__ == '__main__':

    generate_doc()
