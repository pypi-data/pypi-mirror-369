
XML_PROLOG = '<?xml version="1.0" encoding="UTF-8"?>'


ESC_TRANSLATIONS = str.maketrans({
    "&": "&amp;",
    "'": "&apos;",
    '"': "&quot;",
    "<": "&lt;",
    ">": "&gt;",
    # "\t": "<text:tab>",
    # "\n": "<text:line-break>",
})


class Element:

    def __init__(self, name,*, text=None, attr=None):

        self._name = name
        self._text = text

        self.attributes = {}
        self.children = []

        if attr is not None:
            self.attributes.update(attr)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    def __setitem__(self, key, value):
        self.attributes[key] = value

    def __getitem__(self, key):
        return self.attributes[key]

    def __delitem__(self, key):
        del self.attributes[key]

    def hash_value(self):
        ''' Build a hash-value by using all attributes which are not None
            and sorting them they attribute name.
            The hash_values of the children are also included, but the children
            are not sorted.
        '''

        hash_list = []
        for k,v in self.attributes.items():
            if v is None: continue
            hash_list.append((k,v))

        hash_list.sort(key=lambda x: x[0])

        hash_list.append(self.name)

        for c in self.children:
            hash_list.append(c.hash_value())

        if self.text:
            hash_list.append(self.text)

        return hash(tuple(hash_list))

    def add(self, eon, *, text=None, attr=None):
        ''' Add a child-element, NOTE: children can only be added, but not removed, which is
            fine within the scope of this library.
            returns the added child to enable function chaining

            eon can either be another Element object or the name of a new element (i.e. a string)
            In case eon is another Element, it is added as a child. test and attr are ignored
            In case eon is a string, then eon is the the name of a new Element to be created.
            text and attr are used in the creation.
        '''

        match eon:
            case Element():
                self.children.append(eon)
                return eon
            case str():
                new_el = Element(eon, text=text, attr=attr)
                self.children.append(new_el)
                return new_el
            case list() | tuple():
                for el in eon:
                    self.add(el)
            case _:
                raise TypeError("eon needs to be a string, an Element-object, or a sequence of these.")

    def write_to(self, strm):

        def attr_type_filter(val):

            match val:
                case bool():
                    return 'true' if val else 'false' # LibreOffice is sometimes case-sensitive
                case str():
                    val = val.replace("&", "&amp;")
                    val = val.replace(">", "&gt;")
                    val = val.replace("<", "&lt;")
                    val = val.replace('"', "&quot;")

                    return val

            return val

        attr_str =  ''.join([f' {K}="{attr_type_filter(V)}"' for K,V in self.attributes.items()])

        esc_txt = self._text and str(self._text).translate(ESC_TRANSLATIONS)

        if self.children:
            strm.write(f"<{self._name}{attr_str}>{esc_txt or ''}")
            for child in self.children:
                child.write_to(strm)
            strm.write(f"</{self._name}>")
        else:
            if esc_txt:
                strm.write(f"<{self._name}{attr_str}>{esc_txt}</{self._name}>")
            else:
                strm.write(f"<{self._name}{attr_str}/>")








