
import copy
import datetime

from .odoc_xml import XML_PROLOG, Element

from .odoc_attr_checker import *

__all__ = ['CellStyle', 'DataStyle', 'DateStyle', 'NumberStyle', 'ScientificStyle', 'FractionStyle',
    'FontFace', 'PercentStyle', 'BooleanStyle', 'DataCondition', 'Condition', 'ConditionBetween',
    'ConditionNotBetween', 'ConditionTrue', 'GraphicStyle', 'ParagraphStyle',
]


class Styles:

    def __init__(self, doc):

        self.doc = doc

        self.document_styles = Element('office:document-styles', attr={
            'office:version': "1.3" ,
            'xmlns:calcext': "urn:org:documentfoundation:names:experimental:calc:xmlns:calcext:1.0" ,
            'xmlns:chart': "urn:oasis:names:tc:opendocument:xmlns:chart:1.0" ,
            'xmlns:css3t': "http://www.w3.org/TR/css3-text/" ,
            'xmlns:dc': "http://purl.org/dc/elements/1.1/",
            'xmlns:dom': "http://www.w3.org/2001/xml-events" ,
            'xmlns:dr3d': "urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" ,
            'xmlns:draw': "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" ,
            'xmlns:drawooo': "http://openoffice.org/2010/draw" ,
            'xmlns:field': "urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0" ,
            'xmlns:fo': "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" ,
            'xmlns:form': "urn:oasis:names:tc:opendocument:xmlns:form:1.0" ,
            'xmlns:grddl': "http://www.w3.org/2003/g/data-view#" ,
            'xmlns:loext': "urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0" ,
            'xmlns:math': "http://www.w3.org/1998/Math/MathML" ,
            'xmlns:meta': "urn:oasis:names:tc:opendocument:xmlns:meta:1.0" ,
            'xmlns:number': "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" ,
            'xmlns:of': "urn:oasis:names:tc:opendocument:xmlns:of:1.2" ,
            'xmlns:office': "urn:oasis:names:tc:opendocument:xmlns:office:1.0" ,
            'xmlns:ooo': "http://openoffice.org/2004/office" ,
            'xmlns:oooc': "http://openoffice.org/2004/calc" ,
            'xmlns:ooow': "http://openoffice.org/2004/writer" ,
            'xmlns:presentation': "urn:oasis:names:tc:opendocument:xmlns:presentation:1.0" ,
            'xmlns:rpt': "http://openoffice.org/2005/report" ,
            'xmlns:script': "urn:oasis:names:tc:opendocument:xmlns:script:1.0" ,
            'xmlns:style': "urn:oasis:names:tc:opendocument:xmlns:style:1.0" ,
            'xmlns:svg': "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" ,
            'xmlns:table': "urn:oasis:names:tc:opendocument:xmlns:table:1.0" ,
            'xmlns:tableooo': "http://openoffice.org/2009/table" ,
            'xmlns:text': "urn:oasis:names:tc:opendocument:xmlns:text:1.0" ,
            'xmlns:xhtml': "http://www.w3.org/1999/xhtml" ,
            'xmlns:xlink': "http://www.w3.org/1999/xlink" ,
        })

        self._font_face_decls_el = self.document_styles.add('office:font-face-decls')

        self._office_styles_el = self.document_styles.add("office:styles")

        style = self._office_styles_el.add("style:default-style", attr={"style:family": "table-cell"})
        style.add("style:paragraph-properties", attr={
            "style:tab-stop-distance": "12.7mm"})
        style.add("style:text-properties", attr={
            "style:font-name": "Liberation Sans",
            "fo:font-size": "10pt",
            "fo:language": "en",
            "fo:country": "US",
        })

        auto_styles = self.document_styles.add("office:automatic-styles")

        # style = auto_styles.add("number:number-style", attr={
        #     "style:name": f"N{self.doc.counter.inc('data_style')}"})

        style = auto_styles.add("number:number-style", attr={
            "style:name": f'{NumberStyle.PREFIX}{self.doc.counter.inc(f"auto_style_{NumberStyle.PREFIX}")}'})
        style.add("number:number", attr={'number:decimal-places': "2",
            "number:min-integer-digits": "1", 'number:min-decimal-places':"2"})

        style = auto_styles.add("style:page-layout", attr={
            "style:name":  "Mpm1"})
        style.add("style:page-layout-properties", attr={
            "style:writing-mode": "lr-tb"})
        stylePageLayout1Header = style.add("style:header-style")
        stylePageLayout1HeaderProperties = \
            stylePageLayout1Header.add("style:header-footer-properties", attr={
            "fo:min-height": "7.5mm",
            "fo:margin-left": "0",
            "fo:margin-right": "0",
            "fo:margin-bottom": "2.5mm",
        })
        stylePageLayout1Footer = style.add("style:footer-style")
        stylePageLayout1FooterProperties = \
            stylePageLayout1Footer.add("style:header-footer-properties", attr={
            "fo:min-height": "7.5mm",
            "fo:margin-left": "0",
            "fo:margin-right": "0",
            "fo:margin-bottom": "2.5mm",
        })

        style = self.document_styles.add("office:master-styles")
        styleMasterPage1 = style.add("style:master-page", attr={
            "style:name": "Default",
            "style:page-layout-name": "Mpm1",
        })
        styleMasterPage1Header = styleMasterPage1.add("style:header")
        styleMasterPage1Header.add("text:p").add("text:sheet-name", text="???")
        styleMasterPage1.add("style:header-left", attr={"style:display": "false"})
        styleMasterPage1.add("style:header-first", attr={"style:display": "false"})
        styleMasterPage1Footer = styleMasterPage1.add("style:footer")
        styleMasterPage1Footer.add("text:p", text="Page ").add("text:page-number", text="1")
        styleMasterPage1.add("style:footer-left", attr={"style:display": "false"})
        styleMasterPage1.add("style:footer-first", attr={"style:display": "false"})

        #=== set up some font faces ===============================================================
        self.font_face = {}

        self.font_face['Liberation Sans'] = FontFace(family='Liberation Sans',
            generic_family= 'swiss', pitch='variable')

        self.font_face['Lucida Sans'] = FontFace(family='Lucida Sans',
            generic_family= 'system', pitch='variable')

        self.font_face['Tahoma'] = FontFace(family='Tahoma',
            generic_family= 'system', pitch='variable')

        #=== set up a bunch of office-styles =====================================================
        # user could still edit these, if so desired

        self.office_style = {}

        self.office_style['Default'] = CellStyle()

        self.office_style["Heading"] = CellStyle(parent='Default',
                                                shrink_fit=False,
                                                wrap=False,
                                                color="#000000",
                                                font_size = "24pt",
                                                bold = True,)

        self.office_style['Heading 1'] = CellStyle(parent='Heading', font_size = "18pt")
        self.office_style['Heading 2'] = CellStyle(parent='Heading', font_size = "12pt")

        self.office_style['Text'] = CellStyle(parent='Default', shrink_fit=False, wrap=False)
        self.office_style['Note'] = CellStyle(parent='Text',  bgcolor= "#ffffcc",
                                              border="0.74pt solid #808080", color="#333333" )
        self.office_style['Footnote'] = CellStyle(parent='Text', italic=True, color="#808080")
        self.office_style["Hyperlink"] = CellStyle(parent='Text',
                                                    underline='-', color="#0000ee" )
        self.office_style["Status"] = CellStyle(parent='Default', shrink_fit=False, wrap=False)
        self.office_style["Good"] = CellStyle(parent='Status', color="#006600",
                                              bgcolor="#ccffcc" )
        self.office_style["Neutral"] = CellStyle(parent='Status', color="#996600",
                                                 bgcolor="#ffffcc" )
        self.office_style["Bad"] = CellStyle(parent='Status', color="#cc0000",
                                             bgcolor="#ffcccc" )
        self.office_style["Warning"] = CellStyle(parent='Status', color="#cc0000" )
        self.office_style['Error'] = CellStyle(parent='Status',
                                            color="#ffffff", bgcolor="#cc0000", bold=True )

        self.office_style["Accent"] = CellStyle(parent='Default', bold=True)
        self.office_style["Accent 1"] = CellStyle(parent='Accent',
            color="#ffffff", bgcolor="#000000" )
        self.office_style["Accent 2"] = CellStyle(parent='Accent',
            color="#ffffff", bgcolor="#808080" )
        self.office_style["Accent 3"] = CellStyle(parent='Accent' , bgcolor="#dddddd" )

        self.office_style["Result"] = CellStyle(parent='Default', italic=True, bold=True,
                                                underline='-' )

        self.office_style['IsoDate'] = CellStyle(data_style=DateStyle(format='%F'))

    @staticmethod
    def escape_style_name(style_name):
        ''' Non-alphanumeric characters are replaced by their hex-code
        '''

        def e_char(c):
            num = ord(c)
            if ((num >= 48 and num <= 57) or
                (num >= 65 and num <= 90) or
                (num >= 97 and num <= 122)):
                return c

            return f'_{hex(num).upper()[2:]}_'

        return ''.join([e_char(C) for C in style_name])

    def create_office_style(self, style_name, style_family, parent_style_name=None):

        esc_style_name = Styles.escape_style_name(style_name)

        child =   self._office_styles_el.add("style:style", attr={
            "style:name": esc_style_name,
            "style:family": style_family,
        })
        if esc_style_name != style_name:
            child["style:display-name"] = style_name

        if (parent_style_name is not None):
            child["style:parent-style-name"] = parent_style_name
        return child

    def _get_office_data_style_name(self, style=None):

        match style:
            case None:
                return None
            case str():
                return Styles.escape_style_name(style)
            case DataStyle():

                ds_style_name = f'{style.PREFIX}{self.doc.counter.inc(f"auto_style_{style.PREFIX}")}'

                if (map_lst := style.get('map')) is not None:
                    for condition in map_lst:
                        if not isinstance(condition.style, DataStyle):
                            raise TypeError('Styles in DataStyle-conditions must be DataStyles')

                        condition.style = self._get_office_data_style_name(condition.style)

                # Keep the style definition, even if not used as it is part of a cell style
                style.attr['volatile'] = 'true'
                data_style_el = style.element()
                data_style_el['style:name'] = ds_style_name

                self._office_styles_el.add(data_style_el)

                return ds_style_name
            case _:
                raise TypeError('Expected DataStyle object for OfficeStyle data_style')


    def _add_office_style(self, style_name, element):
        esc_style_name = Styles.escape_style_name(style_name)

        if isinstance(element, CellStyle):
            data_style = element.get('data_style')
            element.attr['data_style'] = self._get_office_data_style_name(data_style)

        if isinstance(element, StyleBase):
            element = element.element()

        self._office_styles_el.add(element)

        element["style:name"] = esc_style_name

        if esc_style_name != style_name:
            element["style:display-name"] = style_name

        return element

    def register_fonts(self):
        ''' Register undeclared fonts in office-styles '''

        ff = self.font_face

        for osv in self.office_style.values():
            if isinstance(osv, CellStyle):
                if (fn := osv.text_prop.get('font_name')) is not None:
                    if fn not in ff:
                        ff[fn] = FontFace(family=fn)
                if (fn := osv.text_prop.get('font_name_asian')) is not None:
                    if fn not in ff:
                        ff[fn] = FontFace(family=fn)
                if (fn := osv.text_prop.get('font_name_complex')) is not None:
                    if fn not in ff:
                        ff[fn] = FontFace(family=fn)

    def write_to(self, strm):

        for k, v in self.font_face.items():
            el = v.element()
            el['style:name'] = k
            self._font_face_decls_el.add(el)

        for k, v in self.office_style.items():
            if 'parent' in v.attr and v.attr['parent'] not in self.office_style:
                raise RuntimeError(f"Parent-style '{v.attr['parent']}' for style '{k}' not defined")
            self._add_office_style(k, v)

        strm.write(XML_PROLOG)
        self.document_styles.write_to(strm)


