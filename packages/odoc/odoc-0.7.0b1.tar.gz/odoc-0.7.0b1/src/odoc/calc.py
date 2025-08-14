
import io
import zipfile
from decimal import Decimal
import datetime

from .odoc_xml import XML_PROLOG, Element
from .calc_sheet import Sheet
from .calc_ranges import GlobalNamedExpressions
from .calc_styles import (StyleBase, DataStyle, TableStyle, RowStyle, ColumnStyle, CellStyle,
    GraphicStyle, ParagraphStyle )

from .calc_meta import Meta
from .calc_manifest import Manifest
from .calc_settings import Settings
from .calc_styles import Styles
from .version import __version__

class Calc:
    """Calc - Open Document Format (ODF) spreadsheets
    """

    version = f"odoc {__version__}"

    def __init__(self, autoInit=True):

        self.counter = Counter()

        self.manifest = Manifest()
        self.meta = Meta(self)
        self.settings = Settings(self)
        self.styles = Styles(self)

        self.sheets = {}                            # keys are table names, values are Sheet objects
        self.named_roe = GlobalNamedExpressions()   # global named ranges or expressions
        self.images = {}                            # keys are file-system paths to the images,
                                                    #values are ImageFile objects

        # just an alias, users might find it more intuitive if fontface and officestyles are part
        # of the global calc-document.
        self.font_face = self.styles.font_face
        self.office_style = self.styles.office_style

        #--- meta data -----------------
        self.creation_date = None   # should be a datatime.datetime object

        self.title = None
        self.subject = None
        self.comment = None
        self.keywords = []
        self.user_data = []

        self.contributor = None
        self.coverage = None
        self.identifier = None
        self.publisher = None
        self.relation = None
        self.source = None
        self.type_ = None
        self.rights = None

        # ---- settings ----
        self.active_sheet = None
        self.formula_bar_height = 1
        self.show_formula_marks = False
        self.rowcol_headers = True
        self.sheet_tabs = True
        self.load_readonly = False
        self.shared = False
        self.show_grid = True
        self.show_notes = True
        self.show_page_breaks = False
        self.show_zero_values = True
        self.value_highlight = False

        #--- XML ------------------
        self.document_content = Element("office:document-content", attr={
            "xmlns:meta": "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
            "xmlns:office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
            "xmlns:fo": "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
            "xmlns:ooo": "http://openoffice.org/2004/office",
            "xmlns:xlink": "http://www.w3.org/1999/xlink",
            "xmlns:dc": "http://purl.org/dc/elements/1.1/",
            "xmlns:style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
            "xmlns:text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
            "xmlns:draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
            "xmlns:dr3d": "urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0",
            "xmlns:svg": "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
            "xmlns:chart": "urn:oasis:names:tc:opendocument:xmlns:chart:1.0",
            "xmlns:rpt": "http://openoffice.org/2005/report",
            "xmlns:table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
            "xmlns:number": "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0",
            "xmlns:ooow": "http://openoffice.org/2004/writer",
            "xmlns:oooc": "http://openoffice.org/2004/calc",
            "xmlns:of": "urn:oasis:names:tc:opendocument:xmlns:of:1.2",
            "xmlns:tableooo": "http://openoffice.org/2009/table",
            "xmlns:calcext": "urn:org:documentfoundation:names:experimental:calc:xmlns:calcext:1.0",
            "xmlns:drawooo": "http://openoffice.org/2010/draw",
            "xmlns:loext": "urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0",
            "xmlns:field": "urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0",
            "xmlns:math": "http://www.w3.org/1998/Math/MathML",
            "xmlns:form": "urn:oasis:names:tc:opendocument:xmlns:form:1.0",
            "xmlns:script": "urn:oasis:names:tc:opendocument:xmlns:script:1.0",
            "xmlns:dom": "http://www.w3.org/2001/xml-events",
            "xmlns:xforms": "http://www.w3.org/2002/xforms",
            "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xmlns:formx": "urn:openoffice:names:experimental:ooxml-odf-interop:xmlns:form:1.0",
            "xmlns:xhtml": "http://www.w3.org/1999/xhtml",
            "xmlns:grddl": "http://www.w3.org/2003/g/data-view#",
            "xmlns:css3t": "http://www.w3.org/TR/css3-text/",
            "xmlns:presentation": "urn:oasis:names:tc:opendocument:xmlns:presentation:1.0",
            "office:version": "1.3",
        })

        self.office_scripts = self.document_content.add("office:scripts")

        self._font_face_decls_el = self.document_content.add("office:font-face-decls")

        self.auto_styles = self.document_content.add("office:automatic-styles")
        self.auto_style_names = {}  # keys are style hash values, values are style names

        self.office_body = self.document_content.add("office:body")
        self.office_spreadsheet = self.office_body.add("office:spreadsheet")
        self.office_spreadsheet.add("table:calculation-settings", attr={
            "table:automatic-find-labels": "false",
            "table:use-regular-expressions": "false",
            "table:use-wildcards": "true",
        })

        self.office_spreadsheet.add(self.named_roe.named_expressions)

    @property
    def table_count(self):
        return len(self.sheets);

    @property
    def cell_count(self):
        return sum((S.cell_count for S in self.sheets.values()))

    @property
    def object_count(self):
        return 0

    def add_user_data(self, name, value):

        match value:
            case bool():
                self.user_data.append((name, 'boolean', 'true' if value else 'false'))
            case float() | int() | Decimal():
                self.user_data.append((name, 'float', str(value)))
            case datetime.date():
                self.user_data.append((name, 'date', value.isoformat()))
            case datetime.datetime():
                self.user_data.append((name, 'dateTime', value.isoformat()))
            case datetime.timedelta():
                raise NotImplementedError('time-durations are not yet implemented')
            case _:
                self.user_data.append((name, 'string', str(value)))


    def __getitem__(self, name):
        ''' get or create a sheet
        '''
        return self.get_sheet(name)

    def get_sheet(self, name):
        ''' sheet management:
            sheets can be created, but they cannot be deleted, renamed or re-ordered.
            This should be ok, since this library is concerned with creating new
            spreadsheets from scratch, but not for interactive work with these spreadsheets.
        '''

        if not name:
            raise ValueError('A sheet name must be provided.')

        if (sheet := self.sheets.get(name)) is not None:
            return sheet

        sheet = Sheet(self, name)
        self.sheets[name] = sheet
        return sheet

    def _get_style_name(self, style):

        el = style.element()

        # the hash value needs to be calculated on an object, which still lacks the
        # style:name attribute - otherwise the hash would always differ just because of the name.
        hash_val = el.hash_value()

        if (style_name := self.auto_style_names.get(hash_val)) is not None:
            return style_name

        style_name = f'{style.PREFIX}{self.counter.inc(f"auto_style_{style.PREFIX}")}'
        el['style:name'] = style_name
        self.auto_styles.add(el)
        self.auto_style_names[hash_val] = style_name

        return style_name

    def get_style_name(self, style=None):

        match style:
            case None:
                return 'Default'
            case str():
                return Styles.escape_style_name(style)
            case RowStyle() | ColumnStyle() | TableStyle() | GraphicStyle() | ParagraphStyle():
                pass
            case DataStyle():
                # only DataStyle might have a map
                if (map_lst := style.get('map')) is not None:
                    for condition in map_lst:
                        if not isinstance(condition.style, DataStyle):
                            raise TypeError('Styles in DataStyle-conditions must be DataStyles')

                        condition.style = self.get_style_name(condition.style)
            case CellStyle():
                if style.style is not None:   # if style.style is set it is the name of an office-style
                    return style.style

                if style.data_style is not None:
                    style.data_style = self.get_style_name(style.data_style)
            case _:
                raise TypeError('style is not a style !?!')

        return self._get_style_name(style)

    def get_image_href(self, path, mimetype):

        if path in self.images:
            return self.images[path][0]

        href = f'Pictures/Image{self.counter.inc("image")}{path.suffix}'
        self.images[path] = (href, mimetype)
        return href

    def write_to(self, strm):

        # This is ugly here, but there isn't a better place to put it
        # If the user still explicitly declares font-faces later, those will overwrite these,
        # so there's no damage done here.
        '''
        if name in ['font_name', 'font_name_asian', 'font_name_complex'] :
            if val not in self.sheet.doc.font_face:
                self.sheet.doc.font_face[val] = FontFace(family=val)
        '''

        # For a font-face to be used it must appear in the content file
        # This seems a bit redundant as there are also font-faces declared
        # in the styles file. .It's handled here like in LibreOffice, the same
        # section is included in content as well as styles.

        # first check if there undeclared fonts are used

        for sheet in self.sheets.values():
            sheet.register_fonts()

        for k, v in self.font_face.items():
            el = v.element()
            el['style:name'] = k
            self._font_face_decls_el.add(el)

        for sheet in self.sheets.values():
            sheet_element = sheet.element()
            self.office_spreadsheet.add(sheet_element)

        strm.write(XML_PROLOG)
        self.document_content.write_to(strm)

    def save(self, filename):

        self.styles.register_fonts()

        def write_file(archive, filename, part):
            with io.StringIO() as strm:
                part.write_to(strm)
                archive.writestr(filename, strm.getvalue())
                self.manifest.add_file(filename, 'text/xml')

        with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as arch:
            arch.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")

            write_file(arch, "meta.xml", self.meta)
            write_file(arch, "content.xml", self)
            write_file(arch, "settings.xml", self.settings)
            write_file(arch, "styles.xml", self.styles)

            if self.images:
                for fn, (an, mt) in self.images.items():
                    arch.write(fn, an)
                    self.manifest.add_file(an, mt)

            write_file(arch, "META-INF/manifest.xml", self.manifest)


class Counter:

    def __init__(self):
        self.counter = {}

    def get(self, key, default=0):
        return self.counter.setdefault(key, int(default))

    def set_(self, key, value):
        self.counter[key] = int(value)

    def inc(self, key, default=0):
        ''' increments a counter by one.
            If key does not exist, a new counter will be set up set to default.
            The method returns the value of the counter __before__ the increment.
        '''
        value = self.counter.setdefault(key, int(default))
        self.counter[key] = value + 1
        return value







