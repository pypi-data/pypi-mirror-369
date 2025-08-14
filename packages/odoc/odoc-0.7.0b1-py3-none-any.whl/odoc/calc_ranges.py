
from .odoc_xml import Element
from .calc_util import address


class NamedExpressions:
    '''  NOTE: Names for cells, ranges and expressions must start with a letter, and
         contain only letters, numbers and underscore
    '''

    def __init__(self):

        self.names = set()
        self.named_expressions = Element('table:named-expressions')

    def __len__(self):
        return len(self.names)

    def create_range(self, name, base_cell, cell_range, print_range=False,
        filter_=False, repeat_row=False, repeat_col=False):

        if name in self.names:
            raise RuntimeError(f"{name} already specified as named range/expression")

        self.check_name(name)

        el = self.named_expressions.add('table:named-range', attr={
                'table:name': name,
                'table:base-cell-address': base_cell,
                'table:cell-range-address': cell_range,
            })

        if any([print_range, filter_, repeat_row, repeat_col]):
            lst = []
            if print_range: list.append('print-range')
            if filter_: list.append('filter')
            if repeat_row: list.append('repeat_row')
            if repeat_col: list.append('repeat_col')

            el['table:range-usable-as'] = F"{' '.join(lst)}"

        self.names.add(name)
        return el

    def create_expr(self, name, base_cell, expression):

        if name in self.names:
            raise RuntimeError(f"{name} already specified as named range/expression")

        self.check_name(name)

        el = self.named_expressions.add('table:named-expression', attr={
                'table:name': name,
                'table:base-cell-address': base_cell,
                'table:expression': expression,
            })

        self.names.add(name)
        return el

    @staticmethod
    def check_name(name):
        if len(name) == 0:
            raise RuntimeError('Invalid range or expression name')

        ac = ord(name[0])
        if not((65 <= ac <= 90) or (96 <= ac <= 122)):
            raise RuntimeError(f'Name {name} invalid, it must start with a letter')

        for c in name[1:]:
            ac = ord(c)
            if not ((48 <= ac <= 57) or (65 <= ac <= 90) or (96 <= ac <= 122) or (c == "_")):
                raise RuntimeError(f'Name {name} invalid, only letters, numbers and underscore allowed')


class GlobalNamedExpressions(NamedExpressions):

    def add_range(self, name, sheet, row, col, row2=None, col2=None, *, print_range=False,
        filter_=False, repeat_row=False, repeat_col=False):

        base_cell = address(sheet, row, col)
        cell_range = address(sheet, row, col, row2, col2)

        return self.create_range(name, base_cell, cell_range, print_range, filter_,
            repeat_row, repeat_col)

    def add_expr(self, name, sheet, row, col, expression):
        ''' expression is a standard formula without the leading '='
        '''

        base_cell = address(sheet, row, col)
        return self.create_expr(name, base_cell, expr)


class LocalNamedExpressions(NamedExpressions):

    def __init__(self, sheet_name):
        super().__init__()
        self.sheet_name = sheet_name  # only set for local named expressions

    def add_range(self, name, row, col, row2=None, col2=None, *, print_range=False,
        filter_=False, repeat_row=False, repeat_col=False):

        base_cell = address(self.sheet_name, row, col)
        cell_range = address(self.sheet_name, row, col, row2, col2)

        return self.create_range(name, base_cell, cell_range, print_range, filter_,
            repeat_row, repeat_col)

    def add_expr(self, name, row, col, expression):
        ''' expression is a standard formula without the leading '='
        '''

        base_cell = address(self.sheet_name, row, col)
        return self.create_expr(self.sheet_name, base_cell, expr)