class Attr:

    __slots__ = ['xml_name', 'checker', 'checker_para']

    def __init__(self, xml_name, checker, checker_para=None):
        self.xml_name =  xml_name
        self.checker =  checker
        self.checker_para = checker_para


class StyleBase:
    ''' NOTE: 'name' is not among the attributes, the name of the style is set automatically,
        or taken from the dictionary key in case of FontFace and office-styles.
        Name would also collide with the 'name' attribute for named ranges.

        'country', 'language' et. al. might appear in multiple places in an Element,
        e.g. NumberStyle elements might have 'fo:country' and 'fo:language in their text-properties,
        and 'number:country' and 'number:language' in their own attributes.  Setting 'country' or
        'language' in these cases will set _all_ '*:country', '*:language' attributes. Consider
        it not a bug, but a feature.
    '''

    __slots__ = ['attr']

    def __init__(self, attr=None):
        self.attr = {}

        if attr is not None:
            for k,v in attr.items():
                self.__setattr__(k, v)

    def __setattr__(self, name, value):

        if name == 'attr':
            super().__setattr__(name, value)
            return

        if (arec := self.ATTRIBUTES.get(name)) is None:
            raise AttributeError(f'{self.__class__.__name__} does not have attribute {name}')

        if value is None:
            del self.attr[name]
            return

        if arec.checker_para is None:
            self.attr[name] = arec.checker(name, value)
        else:
            self.attr[name] = arec.checker(name, value, arec.checker_para)

    def __getattr__(self, name):

        if name == 'attr':
            return self.attr

        if name in self.ATTRIBUTES:
            return self.attr.get(name)

        raise AttributeError(f'Style does not have attribute {name}')

    def __len__(self):
        return len(self.attr)

    def update(self, attr):

        if isinstance(attr, StyleBase):
            d = attr.attr
        elif isinstance(attr, dict):
            d = attr
        else:
            raise TypeError('Trying to update style with unsuitable type.')

        for k,v in d.items():
            self.__setattr__(k, v)

    def get(self, key, default=None):
        return self.attr.get(key, default)

    def element(self):

        el = Element(self.TAG)

        for name, value in self.attr.items():
            arec = self.ATTRIBUTES[name]
            el[arec.xml_name] = value

        return el


