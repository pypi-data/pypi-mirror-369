#! /usr/bin/env python3

import datetime
from decimal import Decimal

from odoc import *


def generate_doc():

    doc = Calc()
    generate_sheet_cell_styles(doc)
    generate_sheet_data_styles(doc)
    generate_sheet_conditional_styles(doc)
    generate_sheet_row_and_columns_styles(doc)
    generate_sheet_table_styles(doc)
    generate_sheet_office_styles(doc)

    doc.save("03-Styles.ods")


def generate_sheet_cell_styles(doc):

    sheet = doc['CellStyles']

    ''' There are several ways to set cell-styles.
        - All style attributes are available as cell attributes
        - Cell styles can be set by assigning a CellStyle object to a cell
        - All style attributes can be passed to a CellStyle object as initialization arguments,
          or later bey accessing them as attributes.
    '''

    # Setting a style as a cell attribute
    sheet[0,0] = 'bold'
    sheet[:].bold = True

    # Setting a style as a via assignment of a CellStyle object
    sheet[::1, 0] = 'italic'
    sheet[:] = CellStyle(italic=True)

    # This would also work
    # sheet[:].style = CellStyle(italic=True)

    # Setting a style as a CellStyle attribute
    sheet[::1, 0] = 'underline'
    style = CellStyle()
    style.underline = '-'
    sheet[:] = style

    # In some cases it is necessary for to set country and language, e.g. to invoke the correct
    # spellchecker. Use the usual codes.

    sheet[:].country = 'DE'
    sheet[:].language = 'de'

    '''
    Color values can be set either:
        - As strings of rgb-hex values, e.g. '#7fff00',
        - abbreviated rgb-hex values, e.g. '#060', or
        - using css-names colors, e.g. 'olive'
    '''

    sheet[::2,0] = 'Green text'
    sheet[:].color = '#060'

    sheet[::1,0] = 'Lime background'
    sheet[:].bgcolor = 'lime'
    sheet[:].color = 'olive'

    '''
        The boolean attributes 'underline', 'overline' and 'strikeout' are just convenience
        attributes.
        The detailed attributes are for:
        - underline:  underline_color, underline_mode
        - overline: overline_color, overline_mode
        - strikeout: strikeout_mode,

        Possible values for these attributes are
            (over/under)line_style:
                'solid' / '-',
                'double' / '='
                'bold' / '-!'

                'dotted' / '.',
                'dotted bold' / '.!',

                'dash' / '--' ,
                'dash bold' / '--!' ,

                'long-dash' / '|',
                'long-dash' / '|!',

                'dot-dash' / '.-',
                'dot-dash bold' / '.-!',

                'dot-dot-dash' / '..-',
                'dot-dot-dash bold' / '..-!',

                'wave' / '~'
                'wave bold' / '~!'
                'wave double' / '~~'

            stikeout line_style
                'solid' / '-',
                'double' / '='
                'bold' / '-!'
                '/'
                'x' / 'X'

            (over/under)line_color: color of the line, a color value as described above

        'skip-white-space': when this attribute is set to True, overline, underline and strikeout
             will skip cover white-spaces
    '''

    sheet[::2,0] = 'Wavy red underline'
    sheet[:] = CellStyle(underline='~!', underline_color= 'red', skip_white_space=True)

    sheet[::1,0] = 'Strikeout'
    sheet[:] = CellStyle(strikeout='/')

    sheet[::1,0] = 'Strikeout with a line'
    sheet[:] = CellStyle(strikeout='=')

    ''' To use a certain font, set the font_name attribute to the font_family name.
        Font sizes can be given in length units ('cm', 'mm' 'in', 'pt' 'pc', 'px', 'em').
        Besides 'font_name', there are also attributes 'font_name_asian' and
        'font_name_complex'.
    '''
    sheet[::2,0] = 'Fonts'
    sheet[:] = CellStyle(font_name='Courier', font_size='15pt', color='darkslategrey', bold=True)

    ''' Setting the font_name attribute will automatically enter the name into the documents
        font_face dictionary - however, automatic entries lack 'pitch' and 'generic_family'
        information.
        A more resilient way to use fonts is to explicitly entering them into the font_face
        dictionary, with information on pitch ('fixed' or 'variable') and 'generic_name'
        ('decorative', 'modern', 'roman', 'script', 'swiss', or 'system').  This allows the
        spreadsheet app to find a substitution font, if the requested font is not available on the
        system.
        The name/key in the font_face dictionary can be chosen freely.
    '''

    doc.font_face['bozo'] = FontFace(family='Non-existent Roman Font',
        generic_family='roman', pitch='variable')

    sheet[::1,0] = 'Non-existent Roman Font'
    sheet[:] = CellStyle(font_name='bozo', font_size='20em', color='darkslategrey', bold=True)

    # special font effects

    sheet[::1,0] = 'Text shadow'
    # LibreOffice only offers a 1pt,1pt-offset text shadow
    sheet[:] = CellStyle(font_size='15pt', text_shadow=True)

    # embossed and engraved are mutually exclusive, chose only one
    sheet[::1,0] = 'Embossed'
    sheet[:] = CellStyle(font_size='15pt', embossed=True)
    sheet[::1,0] = 'Engraved'
    sheet[:] = CellStyle(font_size='15pt', engraved=True)

    sheet[::1,0] = 'Outline'
    sheet[:] = CellStyle(font_size='15pt', outline=True)


    # Cell-styling

    sheet[::2,1].font_size = '30pt'  # just to give the row some height
    sheet[::2,0] = 'X'
    sheet[:].valign = 'middle'  # vertical alignment, possible values are 'top', 'middle', 'bottom', 'automatic'
    sheet[:].text_align_source = 'fix'  # 'fix' or 'value-type'
            # The default alignment for a cell value-type string is left, for other value-types it is right
    sheet[:].halign = 'center' # horizontal alignment, possible values are 'start', 'end', 'left', 'right', 'center', 'justify'

    sheet[:,::2] = 123.23
    sheet[:].halign = 'start' # horizontal alignment, possible values are 'start', 'end', 'left', 'right', 'center', 'justify'
    sheet[:,::1] = 'end'
    sheet[:].halign = 'end' # horizontal alignment, possible values are 'start', 'end', 'left', 'right', 'center', 'justify'

    sheet[:,::1] = 123.23
    sheet[:].halign = 'left' # horizontal alignment, possible values are 'start', 'end', 'left', 'right', 'center', 'justify'
    sheet[:,::1] = 'right'
    sheet[:].halign = 'right' # horizontal alignment, possible values are 'start', 'end', 'left', 'right', 'center', 'justify'

    sheet[:,::1] = 'justify'
    sheet[:].halign = 'justify' # horizontal alignment, possible values are 'start', 'end', 'left', 'right', 'center', 'justify'

    sheet[::1,0] = '*'
    sheet[:].repeat_content = True  # repeats the content of the cell until it's visible area is filled

    sheet[::1, 0] = 'abcd abcd abcd abcd abcd abcd abcd'
    sheet[:].wrap = True

    # Borders

    # borders can be defined via a string "[width] [style] [color]".  Each of the three elements
    # is optional.

    sheet[::2,0] = 'thin border'
    sheet[:].border ="thin solid black"
    sheet[:,::1] = 'thick border'
    sheet[:].border ="thick solid black"
    sheet[:,::1] = '1pt border'
    sheet[:].border ="1pt solid black"
    sheet[:,::1] = '0.25mm border'
    sheet[:].border ="0.25mm solid black"

    sheet[::1,0] = 'dotted'
    sheet[:].border ="3pt dotted black"
    sheet[:,::1] = 'dashed'
    sheet[:].border ="dashed black"
    sheet[:,::1] = 'solid'
    sheet[:].border ="solid black"
    sheet[:,::1] = 'double'
    sheet[:].border ="double"
    sheet[:,::1] = 'groove'
    sheet[:].border ="groove"
    sheet[:,::1] = 'ridge'
    sheet[:].border ="ridge"
    sheet[:,::1] = 'inset'
    sheet[:].border ="inset"
    sheet[:,::1] = 'outset'
    sheet[:].border ="outset"

    sheet[::1,0] = 'red'
    sheet[:].border ="red"
    sheet[:,::1] = 'default'
    sheet[:].border =""

    sheet[::2,0] = 'bottom'
    sheet[:].border_b = ''
    sheet[:,::2] = 'left'
    sheet[:].border_l = ''
    sheet[:,::2] = 'right'
    sheet[:].border_r = ''
    sheet[:,::2] = 'top'
    sheet[:].border_t = ''

    # for double borders, the individual line thicknesses can be set with a string with three lengths
    # "lower or left] [space] [upper or right]"
    # border_width only applies to double lines - not all the other styles

    sheet[::2,0] = 'double'
    sheet[:].border = 'double'
    sheet[:].border_width = '1pt 1pt 3pt'

    sheet[:, ::2] = 'double'
    sheet[:].border = 'double'
    sheet[:].border_width = '1pt 3pt 1pt'

    sheet[:, ::2] = 'double'
    sheet[:].border = 'double'
    sheet[:].border_width = '0.1mm 0.2mm 0.1mm'

    # diagonals

    sheet.last_row += 2
    sheet[:, 0].diagonal_bl_tr = 'dotted'
    sheet[:, 1].diagonal_tl_br = 'solid'

    sheet[:, 2].diagonal_bl_tr = 'double'
    sheet[:,2].diagonal_bl_tr_widths = '1pt 2pt 1pt'
    sheet[:, 2].diagonal_tl_br = 'double'
    sheet[:,2].diagonal_tl_br_widths = '1pt 2pt 1pt'

    sheet[::2,0] = 'padded'
    sheet[:].padding = '5mm'
    sheet[::1,0] = 'top padded'
    sheet[:].padding_t = '5mm'
    sheet[::1,0] = 'left padded'
    sheet[:].padding_l = '5mm'
    sheet[::1,0] = 'right padded'
    sheet[:].halign = 'end'
    sheet[:].padding_r = '5mm'
    sheet[::1,0] = 'bottom padded'
    sheet[:].padding_b = '5mm'

    # rotation, should be given as an integer representing degrees
    # the default rotation_align is 'bottom'
    # 'center' and 'none' are identical

    sheet[::2,0:3] = 'rotation'
    sheet[:, 0:3].rotation_angle = 23
    sheet[:, 0].rotation_align = 'none'
    sheet[:, 1].rotation_align = 'bottom'
    sheet[:, 2].rotation_align = 'top'
    sheet[:, 3].rotation_align = 'center'

    sheet[::2,0] = 'top to bottom'
    sheet[:].direction = 'ttb'

    sheet[::2,0] = 'shrink to fit cell size'
    sheet[:].shrink_fit = True


