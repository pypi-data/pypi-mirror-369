

def escape_sheet_name(name):
    '''see "LibreOffice renaming sheets"
        https://help.libreoffice.org/latest/en-US/text/scalc/guide/rename_table.html
    '''
    forbidden_chars = ':\/?*[]'

    if not name: return name

    if name[0]=="'" or name[-1]=="'":
        raise ValueError("Sheet-names cannot start or end with and apostrophe \"'\".")

    exotic_chars = False
    esc_name = ''
    for c in name:
        if c in ':\/?*[]':
            raise ValueError(f"Sheet-names cannot contain \"{c}\".")
        if c == "'":
            esc_name += "''"
            continue
        ac = ord(c)
        esc_name += c

        if not ((48 <= ac <= 57) or (65 <= ac <= 90) or (96 <= ac <= 122) or (c == "_")):
            exotic_chars = True

    if exotic_chars:
        esc_name = f"'{esc_name}'"

    return esc_name


def _col_alpha(col):
    alpha = ''
    while True:
        col, asc = divmod(col, 26)
        alpha = chr(asc+65) + alpha
        if not col: break
        col -= 1

    return alpha


def address(sheet, row, col, row2=None, col2=None, *, spec='$$$$'):
    ''' Full address including sheet-name
        spec: <sheet><row><col><row2><col2>   $ for absolute, any other char for relative

        NOTE: Sheet names are always absolute, otherwise they would not be needed - the
              $ in front of the sheet name is thus redundant, but needed.
    '''

    return _address(sheet, row, col, row2, col2, spec)


def local_address(row, col, row2=None, col2=None, *, spec='$$$$'):
    ''' call as either cell_address(row, col, ...) or
        cell_address(sheet, row, col, ...)
        spec: <sheet><row><col><row2><col2>   $ for absolute, any other char for relative
    '''

    return _address(None, row, col, row2, col2, spec)


def _address(sheet, row, col, row2, col2, spec):

    # This allows the user to use a partial spec like spec=None or spec='__'
    spec = (spec or '') + '_____'

    def absolute(pos):
        if not spec or len(spec) <= pos: return '$'
        return '$' if spec[pos] == '$' else ''

    ar, ac, ar2, ac2 = (absolute(P) for P in range(4))

    if sheet is not None:
        sheet = F"${escape_sheet_name(sheet if isinstance(sheet, str) else sheet.name)}."
        addr = f"{sheet or ''}{ac}{_col_alpha(col)}{ar}{row + 1}"
    else:
        addr = f"{ac}{_col_alpha(col)}{ar}{row + 1}"

    if row2 is not None or col2 is not None:
        row2 = row2 or row
        col2 = col2 or col

        addr += f":{ac2}{_col_alpha(col2)}{ar2}{row2 + 1}"

    return addr


def cellCoord(cellId):
    row = 0
    col = 0
    chars = list(cellId)
    while(chars):
        ch = chars.pop(0)
        if ch.isalpha():
            ch = ch.upper()
            chValue = ord(ch) - 64
            col *= 26
            col += chValue
        elif ch.isdigit():
            chValue = ord(ch) - 48
            row *= 10
            row += chValue
    return (row-1, col-1)