class FontFace(StyleBase):
    ''' FontFace(family, generic_family=None, pitch=None)
        generic_family should be one of ['decorative', 'modern', 'roman', 'script', 'swiss',
        'system'].  pitch takes either 'fixed' or 'variable'.

        The minimum font face declaration looks like this
                font_face['Bozo'] = FontFace(family='Helvetica')
        Where 'Bozo' is the name used with in the documen
        And 'Helvetica' the name of the font on the system. I.e. setting
        sheet[row,col].font_name = 'Bozo', will result in the cell being displayed in
       'Helvetica' font.  The other attributes serve to find equivalent replacements, in case
        the specified font is not available on the system.
    '''

    __slots__ = []

    TAG = "style:font-face"

    ATTRIBUTES= {
        'family': Attr('svg:font-family', chk_str),
        'generic_family': Attr('style:font-family-generic', chk_str,
                ('decorative', 'modern', 'roman', 'script', 'swiss', 'system')),
        'pitch': Attr('style:font-pitch', chk_str,   ('fixed', 'variable')),
        'adornments': Attr('style:font-adornments', chk_str)
    }

    def __init__(self, **attr):
        super().__init__(attr)


class TableProperties(StyleBase):

    __slots__ = []

    TAG = 'style:table-properties'

    ATTRIBUTES = {
        'display': Attr('table:display', chk_bool),
        'writing_mode': Attr('style:writing-mode', chk_str,
            ('lr-tb', 'rl-tb', 'tb-rl', 'tb-lr', 'lr', 'rl', 'tb', 'page')),
        'bgcolor': Attr('fo:background-color',chk_color),
        'break_after': Attr('fo:break-after', chk_str, ('auto', 'column', 'page')),
        'break_before': Attr('fo:break-before', chk_str, ('auto', 'column', 'page')),
        'keep_with_next': Attr('fo:keep-with-next', chk_str, ('auto', 'always')),
        'margin': Attr('fo:margin', chk_pos_len_or_perc),
        'margin_b': Attr('fo:margin-bottom', chk_pos_len_or_perc),
        'margin_l': Attr('fo:margin-left', chk_pos_len_or_perc),
        'margin_r': Attr('fo:margin-right', chk_pos_len_or_perc),
        'margin_t': Attr('fo:margin-top', chk_pos_len_or_perc),
        'may_break_between_rows': Attr('style:may-break-between-rows', chk_bool),
        'page_number': Attr('style:page-number', chk_pos_int_or_str),
        'rel_width': Attr('style:rel-width', chk_perc_or_str),
        'shadow': Attr('style:shadow', chk_shadow),
        'width': Attr('style:width', chk_pos_len),
        'align': Attr('table:align', chk_str, ('left', 'center', 'right', 'margins')),
        'border_model': Attr('table:border-model', chk_str, ('collapsing', 'separating')),
        'tab_color': Attr('table:tab-color', chk_color),
    }


class TableStyle(TableProperties):

    __slots__ = []

    DEFAULT = {
        "display": True,
        "writing_mode": "lr-tb",
    }

    PREFIX = 'ta'

    def __init__(self):
        super().__init__(TableStyle.DEFAULT)

    def element(self):

        el = Element("style:style", attr={
            "style:family": "table",
            "style:master-page-name": "Default",
        })

        el.add(super().element())

        return el


class RowProperties(StyleBase):

    __slots__ = []

    TAG = 'style:table-row-properties'

    ATTRIBUTES = {
        'height': Attr("style:row-height", chk_pos_len),
        'min_height': Attr("style:min-row-height", chk_pos_len),
        'optimal_height': Attr("style:use-optimal-row-height", chk_bool),
        'break_before': Attr("fo:break-before", chk_str, ('auto', 'column', 'page')),
        'break_after': Attr("fo:break-after", chk_str, ('auto', 'column', 'page')),
        'keep_together': Attr("fo:keep-together", chk_str, ('auto', 'always')),
        'bgcolor': Attr("fo:background-color", chk_color),
    }


class RowStyle(RowProperties):

    __slots__ = []

    # The user can modify default attributes here
    DEFAULT = {
            "height": "4.5mm",
            "break_before": "auto",
            "optimal_height" : True,
        }

    PREFIX = 'ro'

    def __init__(self):
        super().__init__(RowStyle.DEFAULT)

    def element(self):
        ''' NOTE: style:name will be set later !'''

        el = Element("style:style", attr={"style:family": "table-row",})

        # the default is optimal_height, this needs to be switched off in order
        # to use height
        if 'height' in self.attr and self.attr['height'] != self.DEFAULT['height']:
            self.optimal_height = False

        el.add(super().element())

        return el


class ColumnProperties(StyleBase):

    __slots__ = []

    TAG = 'style:table-column-properties'

    ATTRIBUTES = {
        'width': Attr("style:column-width", chk_pos_len),
        'break_before': Attr("fo:break-before", chk_str, ('auto', 'column', 'page')),
        'break_after': Attr("fo:break-after", chk_str, ('auto', 'column', 'page')),
    }


class ColumnStyle(ColumnProperties):

    __slots__ = []

    DEFAULT = {
            "width": "22mm",
            "break_before": "auto",
        }

    PREFIX = 'co'

    def __init__(self):
        super().__init__(ColumnStyle.DEFAULT)

    def element(self):
        ''' NOTE: style:name will be set later !'''

        el = Element("style:style", attr={"style:family": "table-column",})

        el.add(super().element())

        return el