def generate_sheet_data_styles(doc):

    sheet = doc['DataStyles']

    '''
    Data styles are defined by one of the DataStyle classes, and set by assigning an
    instance of such a class to a cell.  They are automatically assigned to the data_style attribute
    of the cell.

    DataStyle classes are: NumberStyle, PercentStyle, ScientificStyle, FractionStyle,
        BooleanStyle, and DateStyle

    All data style classes share the following attributes:
    'country': ISO-country code, specifies a country code for a data style. The country code is
            used for formatting properties whose evaluation is locale-dependent.
    'language': ISO language code
    'volatile': True or False, specifies whether unused style in a document are retained or
            discarded by consumers.
    'color':  Color is intended to be used for conditional styling.
            For general (static) color styling use the color attribute of the cell style
            Only the basic eight colors can be used for conditional styling:
                'black', 'blue', 'lime' ('green'), 'cyan', 'red', 'magenta', 'yellow', and 'white'.
    'map': List of DataCondition objects

    'prefix': Text to be placed before the value ('prefix' is not used in DateStyle)
    'postfix': Text to be placed after the value ('postfix' is not used in  DateStyle, PercentStyle)

    'no_value': If set to True (defaults to False), no value will
            be displayed.  One might use prefix (or postfix) to assigning a freeform text.
            'no_value' might be useful when used in condition-maps.
            ('no_value' is not used in DateStyle)
    '''

    '''
    NumberStyle
    'grouping': True/False, group accordung to local, e.g. 1000 => 1,000
                Defaults to True
    'precision': number of decimal places
    'min_digits': Minimum number of integer digits.  Adds leading '0's if necessary.
            'precision' must also be specified for min_digits to have any effect.  If it is not
            specified, 'precision' is assumed to be 0.
    '''

    sheet[0,0] = 1234.5678
    sheet[:] = NumberStyle(precision=2)

    # this would also work:
    # sheet[:].data_style = NumberStyle(precision=2)

    sheet[::1,0] = 1
    sheet[:] = NumberStyle(min_digits=4, grouping=False )

    sheet[::1,0] = 1.23
    sheet[:] = NumberStyle(prefix='<', postfix='>')

    '''
    Scientific style
    Attribute 'grouping', 'precision', and 'min_digits' just like NumberStyle
    'min_exp_digits': minimum number of exponent digits
    'exp_interval': e.g. 1 for scientific (default) or 3 for engineering
    'forced_exp_sign': if True, a plus sign will be added for positive numbers.
    '''

    sheet[::2,0] = 12345678.1234567
    sheet[:] = ScientificStyle(precision=2, min_exp_digits=2, exp_interval=3,
        forced_exp_sign=True)

    '''
    Fractions
    'grouping',  like NumberStyle
    'min_digits': like NumberStyle. Leaving it out will produce only the fraction without the
        whole number integer part, e.g. 10.25 will be rendered as 41/4 instead of for example 10 1/4.
        It can be set to 0, to get the integer part of the number.
    'divisor':
    'max_divisor': The 'max_denominator' attribute specifies the maximum denominator permitted
        to be used if the 'denominator' attribute is not specified. It is ignored otherwise.
        A max_divisor of 9, 99, or 999 signifies any 1, 2, or 3 digit denominator is useable
            respectively.
    'min_divisor_digits': like 'min_digits' but for the denominator
    'min_factor_digits': like 'min_digits' but for the numerator.  In case of doubt, set it to 0.
    'max_factor_digits': libreoffice extension
    '''

    sheet[::2,0] = 10.25
    sheet[:] = FractionStyle(min_digits=0, divisor=8, min_factor_digits=0)
    sheet[::1,0] = 10.33333
    sheet[:] = FractionStyle(min_digits=0, max_divisor=99, min_factor_digits=0)
    sheet[::1,0] = 10.33333
    sheet[:] = FractionStyle(max_divisor=99, min_factor_digits=0)

    '''
    Conditional styling for DataStyles
    Conditional styles are defined by assigning the 'map' attribute of a DataStyle object
    a list of DataCondition objects.  DataCondition objects are created with the
    signature DataCondition(condition, DataStyle-object).

    The condition should be a string of the form 'op value'. Possible op's are '<', '>', '<=',
    '>=', '=' or '!='.  value should be a constant value.

    When using maps, LibreOffice 'swallows' the minus of negative numbers - it thus
    needs to be added back in via prefix.

    Note: There's also styling available for CellStyles, which is similar but different, and
          more powerful.
    '''

    sheet[::2,0] = [[1.23, -1.23]]
    sheet[:2,0] = NumberStyle(precision=2, color='black',
        map=[DataCondition('< 0', NumberStyle(color='red', prefix='-')),
    ])
    sheet.last_row += 2

    sheet[::1,0] = [[True, False]]
    sheet[:2,0] = NumberStyle(color='green',
        map=[DataCondition('= False', NumberStyle(color='blue')),
    ])
    sheet.last_row += 2

    '''
    Boolean style
    If the attribute 'no_value' is set to True (defaults to False), no boolean value will
    be displayed.  One might use prefix (or postfix) to assing a freeform text
    '''

    sheet[::1,0] = [[True, False],[True, False]]
    sheet[:2,0] = BooleanStyle(color='green',
        map=[DataCondition('= False', BooleanStyle(color='blue')),
    ])
    sheet[:2,1] = BooleanStyle(color='green', prefix="That's right", no_value=True,
        map=[DataCondition('= False', BooleanStyle(color='blue', prefix="Wrong !", no_value=True)),
    ])
    sheet.last_row += 2


    '''
    DateStyle
    Has the attributes 'country', 'language', 'volatile', 'color', 'map', and 'format'

    The format attribute take a string, which works like the strftime in python and many posix
    systems, only a few format place-holders are different:

        %a abbrev. week-day
        %A full week-day

        %b abbrev, month nam
        %B full month name
        %m two digit month, leading zero

        %y two digit year, leading zero
        %Y four digit year

        %d day of month, leading zero
        %e day of month, short (would have a leading space in posix-C)

        %H  hour, two digit, leading zero, 12 or 24 hour style depends on whether %p is included
            in the format
        %h  (non-standard) hour without leading zero

        %M minutes, leading zeros
        %S seconds, 2 digits, leading zero

        %p am/pm

        %E (non standard) full era name

        %Q (non standard) quarter as '1st quarter' - '4th quarter'
        %q (non standard) quarter as Q1 - Q4

        %W week of the year number

        %D  Equivalent to %m/%d/%y
        %F  Isodate
        %r  time in am-pm format (%I:%M:%S%p)
        %R  time in 24 hour format (%H:%M)
        %T  time (%H:%M:%S)
    '''

    sheet.col[0].width = '88 mm'

    sheet[::1,0] = datetime.date(2025,5,23)
    sheet[:] = DateStyle(format='%F')

    sheet[::1,0] = datetime.datetime(2025,5,23,23,2,7)
    sheet[:] = DateStyle(format='%A %e %B %Y %H:%M and %s seconds')

    sheet[::1,0] = datetime.datetime(2025,5,23,23,2,7)
    sheet[:] = DateStyle(format='%A %e %B %Y %H:%M %p and %s seconds')


