
import copy
from decimal import Decimal
import datetime

from pathlib import Path

from .odoc_xml import Element
from .calc_util import address, local_address

from .calc_ranges import LocalNamedExpressions

from .calc_styles import (TableStyle, RowStyle, ColumnStyle, CellStyle, DataStyle, GraphicStyle,
    FontFace)

class Sheet:

    def __init__(self, doc, name):

        self.doc = doc

        self._name = name
        self.style = TableStyle()

        self.cells = {}    # keys are cell indices, values are Cell, Row, and Column objects
        self.rows = {}
        self.cols = {}

        self.last_row = 0
        self.last_col = 0

        self.named_roe = LocalNamedExpressions(self._name)

        self.max_col = 0  # the highest row / column index
        self.max_row = 0

        self._row_dispatcher = Rows(self)
        self._col_dispatcher = Columns(self)

        # settings
        self.cursor_col = 0   # cursor will be placed in this row and column on load
        self.cursor_row = 0

        self.view_first_col = 0  # on load the page is scrolled to show this column as the left-most
        self.view_first_row = 0  # on load the page is scrolled to show this row as the top-most

        self.zoom = 100  # percentage zoom value
        self.show_grid = True

    @property
    def name(self):
        return self._name

    @property
    def cell_count(self):
        return len(self.cells)

    @property
    def row(self):
        return self._row_dispatcher

    @property
    def col(self):
        return self._col_dispatcher

    def hide(self):
        # Hiding is done via a function to bring it in line with row and column hiding
        self.display = False

    def get_row(self, idx):
        if (row := self.rows.get(idx)) is None:
            self.rows[idx] = (row := Row())

            self.max_row = max(self.max_row, idx)

        return row

    def get_col(self, idx):
        if (col := self.cols.get(idx)) is None:
            self.cols[idx] = (col := Column())

            self.max_col = max(self.max_col, idx)

        return col

    def get_cell(self, rowcol):

        if (cell := self.cells.get(rowcol)) is None:
            self.cells[rowcol] = (cell := Cell())
            row, col = rowcol

            self.max_row = max(self.max_row, row)
            self.max_col = max(self.max_col, col)

            self.get_row(row).update_max_col(col)

        return cell

    def __setattr__(self, name, val):

        if name in TableStyle.ATTRIBUTES:
            self.style.__setattr__(name, val)
            return

        super().__setattr__(name, val)

    def _coord_parse_key(self, part, last):

        p = p2 = None

        match part:
            case int():
                p, p2 = part, None
            case slice():
                match part.start, part.stop, part.step:
                    case None, None, None:
                        p, p2 = last, None
                    case None, None, int(inc):
                        p, p2 = last+inc, None
                    case None, int(rr), None:
                        p, p2 = last, last + rr
                    case None, int(rr), int(inc):
                        p, p2 = last+inc, last + inc + rr
                        if p > p2: p, p2 = p2, p
                    case int(p), int(p2), None:
                        if p > p2:
                            p, p2 = p2, p  # don't know if it wouldn't be better to raise an exception
                    case _:
                        raise ValueError(f'Invalid coordinate {part.start}:{part.stop}:{part.step}')

        if p < 0 or (p2 is not None and p2 < 0):
            raise ValueError('Coordinates must be positive integer')

        return p, p2

        raise RuntimeError(f'Invalid coordinates {part}')

    def _key_to_cell_coord(self, key):

        if isinstance(key, slice):  # i.e. a single slice, this should be a '::'
            if any((key.start,key.stop, key.step)):
                raise RuntimeError(f'Invalid coordinate')
            return CellCoord(self.last_row, self.last_col)

        if not isinstance(key, tuple) or len(key) != 2:
            raise RuntimeError('Only 2 dimensional sheets are supported')

        row, row2 = self._coord_parse_key(key[0], self.last_row)
        col, col2 = self._coord_parse_key(key[1], self.last_col)

        coord = CellCoord(row, col,  row2, col2)
        return coord

    def _key_to_row_coord(self, key):
        row, row2 = self._coord_parse_key(key, self.last_row)
        coord = RowColCoord(row, row2)
        return coord

    def _key_to_col_coord(self, key):
        col, col2 = self._coord_parse_key(key, self.last_col)
        coord = RowColCoord(col, col2)
        return coord

    def __setitem__(self, key, val):
        coord = self._key_to_cell_coord(key)
        self.last_row = coord.row
        self.last_col = coord.col

        if coord.is_range():
            if isinstance(val, str) and val.startswith('='):  # array formula
                af = ArrayFormula(val, coord.n_rows(), coord.n_cols())
                self.get_cell(coord.rowcol).assign(af, self)
                return

            for rowcol in coord.rowcol_range():
                self.get_cell(rowcol).assign(val, self)
        else:
            ''' Setting cell values from a list is only possible if cell coordinates reference a
                single cell - not a range. as a base cell is needed.
                The alternative would be to require a range, which fits the list exactly - sort
                of broadcasting = but that would be more complicated for the user.
            '''
            if isinstance(val, (list, tuple)):
                row, col = coord.rowcol
                for i_col, v_col in enumerate(val):  # move across columns
                    if v_col is Ellipsis: continue
                    if isinstance(v_col, (list, tuple)):
                        for i_row, v_row in enumerate(v_col):  # move across rows
                            if v_row is Ellipsis: continue
                            self.get_cell((row+i_row, col+i_col)).assign(v_row, self)
                    else:
                        self.get_cell((row, col+i_col)).assign(v_col, self)
            else:
                self.get_cell(coord.rowcol).assign(val, self)

    def __getitem__(self, key):
        coord = self._key_to_cell_coord(key)
        return CellRep(self, coord)

    def register_fonts(self):

        ff = self.doc.font_face

        for cell in self.cells.values():
            if isinstance(cell.style, CellStyle):
                if (fn := cell.style.text_prop.get('font_name')) is not None:
                    if fn not in ff:
                        ff[fn] = FontFace(family=fn)
                if (fn := cell.style.text_prop.get('font_name_asian')) is not None:
                    if fn not in ff:
                        ff[fn] = FontFace(family=fn)
                if (fn := cell.style.text_prop.get('font_name_complex')) is not None:
                    if fn not in ff:
                        ff[fn] = FontFace(family=fn)

    def element(self):

        ''' Here should go the code to figure out 'covered-cell', which are a result of merged cells,
            and mark them by setting covered-True.  However, LibreOffice seems to be fine without this.
        '''

        style_name = self.doc.get_style_name(self.style)

        table = Element("table:table", attr={"table:name": self.name,
            "table:style-name": style_name,})

        for col in range(self.max_col + 1):
            table.add(self.get_col(col).element(self))

        for row in range(self.max_row + 1):
            table_row = table.add(self.get_row(row).element(self))

            for col in range(self.get_row(row).max_col + 1):
                if (cell := self.cells.get((row, col))) is not None:
                    table_row.add(cell.element(self))
                else:
                    table_row.add(Element("table:table-cell"))

        if self.named_roe:
            table.add(self.named_roe.named_expressions)

        return table