class ParagraphProperties(StyleBase):

    __slots__ = []

    TAG = "style:paragraph-properties"

    ATTRIBUTES = {
        'halign': Attr("fo:text-align", chk_halign),
    }

    '''
    Attr('fo:background-color',),
    Attr('fo:border',),
    Attr('fo:border-bottom',),
    Attr('fo:border-left',),
    Attr('fo:border-right',),
    Attr('fo:border-top',),
    Attr('fo:break-after',),
    Attr('fo:break-before',),
    Attr('fo:hyphenation-keep',),
    Attr('fo:hyphenation-ladder-count',),
    Attr('fo:keep-together',),
    Attr('fo:keep-with-next',),
    Attr('fo:line-height',),
    Attr('fo:margin',),
    Attr('fo:margin-bottom',),
    Attr('fo:margin-left',),
    Attr('fo:margin-right',),
    Attr('fo:margin-top',),
    Attr('fo:orphans',),
    Attr('fo:padding',),
    Attr('fo:padding-bottom',),
    Attr('fo:padding-left',),
    Attr('fo:padding-right',),
    Attr('fo:padding-top',),
    Attr('fo:text-align',),
    Attr('fo:text-align-last',),
    Attr('fo:text-indent',),
    Attr('fo:widows',),
    Attr('style:auto-text-indent',),
    Attr('style:background-transparency',),
    Attr('style:border-line-width',),
    Attr('style:border-line-width-bottom',),
    Attr('style:border-line-width-left',),
    Attr('style:border-line-width-right',),
    Attr('style:border-line-width-top',),
    Attr('style:contextual-spacing',),
    Attr('style:font-independent-line-spacing',),
    Attr('style:join-border',),
    Attr('style:justify-single-word',),
    Attr('style:line-break',),
    Attr('style:line-height-at-least',),
    Attr('style:line-spacing',),
    Attr('style:page-number',),
    Attr('style:punctuation-wrap',),
    Attr('style:register-true',),
    Attr('style:shadow',),
    Attr('style:snap-to-layout-grid',),
    Attr('style:tab-stop-distance',),
    Attr('style:text-autospace',),
    Attr('style:vertical-align',),
    Attr('style:writing-mode',),
    Attr('style:writing-mode-automatic',),
    Attr('text:line-number',),
    Attr('text:number-lines',),
    '''


class ParagraphStyle(ParagraphProperties):
    ''' NOTE: No real support yet, just default settings '''

    __slots__ = []

    PREFIX = 'P'

    def __init__(self):
        super().__init__()

    def element(self):

        el = Element('style:style', attr={'style:family': "paragraph", })

        for name, value in self.attr.items():
            arec = self.ATTRIBUTES[name]
            match name:
                case 'halign':
                    el[arec.xml_name]= value
                    if "margin_l" not in self.attr:
                        el["fo:margin-left"]= "0"
                case _:
                    el[arec.xml_name] = value

        el.add('loext:graphic-properties', attr={
            'draw:fill': "none",
        })

        return el


class TextProperties(StyleBase):

    __slots__ = []

    TAG = "style:text-properties"

    ATTRIBUTES = {
        'bold': Attr(None, chk_bool),
        "italic": Attr(None, chk_bool),
        "underline": Attr(None, chk_over_underline),
        'underline_color': Attr("style:text-underline-color", chk_color_or_str, ('font-color',)),
        'strikeout': Attr(None, chk_strikeout),
        "overline": Attr(None, chk_over_underline),
        'overline_color': Attr("style:text-overline-color",chk_color_or_str, ('font-color',)),
        "skip_white_space": Attr(None, chk_bool),
        'country': Attr('fo:country', chk_str),
        'language': Attr('fo:language', chk_str),
        "color": Attr("fo:color", chk_color),
        "font_size": Attr(None, chk_fontsize),
        'font_name': Attr('style:font-name', chk_str),
        'font_name_asian': Attr('style:font-name-asian', chk_str),
        'font_name_complex': Attr('style:font-name-complex', chk_str),
        'font_family': Attr('style:font-family', chk_str),
        'text_shadow': Attr(None, chk_bool),
        'embossed': Attr(None, chk_bool),
        'engraved': Attr(None, chk_bool),
        'outline': Attr('style:text-outline', chk_bool),
    }

    """
    'fo:background-color'  - ignored by libreoffice

    'fo:font-family'
    'fo:font-variant'
    'fo:hyphenate'
    'fo:hyphenation-push-char-count'
    'fo:hyphenation-remain-char-count'

    'fo:letter-spacing'
    'fo:script'
    'fo:text-transform'
    'style:country-asian'
    'style:country-complex'
    'style:font-charset'
    'style:font-charset-asian'
    'style:font-charset-complex'
    'style:font-family-asian'
    'style:font-family-complex'
    'style:font-family-generic'
    'style:font-family-generic-asian'
    'style:font-family-generic-complex'
    'style:font-pitch'
    'style:font-pitch-asian'
    'style:font-pitch-complex'
    'style:font-size-rel'
    'style:font-size-rel-asian'
    'style:font-size-rel-complex'
    'style:font-style-name'
    'style:font-style-name-asian'
    'style:font-style-name-complex'
    'style:language-asian'
    'style:language-complex'
    'style:letter-kerning'
    'style:rfc-language-tag'
    'style:rfc-language-tag-asian'
    'style:rfc-language-tag-complex'
    'style:script-asian'
    'style:script-complex'
    'style:script-type'
    'style:text-blinking'
    'style:text-combine'
    'style:text-combine-end-char'
    'style:text-combine-start-char'
    'style:text-emphasize'
    'style:text-position'
    'style:text-rotation-angle'
    'style:text-rotation-scale'
    'style:text-scale'
    'style:use-window-font-color'
    'text:condition'
    'text:display
    """

    def element(self):

        el = Element(self.TAG)

        for name, value in self.attr.items():
            if value is None: continue
            arec = self.ATTRIBUTES[name]
            match name:
                case 'bold':
                    txt_val = 'bold' if value is True else 'normal'
                    el["fo:font-weight"] = txt_val
                    el["style:font-weight-asian"] = txt_val
                    el["style:font-weight-complex"] = txt_val

                case "italic":
                    txt_val = 'italic' if value is True else 'normal'
                    el["fo:font-style"] = txt_val
                    el["style:font-style-asian"] = txt_val
                    el["style:font-style-complex"] = txt_val

                case 'underline' | 'overline':
                    match value:
                        case '-': swt = 'solid', 'auto', 'single'
                        case '=': swt = 'solid', 'auto', 'double'
                        case '-!': swt = 'solid', 'bold', 'single'
                        case '.': swt = 'dotted', 'auto', 'single'
                        case '.!': swt = 'dotted', 'bold', 'single'
                        case '--': swt = 'dash', 'auto', 'single'
                        case '--!': swt = 'dash', 'bold', 'single'
                        case '|': swt = 'long-dash', 'auto', 'single'
                        case '|!': swt = 'long-dash', 'bold', 'single'
                        case '.-': swt = 'dot-dash', 'auto', 'single'
                        case '.-!': swt = 'dot-dash', 'bold', 'single'
                        case '..-': swt = 'dot-dot-dash', 'auto', 'single'
                        case '..-!': swt = 'dot-dot-dash', 'bold', 'single'
                        case '~': swt = 'wave', 'auto', 'single'
                        case '~!': swt = 'wave', 'bold', 'single'
                        case '~~': swt = 'wave', 'auto', 'double'

                    if name == 'underline':
                        el["style:text-underline-style"] = swt[0]
                        el["style:text-underline-width"] = swt[1]
                        el["style:text-underline-type"] = swt[2]

                        if 'underline_color' not in self.attr:
                            el["style:text-underline-color"] = "font-color"

                        if self.attr.get('skip_white_space', False):
                            el['style:text-underline-mode'] = 'skip-white-space'
                    else:
                        el["style:text-overline-style"] = swt[0]
                        el["style:text-overline-width"] = swt[1]
                        el["style:text-overline-type"] = swt[2]

                        if 'overline_color' not in self.attr:
                            el["style:text-overline-color"] = "font-color"

                        if self.attr.get('skip_white_space', False):
                            el['style:text-overline-mode'] = 'skip-white-space'

                case 'strikeout':
                    el['style:text-line-through-style'] = "solid"
                    el['style:text-line-through-width'] = "auto"
                    el['style:text-line-through-type'] = "single"

                    match value:
                        case '=':
                            el['style:text-line-through-type'] = "double"
                        case '-!':
                            el['style:text-line-through-width'] = "bold"
                        case '/':
                            el['style:text-line-through-text'] = '/'
                        case 'x':
                            el['style:text-line-through-text'] = 'x'

                    if self.attr.get('skip_white_space', False):
                        el['style:text-line-through-mode'] = 'skip-white-space'

                case "font_size":
                    el["fo:font-size"] = value
                    el["style:font-size-asian"]= value
                    el["style:font-size-complex"]= value
                case 'text_shadow':
                    # libreoffice supports only one setting for text-shadows (1pt 1pt)
                    if value is True:
                        el['fo:text-shadow'] = '1pt 1pt'
                case 'embossed':
                    if value is True:
                        el['style:font-relief'] = 'embossed'
                case 'engraved':
                    if value is True:
                        el['style:font-relief'] = 'engraved'
                case _ if arec.xml_name is not None:
                    el[arec.xml_name] = value

        return el