def generate_sheet_row_and_columns_styles(doc):
    # NOTE: The instruction to use optimal column width cannot be issued in the document-file.

    sheet = doc['RowColStyles']

    sheet[0,0] = '10 mm column width'
    sheet.col[0].width= '10 mm'

    sheet.col[1:5].width= '15 mm'

    sheet[1,0] = '20 mm row height'
    sheet.row[1].height = '20 mm'

    sheet[2,0] = 'optimal height'
    sheet[:].font_size = '25 pt'
    sheet.row[2].optimal_height = True

    # bgcolor is available for rows, but not columns
    sheet.row[2].bgcolor = 'orange'

    # ranges also work for columns and rows
    sheet.row[4:6].bgcolor = 'coral'


def generate_sheet_conditional_styles(doc):

    sheet = doc['ConditionalStyles']

    '''
    Conditional styles are set up via a 'map', which is a list of condition
    objects.  Condition objects take a parametrization for the condition and
    the name of an office-style, to apply should a condition be met.
    Supplying a CellStyle instead of an office style name will __not__ work.

    The following condition objects are avaiable:
    - Condition(cond, style):
        cond is a condition string in the form of '<op> <value>'
        Possible <op>s are '<', '>', '<=', '>=','=' or '!='
        value can be a constant e.g 42, the
        address of a cell, or a formula eg 'AVERAGE(A1:A10)'
    - ConditionBetween(value1, value2, style)
        The condition is met if the value of the cell lies between value1 and value2
    - ConditionNotBetween(value1, value2, style)
    - ConditionTrue(expr, style)
        The condition is met, if expression expr is true.

    LibreOffice has a whole set of additional conditions, specific to LibreOffice.
    These are not supported (yet).
    '''

    sheet[1,1] = [75,22,5,90,67,51,44,38,87,27]
    sheet[:,1:10] = CellStyle( map = [
        Condition('>50', 'Accent 1'),
        ConditionBetween(20, 40, 'Accent 2')
    ])

    sheet[::2,1] = [75,22,5,90,67,51,44,38,87,27]
    sheet[:,1:10] = CellStyle( map = [
        Condition(f'> {sheet[::1,2].address()}', 'Accent 1'),
    ])
    lr = sheet.last_row

    sheet[::1,1] = 'Average'
    sheet[:,2] = f'=AVERAGE({sheet[lr,1:10].address()})'

    sheet[::2,1] = [75,22,5,90,67,51,44,38,87,27]
    sheet[:,1:10] = CellStyle( map = [
        ConditionTrue(f'{sheet[:].address()} > 50', 'Accent 1'),
    ])