class Rows:

    def __init__(self, sheet):
        self.sheet = sheet

    def __getitem__(self, key):
        coord = self.sheet._key_to_row_coord(key)
        return RowRep(self.sheet, coord)


class RowRep:

    __slots__ = ['sheet', 'coord']

    def __init__(self, sheet, coord):
        self.sheet = sheet
        self.coord = coord

    def _set_row_attr(self, idx, name, val):
        row = self.sheet.get_row(idx)
        row.style.__setattr__(name, val)

    def hide(self):
        for idx in self.coord.idx_range():
            self.sheet.get_row(idx).hidden = True

    def __setattr__(self, name, val):

        if name in RowStyle.ATTRIBUTES:
            if not self.coord.is_range():
                if isinstance(val, (list, tuple)):
                    for i, v in enumerate(val):
                        if v is Ellipsis: continue
                        self._set_row_attr(self.coord.idx+i, name, v)
                else:
                    self._set_row_attr(self.coord.idx, name, val)
            else:
                for idx in self.coord.idx_range():
                    self._set_row_attr(idx, name, val)
            return

        super().__setattr__(name, val)


class Row:

    def __init__(self):
        self.max_col = -1  # the highest column index in that row
        self.style = RowStyle()
        self.hidden = False

    def update_style(self, style_dict):
        self.style.update(style_dict)

    def update_max_col(self, idx):
        if idx > self.max_col:
            self.max_col = idx

    def element(self, sheet):
        style_name = sheet.doc.get_style_name(self.style)
        el = Element("table:table-row", attr={"table:style-name": style_name,})

        if self.hidden:
            el['table:visibility'] = 'collapse'

        return el