class CellProperties(StyleBase):

    __slots__ = []

    TAG = 'style:table-cell-properties'

    ATTRIBUTES = {
        'bgcolor': Attr("fo:background-color",chk_color_or_str, ('transparent',)),
        'valign': Attr("style:vertical-align", chk_str, ('top', 'middle', 'bottom', 'automatic')),
        "text_align_source": Attr("style:text-align-source", chk_str, ('fix', 'value-type')),
        "repeat_content": Attr("style:repeat-content", chk_bool),
        "wrap": Attr("fo:wrap-option", chk_bool),
        "protect": Attr("style:cell-protect", chk_str, ('formula-hidden', 'hidden-and-protected',
            'none', 'protected', 'protected formula-hidden')),
        'border': Attr("fo:border", chk_border),
        'border_b': Attr("fo:border-bottom", chk_border),
        'border_l': Attr("fo:border-left", chk_border),
        'border_r': Attr("fo:border-right", chk_border),
        'border_t': Attr("fo:border-top", chk_border),
        'border_width': Attr("style:border-line-width",chk_dbl_line_width),
        'border_width_b': Attr("style:border-line-width-bottom", chk_dbl_line_width),
        'border_width_l': Attr("style:border-line-width-left", chk_dbl_line_width),
        'border_width_r': Attr("style:border-line-width-right", chk_dbl_line_width),
        'border_width_t': Attr("style:border-line-width-top", chk_dbl_line_width),
        'padding': Attr("fo:padding", chk_padding),
        'padding_b': Attr("fo:padding-bottom", chk_pos_len),
        'padding_l': Attr("fo:padding-left", chk_pos_len),
        'padding_r': Attr("fo:padding-right", chk_pos_len),
        'padding_t': Attr("fo:padding-top", chk_pos_len),
        'diagonal_bl_tr': Attr("style:diagonal-bl-tr", chk_border),
        'diagonal_bl_tr_widths': Attr("style:diagonal-bl-tr-widths", chk_dbl_line_width),
        'diagonal_tl_br': Attr("style:diagonal-tl-br", chk_border),
        'diagonal_tl_br_widths': Attr("style:diagonal-tl-br-widths", chk_dbl_line_width),
        'direction': Attr('style:direction', chk_str, ('ltr', 'ttb')),
        'print_content': Attr('style:print-content', chk_bool),
        'rotation_align': Attr('style:rotation-align', chk_str, ('none', 'bottom', 'top', 'center')),
        'rotation_angle': Attr('style:rotation-angle', chk_angle),
        'shadow': Attr('style:shadow', chk_shadow ),
        'shrink_fit': Attr('style:shrink-to-fit', chk_bool),
        'writing_mode': Attr('style:writing-mode', chk_str, ('lr-tb', 'rl-tb', 'tb-rl', 'tb-lr',
                            'lr', 'rl', 'tb', 'page')),
    }

    def element(self):

        el = Element(self.TAG)

        for name, value in self.attr.items():
            arec = self.ATTRIBUTES[name]
            match name:
                case 'valign':
                    el["style:vertical-align"] = value
                    if "text_align_source" not in self.attr:
                        el["style:text-align-source"] = "fix"
                    if "repeat_content" not in self.attr:
                        el["style:repeat-content"] = "false"
                case "wrap":
                    el["fo:wrap-option"] = "wrap" if value else "no-wrap"
                case _:
                    el[arec.xml_name] = value

        return el


def chk_style(key, value):

    if isinstance(value, str):
        return value

    if isinstance(value, StyleBase):
        return copy.deepcopy(value)

    raise ValueError(f"{key} should be a style-object")


