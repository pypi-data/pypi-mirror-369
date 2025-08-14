
from decimal import Decimal
import datetime

from .odoc_xml import XML_PROLOG, Element

class Meta:

    def __init__(self, doc):

        self.doc = doc

    def write_to(self, strm):

        meta_el = Element("office:document-meta", attr={
            "xmlns:grddl": "http://www.w3.org/2003/g/data-view#",
            "xmlns:meta": "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
            "xmlns:office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
            "xmlns:ooo": "http://openoffice.org/2004/office",
            "xmlns:xlink": "http://www.w3.org/1999/xlink",
            "xmlns:dc": "http://purl.org/dc/elements/1.1/",
            "office:version": "1.3",
        })
        office_meta = meta_el.add("office:meta")

        def write_item(name, value):
            if value is not None:
                office_meta.add(name, text=str(value))

        if self.doc.creation_date is not None:
            office_meta.add("meta:creation-date", text=self.doc.creation_date.isoformat())
        else:
            office_meta.add("meta:creation-date", text=datetime.datetime.now().isoformat())

        write_item("meta:generator", self.doc.version)

        write_item("dc:title", self.doc.title)
        write_item("dc:subject", self.doc.subject)
        write_item("dc:description", self.doc.comment)
        write_item("dc:contributor", self.doc.contributor)
        write_item("dc:coverage", self.doc.coverage)
        write_item("dc:identifier", self.doc.identifier)
        write_item("dc:publisher", self.doc.publisher)
        write_item("dc:relation", self.doc.relation)
        write_item("dc:source", self.doc.source)
        write_item("dc:type", self.doc.type_)
        write_item("dc:rights", self.doc.rights)

        for kw in self.doc.keywords:
            office_meta.add("meta:keyword", text=kw)

        for name, value_type, value in self.doc.user_data:
            office_meta.add("meta:user-defined", attr={
                'meta:name': name, 'meta:value-type': value_type,
                }, text=value)

        office_meta.add("meta:editing-cycles", text="1")

        doc_stats = office_meta.add("meta:document-statistic")

        doc_stats["meta:table-count"]= self.doc.table_count
        doc_stats["meta:cell-count"]= self.doc.cell_count
        doc_stats["meta:object-count"]= self.doc.object_count

        strm.write(XML_PROLOG)
        meta_el.write_to(strm)