def generate_sheet_table_styles(doc):

    sheet = doc['TableStyles']

    sheet.bgcolor = 'antiquewhite'

    # 'lr-tb' (default), 'rl-tb', 'tb-rl', 'tb-lr', 'lr', 'rl', 'tb', 'page'
    #  only 'rl' and 'rl-tb' seem to have an effect

    sheet.writing_mode = 'rl'
    sheet[0,0] = 'hello'
    sheet.tab_color = 'orange'


    # To show the hidden sheet use "Sheet" > "Show sheet ..." in LibreOffice
    sheet_h = doc['Hidden sheet']
    sheet_h[0,0] = 'This is no longer a hidden sheet'
    sheet_h.display = False

    generate_sheet_office_styles(doc)


def generate_sheet_office_styles(doc):
    '''
    Office-styles are predefined cell-styles, which the LibreOffice user can for example select from
    a side bar.  To define an office-style, add it to the doc.office_style dictionary
    '''
    sheet = doc['office-styles']

    doc.office_style['My special style'] = CellStyle(
        bgcolor='pink',
        color='blue',
        bold=True
    )

    # Now it can be used by assigning its name to the cell style attribute
    # NOTE: If the 'style' attribute is used, all other style-related cell attributes are ignored
    sheet[1,1] = 'some text'
    sheet[:].style = 'My special style'
    sheet[:].border = 'solid'  # this will be ignored


    # In order to use an office style and either override or add style attribute
    # the office-style should be assigned to the 'parent' attribute
    sheet[::2,1] = 'some boxed text'
    sheet[:].parent = 'My special style'
    sheet[:].border = 'solid'

    # Office-styles can be derived from other office styles.

    doc.office_style['My other style'] = CellStyle(parent='My special style', italic=True)
    sheet[::2,1] = 'some italic text'
    sheet[:].style = 'My other style'

    sheet.col[1].width = '100 mm'

    doc.office_style['NumNegRed'] = CellStyle(
        data_style=NumberStyle(grouping=True, precision=0, min_digits=1, color='black',
           map=[DataCondition('< 0', NumberStyle(color='red', prefix='-')),]
        )
    )

    sheet[::2,1] = ['NumNegRed', 1.0, -1.0]
    sheet[:,2:3].style = 'NumNegRed'


if __name__ == '__main__':
    generate_doc()