class CellStyle(StyleBase):

    SLOTS = ['cell_prop', 'text_prop', 'para_prop']

    ATTRIBUTES = {
        'style': Attr(None, chk_style),
        'parent': Attr(None, chk_str),
        'data_style': Attr(None, chk_style),
        'map': Attr(None, lambda name, value: value),
    }

    PREFIX = 'ce'

    def __init__(self, **attr):
        self.cell_prop = CellProperties()
        self.text_prop = TextProperties()
        self.para_prop = ParagraphProperties()

        super().__init__(attr)

        if self.parent is None:
            self.parent = 'Default'

    def __setattr__(self, name, value):

        if name in CellStyle.SLOTS:
            self.__dict__[name] = value
            return

        if name in CellProperties.ATTRIBUTES:
            self.cell_prop.__setattr__(name, value)
            return

        if name in TextProperties.ATTRIBUTES:
            self.text_prop.__setattr__(name, value)
            return

        if name in ParagraphProperties.ATTRIBUTES:
            self.para_prop.__setattr__(name, value)
            return

        if name == 'attr':
            super().__setattr__(name, value)
            return

        if (arec := self.ATTRIBUTES.get(name)) is None:
            raise AttributeError(f'{self.__class__.__name__} does not have attribute {name}')

        if arec.checker_para is None:
            self.attr[name] = arec.checker(name, value)
        else:
            self.attr[name] = arec.checker(name, value, arec.checker_para)

    def __getattr__(self, name):

        if name in CellProperties.ATTRIBUTES:
            return self.cell_prop.get(name)

        if name in TextProperties.ATTRIBUTES:
            return self.text_prop.get(name)

        if name in ParagraphProperties.ATTRIBUTES:
            return self.para_prop.get(name)

        return super().__getattr__(name)

    @staticmethod
    def has_attr(name):
        return (name in CellStyle.SLOTS or
            name in CellStyle.ATTRIBUTES or
            name in CellProperties.ATTRIBUTES or
            name in TextProperties.ATTRIBUTES or
            name in ParagraphProperties.ATTRIBUTES
        )

    def update(self, attr):

        if isinstance(attr, CellStyle):
            self.cell_prop.update(attr.cell_prop)
            self.text_prop.update(attr.text_prop)
            self.para_prop.update(attr.para_prop)

        super().update(attr)

    def element(self):
        # doc is not optional, as it is needed by text_prop to set up fonts

        el = Element("style:style", attr={
            "style:family": "table-cell",
            "style:parent-style-name": self.parent,
        })

        if isinstance(self.data_style, str):
            el['style:data-style-name'] = self.data_style

        if 'halign' in self.para_prop.attr and 'text_align_source' not in self.cell_prop.attr:
            self.cell_prop.text_align_source = 'fix'

        if self.cell_prop:
            el.add(self.cell_prop.element())
        if self.text_prop:
            el.add(self.text_prop.element())
        if self.para_prop:
            el.add(self.para_prop.element())

        if self.map is not None:
            for condition in self.map:
                match condition:
                    case Condition():
                        cstr = f'cell-content(){condition.cond}'
                    case ConditionBetween():
                        cstr = f'cell-content-is-between({condition.value1},{condition.value2})'
                    case ConditionNotBetween():
                        cstr = f'cell-content-is-not-between({condition.value1},{condition.value2})'
                    case ConditionTrue():
                        cstr = f'is-true-formula({condition.expr})'
                    case _:
                        raise TypeError('Not a condition')

                el.add('style:map', attr={
                    'style:base-cell-address': 'A1',
                    'style:condition': cstr,
                    'style:apply-style-name':  Styles.escape_style_name(condition.style),
                })

        return el


class DataStyle(StyleBase):

    __slots__ = StyleBase.__slots__

    PREFIX = 'N'

    def _element_common(self, el):

        for name, value in self.attr.items():
            arec = self.ATTRIBUTES[name]
            match name:
                case 'country' | 'language' | 'volatile':
                    el[arec.xml_name] = value
                case 'color':
                    el.add("style:text-properties", attr={"fo:color": value})
                case 'map':
                    for condition in value:
                        if not isinstance(condition, DataCondition):
                            raise TypeError('Only simple Conditions can be handled by DataStyles')

                        el.add('style:map', attr={
                            'style:base-cell-address': 'A1',
                            'style:condition': f'value() {condition.cond}',
                            'style:apply-style-name': condition.style,
                        })
                case _:
                    pass


class NumberStyle(DataStyle):
    ''' Data-style

        NOTE: Following attributes are apparently not supported by libreoffice:
            number:min-decimal-places, number:display-factor
            number:decimal-replacement
    '''

    __slots__ = DataStyle.__slots__

    ATTRIBUTES = {
        'country': Attr('number:country', chk_str),
        'language': Attr('number:language', chk_str),
        'volatile': Attr('style:volatile', chk_bool),
        'prefix': Attr(None, chk_str),
        'postfix': Attr(None, chk_str),
        'no_value': Attr(None, chk_bool),
        'grouping': Attr('number:grouping', chk_bool),
        'precision': Attr('number:decimal-places', chk_pos_int),
        'min_precision': Attr('number:min-decimal-places', chk_pos_int),
        'min_digits': Attr('number:min-integer-digits', chk_pos_int),

        'color': Attr("fo:color", chk_data_style_color),
        'map': Attr(None, lambda key, value: value),  # TODO put in proper check for list of Conditions
    }

    TAG = 'number:number-style'

    def __init__(self, **attr):
        super().__init__(attr)

    def element(self):

        el = Element(self.TAG)

        if (prefix := self.get('prefix')) is not None:
            el.add('number:text', text=prefix)

        if not self.get('no_value'):
            el_num = el.add('number:number')

        for name, value in self.attr.items():
            if name in ['prefix', 'postfix', 'map', 'color', 'country', 'language', 'volatile',
                'no_value']:
                continue

            arec = self.ATTRIBUTES[name]
            el_num[arec.xml_name] = value

        if 'min_digits' not in self.attr:
            el_num['number:min-integer-digits'] = '1'    # seems to be a mandatory field in libreoffice
        else:
            # min-integer-digits has no effect in libreoffice, unless decimal-places is specified
            if 'precision' not in self.attr:
                el_num['number:decimal-places'] = '0'

        if 'grouping' not in self.attr:
            el_num['number:grouping'] = 'true'

        if (postfix := self.get('postfix')) is not None:
            el.add('number:text', text=postfix)

        self._element_common(el)

        return el


class PercentStyle(NumberStyle):
    ''' Data-style
        percentage-style is almost identical to number-style.  Just the postfix is set to
        '%'. Using anything other than '%' will make LibreOffice ignore the style
    '''
    __slots__ = NumberStyle.__slots__

    TAG = 'number:percentage-style'

    def element(self):

        self.attr['postfix'] = '%'
        return super().element()


