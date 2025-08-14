
from .odoc_xml import XML_PROLOG, Element

class Manifest:

    def __init__(self):

        self.manifest = Element("manifest:manifest", attr={
            "xmlns:manifest": "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0",
            "manifest:version": "1.3",
            "xmlns:loext": "urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0",
        })

        self.manifest.add("manifest:file-entry", attr={
            "manifest:full-path": "/",
            "manifest:version": "1.3",
            "manifest:media-type": "application/vnd.oasis.opendocument.spreadsheet",
        })

    def add_file(self, an, mt):
        self.manifest.add("manifest:file-entry", attr={
            "manifest:full-path": an,
            "manifest:media-type": mt,
        })

    def write_to(self, strm):
        strm.write(XML_PROLOG)
        self.manifest.write_to(strm)