class Columns:

    def __init__(self, sheet):
        self.sheet = sheet

    def __getitem__(self, key):
        coord = self.sheet._key_to_col_coord(key)
        return ColumnRep(self.sheet, coord)


class ColumnRep:

    __slots__ = ['sheet', 'coord']

    def __init__(self, sheet, coord):
        self.sheet = sheet
        self.coord = coord

    def hide(self):
        for idx in self.coord.idx_range():
            self.sheet.get_col(idx).hidden = True

    def _set_col_attr(self, idx, name, val):
        col = self.sheet.get_col(idx)
        col.style.__setattr__(name, val)

    def __setattr__(self, name, val):

        if name in ColumnStyle.ATTRIBUTES:
            if not self.coord.is_range():
                if isinstance(val, (list, tuple)):
                    for i, v in enumerate(val):
                        if v is Ellipsis: continue
                        self._set_col_attr(self.coord.idx+i, name, v)
                else:
                    self._set_col_attr(self.coord.idx, name, val)
            else:
                for idx in self.coord.idx_range():
                    self._set_col_attr(idx, name, val)
            return

        super().__setattr__(name, val)


class Column:

    def __init__(self):
        self.style = ColumnStyle()
        self.hidden = False

    def update_style(self, style_dict):
        self.style.update(style_dict)

    def element(self, sheet):
        style_name = sheet.doc.get_style_name(self.style)

        el = Element("table:table-column", attr={"table:style-name": style_name,
            "table:default-cell-style-name": "Default", })

        if self.hidden:
            el['table:visibility'] = 'collapse'

        return el


class RowColCoord:

    def __init__(self, idx, idx2):
        # idx row or col for single row or col addressing
        # idx2 second coordinate for ranges

        self.idx = idx
        self.idx2 = idx2

    def idx_range(self):
        return range(self.idx, (self.idx2 or self.idx) +1)

    def is_range(self):
        return self.idx2 is not None


class CellCoord:
    ''' Used to disentangle cell-coordinates from square bracket calls.
        These might be ov the simple form [row,col] to address a single cell, or
        [row:row2, col:col2] to address a range
    '''

    def __init__(self,row=None, col=None, row2=None, col2=None):

            self.row = row
            self.col = col
            self.row2 = row2
            self.col2 = col2

    @property
    def rowcol(self):
        return (self.row, self.col)

    def rowcol_range(self):
        for r in range(self.row, (self.row2 or self.row) +1):
            for c in range(self.col, (self.col2 or self.col) +1):
                yield (r, c)

    def is_range(self):
        return self.row2 is not None or self.col2 is not None

    def n_rows(self):
        ''' number of rows spanned over by a range '''
        return 1 if self.row2 is None else (abs(self.row2 - self.row) + 1)

    def n_cols(self):
        ''' number of columns spanned over by a range '''
        return 1 if self.col2 is None else (abs(self.col2 - self.col) + 1)