class ScientificStyle(DataStyle):
    ''' Data-style  '''

    __slots__ = DataStyle.__slots__

    ATTRIBUTES = {
        'country': Attr('number:country', chk_str),
        'language': Attr('number:language', chk_str),
        'volatile': Attr('style:volatile', chk_bool),
        'prefix': Attr(None, chk_str),
        'postfix': Attr(None, chk_str),
        'no_value': Attr(None, chk_bool),
        'grouping': Attr('number:grouping', chk_bool),
        'precision': Attr('number:decimal-places', chk_pos_int),
        'min_precision': Attr('number:min-decimal-places', chk_pos_int),

        'min_digits': Attr('number:min-integer-digits', chk_pos_int),
        'min_exp_digits': Attr('number:min-exponent-digits', chk_pos_int),
        'exp_interval': Attr('number:exponent-interval', chk_pos_int),
        'forced_exp_sign': Attr('number:forced-exponent-sign', chk_bool),

        'color': Attr("fo:color", chk_data_style_color),
        'map': Attr(None, lambda key, value: value),
    }

    TAG = 'number:number-style'

    def __init__(self, **attr):
        super().__init__(attr)

    def element(self):

        el = Element(self.TAG)

        if (prefix := self.get('prefix')) is not None:
            el.add('number:text', text=prefix)

        if not self.get('no_value'):
            el_num = el.add('number:scientific-number')

        for name, value in self.attr.items():
            if name in ['prefix', 'postfix', 'map', 'color', 'country', 'language', 'volatile',
                'no_value']:
                continue

            arec = self.ATTRIBUTES[name]
            el_num[arec.xml_name] = value

        if 'min_digits' not in self.attr:
            el_num['number:min-integer-digits'] = '1'     # seems to be a mandatory field in LibreOffice
        else:
            # min-integer-digits has no effect in LibreOffice, unless decimal-places is specified
            if 'precision' not in self.attr:
                el_num['number:decimal-places'] = '0'

        if 'forced_exp_sign' not in self.attr:
            el_num['number:forced-exponent-sign'] = 'true'
        if 'min_exp_digits' not in self.attr:
            el_num['number:min-exponent-digits'] = '2'
        if 'exp_interval' not in self.attr:
            el_num['number:exponent-interval'] = '1'

        if (postfix := self.get('postfix')) is not None:
            el.add('number:text', text=postfix)

        self._element_common(el)

        return el


class FractionStyle(DataStyle):
    ''' Data-style  '''

    __slots__ = DataStyle.__slots__

    ATTRIBUTES = {
        'country': Attr('number:country', chk_str),
        'language': Attr('number:language', chk_str),
        'volatile': Attr('style:volatile', chk_bool),
        'prefix': Attr(None, chk_str),
        'postfix': Attr(None, chk_str),
        'no_value': Attr(None, chk_bool),
        'grouping': Attr('number:grouping', chk_bool),
        'min_digits': Attr('number:min-integer-digits', chk_pos_int),
        'divisor': Attr('number:denominator-value', chk_int),
        'max_divisor': Attr('number:max-denominator-value', chk_pos_int),
        'min_divisor_digits': Attr('number:min-denominator-digits', chk_pos_int),
        'max_factor_digits': Attr('loext:max-numerator-digits', chk_pos_int),
        'min_factor_digits': Attr('number:min-numerator-digits', chk_pos_int),

        'color': Attr("fo:color", chk_data_style_color),
        'map': Attr(None, lambda key, value: value),
    }

    TAG = 'number:number-style'

    def __init__(self, **attr):
        super().__init__(attr)

    def element(self):

        el = Element(self.TAG)

        if (prefix := self.get('prefix')) is not None:
            el.add('number:text', text=prefix)

        if not self.get('no_value'):
            el_num = el.add('number:fraction')

        for name, value in self.attr.items():
            if name in ['prefix', 'postfix', 'map', 'color', 'country', 'language', 'volatile',
                'no_value']:
                continue

            arec = self.ATTRIBUTES[name]
            el_num[arec.xml_name] = value

        if (postfix := self.get('postfix')) is not None:
            el.add('number:text', text=postfix)

        self._element_common(el)

        return el


class BooleanStyle(DataStyle):
    ''' Data-style '''

    __slots__ = DataStyle.__slots__

    ATTRIBUTES = {
        'country': Attr('number:country', chk_str),
        'language': Attr('number:language', chk_str),
        'volatile': Attr('style:volatile', chk_bool),
        'prefix': Attr(None, chk_str),
        'postfix': Attr(None, chk_str),
        'no_value': Attr(None, chk_bool),

        'color': Attr("fo:color", chk_data_style_color),
        'map': Attr(None, lambda key, value: value),
    }

    TAG = 'number:boolean-style'

    def __init__(self, **attr):
        super().__init__(attr)

    def element(self):

        el = Element(self.TAG)

        if (prefix := self.get('prefix')) is not None:
            el.add('number:text', text=prefix)

        if not self.get('no_value'):
            el.add('number:boolean')

        if (postfix := self.get('postfix')) is not None:
            el.add('number:text', text=postfix)

        self._element_common(el)

        return el


