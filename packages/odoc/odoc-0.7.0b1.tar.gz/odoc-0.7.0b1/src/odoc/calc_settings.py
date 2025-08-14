
import datetime
from decimal import Decimal

from .odoc_xml import XML_PROLOG, Element


class Settings:

    def __init__(self, doc):
        self.doc = doc

    def write_to(self, strm):

        docSettings = Element("office:document-settings", attr={
            "xmlns:office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
            "xmlns:ooo": "http://openoffice.org/2004/office",
            "xmlns:xlink": "http://www.w3.org/1999/xlink",
            "xmlns:config": "urn:oasis:names:tc:opendocument:xmlns:config:1.0",
            "office:version": "1.3",
        })

        settings = docSettings.add("office:settings")


        def add_ci(el, name, type_, value=None):
            ''' add a config-item to xml element el '''
            if value is None: return

            match value:
                case None: return
                case bool():
                    txt = 'true' if value else 'false'
                case float() | int() | Decimal():
                    txt = str(value)
                case str():
                    txt = value

            el.add("config:config-item", attr={"config:name": name, "config:type": type_}, text=txt)

        #--- add view setting --------

        view_settings = settings.add("config:config-item-set", attr={'config:name': 'ooo:view-settings'})

        views = view_settings.add("config:config-item-map-indexed", attr={"config:name": 'Views'})
        views_me = views.add("config:config-item-map-entry")
        add_ci(views_me, 'ViewId', 'string', 'view1')

        tables = views_me.add('config:config-item-map-named', attr={"config:name":'Tables'})
        for sheet_name, sheet in self.doc.sheets.items():
            sheet_cime  = tables.add('config:config-item-map-entry', attr={"config:name":sheet_name})

            add_ci(sheet_cime, "CursorPositionX", "int", sheet.cursor_col)
            add_ci(sheet_cime, "CursorPositionY", "int", sheet.cursor_row)
            add_ci(sheet_cime, "PositionLeft", "int", sheet.view_first_col)
            add_ci(sheet_cime, "PositionBottom", "int", sheet.view_first_row)
            add_ci(sheet_cime, "ZoomValue", "int", sheet.zoom)
            add_ci(sheet_cime, "ShowGrid", "boolean", sheet.show_grid) #

        add_ci(views_me, "ActiveTable", "string", self.doc.active_sheet)
        add_ci(views_me, "ShowZeroValues", "boolean", self.doc.show_zero_values)
        add_ci(views_me, "ShowNotes", "boolean", self.doc.show_notes)
        add_ci(views_me, "ShowFormulasMarks", "boolean", self.doc.show_formula_marks)
        add_ci(views_me, "FormulaBarHeight", "short", self.doc.formula_bar_height)
        add_ci(views_me, "HasColumnRowHeaders", "boolean", self.doc.rowcol_headers)
        add_ci(views_me, "HasSheetTabs", "boolean", self.doc.sheet_tabs)
        add_ci(views_me, "IsValueHighlightingEnabled", "boolean", self.doc.value_highlight)

        #--- add configs --------

        config = settings.add("config:config-item-set",
            attr={'config:name': 'ooo:configuration-settings'})

        # specifies if the user-specific settings saved within a document should be loaded with
        # the document.
        add_ci(config, "ApplyUserData", "boolean", True)
        add_ci(config, "AutoCalculate", "boolean", True)
        add_ci(config, "SaveThumbnail", "boolean", True)

        add_ci(config, "ShowPageBreaks", "boolean", self.doc.show_page_breaks)
        add_ci(config, "LoadReadonly", "boolean", self.doc.load_readonly)
        add_ci(config, "IsDocumentShared", "boolean", self.doc.shared)

        strm.write(XML_PROLOG)
        docSettings.write_to(strm)