class Cell:

    def __init__(self):
        self.content = None
        self.style = CellStyle()
        self.objects = []

        self.rows_spanned = 1
        self.cols_spanned = 1
        self.covered = False  # only used in the final phase of the document creation

    def assign(self, value, sheet):
        ''' if value is a CellStyle object, value is assigned to self.style
            otherwise value is assigned to self.content.
            This behavior is useful, since it allows to set styles in the same way
            as content.
        '''
        match value:
            case CellStyle():
                self.style.update(value)
            case DataStyle():
                self.style.data_style = value
            case Note():
                self.objects.append(value)
            case Image():
                self.objects.append(value)
            case _:
                self.content = value

    def element(self, sheet):

        el = Element('table:table-cell' if not self.covered else  'table:covered-table-cell')

        el['table:style-name'] = sheet.doc.get_style_name(self.style)

        if self.rows_spanned > 1:
            el['table:number-rows-spanned'] = str(self.rows_spanned)

        if self.cols_spanned > 1:
            el['table:number-columns-spanned'] = str(self.cols_spanned)

        match self.content:
            case bool():
                # NOTE: The bool() section has to come before the int() section, since
                # isinstance(bool(1) , int) returns True
                value = self.content
                el["office:value-type"] = "boolean"
                el["office:boolean-value"] =  'true' if value else 'false'
                el.add("text:p", text=value)
            case float() | int() | Decimal():
                value = str(self.content)
                el["office:value-type"] = "float"
                el["office:value"] = value
                el.add("text:p", text=value)
            case datetime.datetime() | datetime.date():
                value = self.content.isoformat()
                el["office:value-type"] = "date"
                el["office:date-value"] = value
                el.add("text:p", text=value)
            case datetime.time():
                value = self.content
                el["office:value-type"] = "time"
                el["office:time-value"] = f'PT{value.hour:02}H{value.minute:02}M{value.second:02}S'
                el.add("text:p", text=value.isoformat())
            case datetime.timedelta():
                raise NotImplemented()   # TODO
            case str():
                value = self.content

                if value and value[0] == '=':
                    ''' The minimal formula spec is used, as the type of the result
                        of the formula cannot be determined here.
                    '''
                    el["table:formula"]= 'of:' + value
                else:
                    if value and value[0] == "'":  # otherwise it will be doubled
                        value = value[1:]

                    el["office:value-type"] = "string"
                    el.add("text:p", text=value)

            case HyperLink():
                value = self.content
                el["office:value-type"] = "string"
                p = el.add("text:p")
                p.add('text:a', attr={'xlink:href': value.url, 'xlink:type': 'simple'},
                        text=value.text)

            case Percent():
                value = float(self.content.value)
                el["office:value-type"] = "percentage"
                el["office:value"] = value
                el.add("text:p", text=f"{value:%}")

            case Currency():
                # currency only works in conjunction with a currency style
                # TODO: generate a currency style, if none is given by the user.
                # On the other hand, just a normal number plus a style can replace
                # currency anyways.
                value = float(self.content.value)

                el["office:value-type"] = "currency"
                el["office:currency"] = self.content.currency
                el["office:value"] = value
                el.add("text:p", text=f"{value} {self.content.currency}")

            case ArrayFormula():
                value = self.content
                el["table:formula"] = 'of:' + value.formula
                el["table:number-matrix-rows-spanned"] = value.n_rows
                el["table:number-matrix-columns-spanned"] = value.n_cols

            case None:
                pass

            case _:
                value = str(self.content)
                el["office:value-type"] = "string"
                el["calcext:value-type"] = "error"
                el.add("text:p", text=value)

        for obj in self.objects:
            el.add(obj.element(sheet))

        return el


class CellRep:

    __slots__ = ['sheet', 'coord']

    def __init__(self, sheet, coord):
        ''' sheet a Sheet-object, coord a CellCoord object
        '''
        self.sheet = sheet
        self.coord = coord

    def address(self, spec='$$$$'):
        ''' local address without sheet name '''
        coord = self.coord
        return local_address(coord.row, coord.col, coord.row2, coord.col2, spec=spec)

    def full_address(self, spec='$$$$$'):
        ''' address including sheet name '''
        coord = self.coord
        return address(self.sheet.name, coord.row, coord.col, coord.row2, coord.col2, spec=spec)

    def merge(self):
        cell = self.sheet.get_cell(self.coord.rowcol)
        cell.rows_spanned = self.coord.n_rows()
        cell.cols_spanned = self.coord.n_cols()

    @property
    def content(self):
        if self.coord.is_range():
            raise NotImplemented() # TODO

        cell = self.sheet.get_cell(self.coord.rowcol)
        return cell.content

    def _set_cell_attr(self, rowcol, name, val):
        cell = self.sheet.get_cell(rowcol)
        cell.style.__setattr__(name, val)

    def __setattr__(self, name, val):

        if CellStyle.has_attr(name):
            if not self.coord.is_range():
                if isinstance(val, (list, tuple)):
                    row, col = self.coord.rowcol
                    for i_col, v_col in enumerate(val):  # move across columns
                        if v_col is Ellipsis: continue
                        if isinstance(v_col, (list, tuple)):
                            for i_row, v_row in enumerate(v_col):  # move across rows
                                if v_row is Ellipsis: continue
                                self._set_cell_attr((row+i_row, col+i_col), name, v_row)
                        else:
                            self._set_cell_attr((row, col+i_col), name, v_col)
                else:
                    self._set_cell_attr(self.coord.rowcol, name, val)
            else:
                for rowcol in self.coord.rowcol_range():
                    self._set_cell_attr(rowcol, name, val)
            return

        if name == 'name':  # global named cell or range
            self.sheet.doc.named_roe.add_range(val, self.sheet.name,
                self.coord.row, self.coord.col, self.coord.row2, self.coord.col2)
            return

        if name == 'local_name':
            self.sheet.named_roe.add_range(val,
                self.coord.row, self.coord.col, self.coord.row2, self.coord.col2)
            return

        super().__setattr__(name, val)