class DateStyle(DataStyle):
    ''' Data-style

        Format, works like strftime, only a few format place-holders are different:

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

        $Q (non standard) quarter as '1st quarter' - '4th quarter'
        %q (non standard) quarter as Q1 - Q4

        %W week of the year number

        %D  Equivalent to %m/%d/%y
        %F  Isodate
        %r  time in am-pm format (%I:%M:%S%p)
        %R  time in 24 hour format (%H:%M)
        %T  time (%H:%M:%S)
    '''

    __slots__ = DataStyle.__slots__ + []

    TAG = 'number:date-style'

    ATTRIBUTES = {
        'country': Attr('number:country', chk_str),
        'language': Attr('number:language', chk_str),
        'volatile': Attr('style:volatile', chk_bool),
        'format': Attr(None, chk_str),
        'color': Attr("fo:color", chk_data_style_color),
        'map': Attr(None, lambda key, value: value),
    }

    def __init__(self, **attr):
        super().__init__(attr)

        if self.format is None:
            self.format = '%F'

    def element(self):

        el = Element(DateStyle.TAG)

        text_buf = ''
        parsing_percent = False

        for c in self.attr['format']:
            if parsing_percent:
                if c == '%':
                    text_buf += '%'
                    parsing_percent = False
                    continue
                else:
                    if text_buf:
                        el.add("number:text", text=text_buf)
                        text_buf = ''

                match c:
                    case 'Y':
                        el.add('number:year', attr={"number:style": "long"})
                    case 'y':
                        el.add('number:year', attr={"number:style": "short"})
                    case 'B':
                        el.add('number:month', attr={
                            'number:style': 'long', 'number:textual':'true' })
                    case 'b':
                        el.add('number:month', attr={
                            'number:style': 'short', 'number:textual':'true' })
                    case 'm':
                        el.add('number:month', attr={
                            'number:style': 'long', 'number:textual':'false' })
                    # case ???:
                    #     el.add('number:month', attr={
                    #         'number:style': 'short', 'number:textual':'false' })
                    case 'd':
                        el.add('number:day', attr={'number:style': 'long'})
                    case 'e':
                        el.add('number:day', attr={'number:style': 'short'})
                    case 'A':
                        el.add('number:day-of-week', attr={"number:style": "long"})
                    case 'a':
                        el.add('number:day-of-week', attr={"number:style": "short"})
                    case 'H':
                        el.add('number:hours', attr={"number:style": "long"})
                    case 'h':
                        el.add('number:hours', attr={"number:style": "short"})
                    case 'M':
                        el.add('number:minutes', attr={"number:style": "long"})
                    # case '???':
                    #     el.add('number:minutes', attr={"number:style": "short"})
                    case 'S':
                        el.add('number:seconds', attr={"number:style": "long"})
                    case 's':
                        el.add('number:seconds', attr={"number:style": "short"})
                    case 'p':
                        el.add('number:am-pm', attr={"number:style": "long"})
                    case 'E':
                        el.add('number:era', attr={"number:style": "long"})
                    # case ???:
                    #     el.add('number:era', attr={"number:style": "short"})
                    case 'Q':
                        el.add('number:quarter', attr={"number:style": "long"})
                    case 'q':
                        el.add('number:quarter', attr={"number:style": "short"})
                    case 'W':
                        el.add('number:week-of-year')
                    case 'D':
                        el.add("number:month", attr={"number:style": "long", 'number:textual':'false'})
                        el.add("number:text", text="/")
                        el.add("number:day", attr={"number:style": "long"})
                        el.add("number:text", text="/")
                        el.add("number:year", attr={"number:style": "long"})
                    case 'F':
                        el.add("number:year", attr={"number:style": "long"})
                        el.add("number:text", text="-")
                        el.add("number:month", attr={"number:style": "long", "textual": "false"})
                        el.add("number:text", text="-")
                        el.add("number:day", attr={"number:style": "long"})
                    case 'r':
                        el.add('number:hour', attr={"number:style": "long"})
                        el.add("number:text", text=":")
                        el.add('number:minutes', attr={"number:style": "long"})
                        el.add("number:text", text=":")
                        el.add('number:seconds', attr={"number:style": "long"})
                        el.add("number:text", text=" ")
                        el.add('number:am-pm', attr={"number:style": "long"})
                    case 'R':
                        el.add('number:hour', attr={"number:style": "long"})
                        el.add("number:text", text=":")
                        el.add('number:minutes', attr={"number:style": "long"})
                    case 'T':
                        el.add('number:hour', attr={"number:style": "long"})
                        el.add("number:text", text=":")
                        el.add('number:minutes', attr={"number:style": "long"})
                        el.add("number:text", text=":")
                        el.add('number:seconds', attr={"number:style": "long"})

                parsing_percent = False
            else:
                if c == '%':
                    parsing_percent = True
                else:
                    text_buf += c

        if text_buf:
            el.add("number:text", text=text_buf)
            text_buf = ''

        self._element_common(el)

        return el


class TimeStyle(DataStyle):
    ''' Data-style '''

    __slots__ = DataStyle.__slots__ + []
    # STILL TO IMPLEMENT

    def __init__(self, **attr):
        super().__init__(attr)


class DataCondition:
    ''' Data conditions are used in maps of DataStyles.
        The conditional styles must be also DataStyle objects

        NOTE that the styling capabilities are actually very limited.  Background-color
        cannot be changed at all.  Font-color is limited to the values:

        cyan #0ff , black #000, magenta #f0f, white #fff,
        lime #0f0, blue #00f, red #f00, yellow #ff0
    '''

    def __init__(self, cond, style):
        ''' cond should be of the form 'op value'. Possible ops are '<', '>', '<=', '>=',
            '=' or '!='.  value can be a number or a bool
        '''

        self.cond = cond.strip()
        self.style = style

        if not isinstance(style, DataStyle):
            raise TypeError('style in DataCondition needs to be a DataStyle')

        if 'map' in style.attr:
            ''' I don't know if this is mandated by the standard, but nested maps
                make implementing more complex, so it's left out for the time being
            '''
            raise RuntimeError('A Style used in a map, should not have a map.')


class ConditionBase:
    ''' Conditions based on ConditionBase are used in regular CellStyle maps.
        Conditional styles must be office-styles
    '''

    def __init__(self, style):
        self.style = style

        if not isinstance(style, str):
            raise ValueError('style must be the name of an office-style')


class Condition(ConditionBase):

    def __init__(self, cond, style):
        ''' cond should be of the form 'op value'. Possible ops are '<', '>', '<=', '>=',
            '=' or '!='.  value can be a constant e.g 42, the
            address of a cell, or a formula eg 'AVERAGE(A1:A10)'
        '''
        super().__init__(style)

        self.cond = cond.strip()


class ConditionBetween(ConditionBase):

    def __init__(self, value1, value2, style):
        ''' Condition evaluates to true if cell-content is between value1 and value2
        '''
        super().__init__(style)

        self.value1 = value1
        self.value2 = value2


class ConditionNotBetween(ConditionBase):

    def __init__(self, value1, value2, style):
        ''' Condition evaluates to true if cell-content is _NOT_ between value1 and value2
        '''
        super().__init__(style)

        self.value1 = value1
        self.value2 = value2


class ConditionTrue(ConditionBase):

    def __init__(self, expr, style):
        ''' Condition evaluates to true expr is True
        '''
        super().__init__(style)

        self.expr = expr


class GraphicStyle(StyleBase):
    ''' NOTE: No real support yet, just default settings '''

    __slots__ = StyleBase.__slots__ + []

    ATTRIBUTES = set()

    PREFIX = 'gr'

    def __init__(self):
        super().__init__()

    def __setattr__(self, name, value):
        pass

    def element(self):

        el = Element('style:style', attr={
            'style:family': "graphic",
            'style:parent-style-name': "Default",
        })

        el.add('style:graphic-properties', attr={
            'draw:stroke': "none",
            'draw:fill': "none",
            'style:mirror': "none",
            'loext:decorative': "false",
        })

        return el