class Percent:
    ''' Just a container for percentage values '''

    def __init__(self, value):
        self.value = value


class Currency:
    ''' Just a container for currency values '''

    def __init__(self, value, currency):
        self.value = value
        self.currency = currency


class ArrayFormula:

    def __init__(self, formula, n_rows, n_cols):
        self.formula = formula
        self.n_rows = n_rows
        self.n_cols = n_cols


class HyperLink:

    def __init__(self, text, url):
        self.text = text
        self.url = url


class Note:

    def __init__(self, text, creator=None):
        self.text= text
        self.creator = creator

    def element(self, sheet):

        el = Element('office:annotation')
        el.add('text:p', text=self.text)

        el.add('dc:date', text=datetime.datetime.now().isoformat())
        if self.creator is not None:
            el.add('dc:creator', text=self.creator)

        return el


class Image:
    ''' Image to be placed on a spreadsheet.

        Image(path, width=None, height=None, mimetype=None,
            z_index=None, x=None, y=None, background=False, )

        path: path the the image file
        width, height: in css length units, e.g. '15mm' or '20px'
                width and height are optional only if the Pillow-library is installed.
        mimetype: mimetype of the image, optional only if the Pillow-library is installed
        z_index; where to place the image in z-diretion
        x,y: offset from the upper left corner of the anchor cell in css length units.
    '''
    '''
        TODO: bring these attributes up
        name: used to reference graphical attributes, currently unused in odoc
        style: must be a GraphicStyle object if given.  The GraphicStyle object is odoc
            is currently still very rudimentary - so there is not much use for this parameter
        text_style: this must be a ParagraphStyle object.  The ParagrahStyle object is odoc
            is currently still very rudimentary - so there is not much use for this parameter
        text: text to be placed over the image.
    '''

    ATTRIBUTES = set(('name', 'width', 'height', 'mimetype',
         'z_index', 'x', 'y', 'background', 'style', 'text_style', 'text'))

    def __init__(self, path, **attr):
        self.path = Path(path)
        self.attr = {}

        for name, value in attr.items():
            self.__setattr__(name, value)

        if self.style is None:
            self.style = GraphicStyle()

        if not all((self.width, self.height, self.mimetype)):
            try:
                from PIL import Image as PImage
            except ModuleNotFoundError:
                raise RuntimeError('Pillow needs to be installed to use Image')

            with PImage.open(path) as img:
                if self.mimetype is None:
                    self.mimetype = f'image/{img.format}'
                if self.width is None:
                    self.width = img.width    # if int() width and height are in pixels
                if self.height is None:
                    self.height = img.height  # setting width and height as length strings is also possible
                                      # e.g. '55.3mm' etc.

    def __setattr__(self, name, value):

        if name in Image.ATTRIBUTES:
            self.attr[name] = value
            return

        super().__setattr__(name, value)

    def __getattribute__(self, name):

        if name in Image.ATTRIBUTES:
            return self.attr.get(name)

        return super().__getattribute__(name)

    def element(self, sheet):

        el = Element('draw:frame')

        for name, value in self.attr.items():
            match name:
                case 'name':
                    el['draw:name']= value
                case 'width':
                    el['svg:width'] = \
                        f'{self.width}px' if isinstance(self.width, int) else self.width
                case 'height':
                    el['svg:height'] = \
                        f'{self.height}px' if isinstance(self.height, int) else self.height
                case 'z_index':
                    el['draw:z-index']= value
                case 'x':
                    el['svg:x'] = value
                case 'y':
                    el['svg:y'] = value
                case 'background':
                    if value:
                        el['table:table-background'] = "true"
                case 'style':
                    el['draw:style-name'] = sheet.doc.get_style_name(value)
                case 'text-style':
                    el['draw:text-style-name']= sheet.doc.get_style_name(value)
                case _:
                    pass

        el_img = el.add('draw:image', attr={
            'xlink:type':"simple", 'xlink:show': "embed", 'xlink:actuate': "onLoad",
            'xlink:href': sheet.doc.get_image_href(self.path, self.mimetype),
            'draw:mime-type': self.mimetype,
        })
        el_txt = el_img.add('text:p')
        if 'text' in self.attr:
            el_txt.text = self.attr['text']

        return el


