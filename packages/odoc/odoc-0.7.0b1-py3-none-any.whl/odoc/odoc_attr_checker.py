
'''
    Pattern:
        chk_* functions check whether a value is appropriate, may modify it to be appropriate (see
            for example chk_color, and if a value is unsuitable throw an exception.
            chk_* functions return the (possibly modified) value, which should be used for the
            .attribute

        get_* are like chk_* functions, but do not throw exceptions.  They return None instead
'''

import re

def chk_str(key, val, lst=None):

    if not isinstance(val, str):
        raise TypeError(f'{key} should be a string not {type(val).__name__}')

    if lst is not None and val not in lst:
        raise ValueError(f'{key}, {val} not one of {lst}')

    return val


def chk_bool(key, val):

    if isinstance(val, bool):
        return val

    raise TypeError(f"{key} should be a boolean not {type(val).__name__}")


def chk_over_underline(key, val):

    if val is None:
        return None

    if not isinstance(val, str):
        raise TypeError(f'{key} should be a string not {type(val).__name__}')

    match val:
        case '-' | '=' | '-!' | '.' | '.!' | '--' | '--!' | '|' | '|!' | '.-' | '.-!' | \
            '..-' | '..-!' | '~' | '~!' | '~~':
            return val
        case 'single' | 'solid': return '-'
        case 'double': return '='
        case 'bold': return '-!'
        case 'dotted': return '.'
        case 'dotted bold': return '.!'
        case 'dash': return '--'
        case 'dash bold': return '--!'
        case 'long-dash': return '|'
        case 'long-dash': return '|!'
        case 'dot-dash': return '.-'
        case 'dot-dash bold': return '.-!'
        case 'dot-dot-dash': return '..-'
        case 'dot-dot-dash bold': return '..-!'
        case 'wave': return '~'
        case 'wave bold': return '~!'
        case 'wave double': '~~'

    raise ValueError(f"{name} not a valid line-style for {key}")


def chk_strikeout(key, val):

    if val is None:
        return None

    if not isinstance(val, str):
        raise TypeError(f'{key} should be a string not {type(val).__name__}')

    val = val.lower()

    match val:
        case '-' | '=' | '-!' | '/' | 'x':
            return val
        case 'single' | 'solid': return '-'
        case 'double': return '='
        case 'bold': return '-!'

    raise ValueError(f"{name} not a valid line-style for {key}")


RE_POS_LEN_OR_PERC = re.compile('((?:\d+(?:\.\d+)?|\.\d+)(?:cm|mm|in|pt|pc|px|em|%){1})')

def chk_pos_len_or_perc(key, value):
    ''' Non-negative length or percent
        lengths are: 'cm', 'mm' 'in', 'pt' 'pc', 'px', 'em'
    '''

    match value:
        case 0:
            return '0'
        case str():
            value = value.replace(' ','')
            if RE_POS_LEN_OR_PERC.fullmatch(value):
                return value

    raise ValueError(f'{key} should be a non-negative length or percentage.')


RE_FONTSIZE = re.compile('((?:\d+(?:\.\d+)?|\.\d+)(?:cm|mm|in|pt|pc|px|em){1})')

def chk_fontsize(key, value):
    ''' Non-negative length or em
        lengths are: 'cm', 'mm' 'in', 'pt' 'pc', 'px', 'em'
        It seems that percentages are not supported by LibreOffice
    '''

    match value:
        case 0:
            return '0'
        case str():
            value = value.replace(' ','')
            if RE_FONTSIZE.fullmatch(value):
                return value

    raise ValueError(f'{key} should be a non-negative length.')



RE_POS_INT_OR_LEN_OR_PERC = re.compile('((?:\d+(?:\.\d+)?|\.\d+)(?:cm|mm|in|pt|pc|px|%)?)')

def chk_pos_int_or_len_or_perc_or_str(key, value, str_list):
    ''' Non-negative length or percent
        lengths are: 'cm', 'mm' 'in', 'pt' 'pc', 'px', 'em'
    '''

    match value:
        case int() if value >= 0:
            return str(int)
        case str():
            if value in str_list:
                return value

            value = value.replace(' ','')
            if RE_POS_INT_OR_LEN_OR_PERC.fullmatch(value):
                return value

    raise ValueError(f'{key} should be a non-negative length or percentage.')


RE_POS_LEN = re.compile('((?:\d+(?:\.\d+)?|\.\d+)(?:cm|mm|in|pt|pc|px){1})')

def get_pos_len(value):
    ''' Non-negative length or percent
        lengths are: 'cm', 'mm' 'in', 'pt' 'pc', 'px', 'em'
    '''

    match value:
        case 0:
            return '0'
        case str():
            value = value.replace(' ','')
            if RE_POS_LEN_OR_PERC.fullmatch(value):
                return value

    return None


def chk_pos_len(key, value):

    if (value := get_pos_len(value)) is None:
        raise ValueError(f'{key} should be a non-negative length or percentage.')
    return value


def chk_dbl_line_width(key, value):

    if isinstance(value,str):
        lst = value.split()
        if (len(lst) == 3 and
            RE_POS_LEN_OR_PERC.fullmatch(lst[0]) and
            RE_POS_LEN_OR_PERC.fullmatch(lst[1]) and
            RE_POS_LEN_OR_PERC.fullmatch(lst[2])):
            return value

    raise ValueError(f'{key} should a string with three lengths.')


RE_ANGLE = re.compile('((?:\d+(?:\.\d+)?|\.\d+)(?:deg|grad|rad)?)')

def chk_angle(key, value):
    ''' Positive integer which might be followed by deg grad or rad.  If no unit is given it defaults
        to degrees.
        However, LibreOffice only seems to accept numbers without deg,grad or rad.  So we do the
        simple thing and do the same
    '''

    match value:
        case int() if value >= 0:
            return str(value)
    '''
        case str():
            value = value.replace(' ','')
            if RE_ANGLE.fullmatch(value):
                return value
    '''

    raise ValueError(f'{key} should be an angle, i.e. an integer number representing degrees')


def chk_padding(key, value):
    ''' a list of 1 to 4 positive lengths '''

    if isinstance(value,str):
        lst = value.split()
        for l in lst:
            if not RE_POS_LEN_OR_PERC.fullmatch(l):
                break
        else:
            return value

    raise ValueError(f'{key} should a string with  one to four lengths.')


RE_COLOR_LONG = re.compile('#[a-f0-9]{6}')
RE_COLOR_SHORT = re.compile('#[a-f0-9]{3}')


def get_color(value):

    value = value.lower()

    if value.startswith('#'):
        if RE_COLOR_LONG.fullmatch(value):
            return value
        if RE_COLOR_SHORT.fullmatch(value):
            r = value[1]
            g = value[2]
            b = value[3]
            return f'#{r}{r}{g}{g}{b}{b}'

    return CSS3_NAMED_COLORS.get(value)


def chk_color(key, value):

    if not isinstance(value, str):
        raise ValueError(f'{key} expects a color-string')

    if (color := get_color(value)) is None:
        raise ValueError(f'{key} expects a color-string')

    return color


def chk_color_or_str(key, value, str_list):

    if not isinstance(value, str):
        raise ValueError(f'{key} expects a color-string')

    value = value.lower()

    if value in str_list:
        return value

    if (color := get_color(value)) is None:
        raise ValueError(f'{key} expects a color-string')

    return color


RE_DS_COLOR_LONG = re.compile('#(?:00|ff){3}')
RE_DS_COLOR_SHORT = re.compile('#[0f]{3}')

DS_COLORS = {
    'black': '#000000',
    'blue': '#0000ff',
    'lime': '#00ff00',
    'green': '#00ff00',  # be real - nobody will call it lime, even though that's css3-correct
    'cyan': '#00ffff',
    'red': '#ff0000',
    'magenta': '#ff00ff',
    'yellow': '#ffff00',
    'white': '#ffffff',
}

def chk_data_style_color(key, value):

    if not isinstance(value, str):
        raise ValueError(f'{key} expects a color-string')

    value = value.lower()

    if value.startswith('#'):
        if RE_DS_COLOR_LONG.fullmatch(value):
            pass
        elif RE_DS_COLOR_SHORT.fullmatch(value):
            r = value[1]
            g = value[2]
            b = value[3]
            value = f'#{r}{r}{g}{g}{b}{b}'
        else:
            raise ValueError(f'{key} expects a color-string')

        return value

    if (value := DS_COLORS.get(value)) is None:
        raise ValueError(f'{key} must be one of the eight basic colors')

    return value


def chk_int(key, value):

    if isinstance(value, int):
        return str(value)

    raise ValueError(f"{key} expects either a non-negative integer or one of {str_list}")


def chk_pos_int(key, value):

    if isinstance(value, int) and value >= 0:
        return str(value)

    raise ValueError(f"{key} expects either a non-negative integer or one of {str_list}")


def chk_pos_int_or_str(key, value, str_list):

    if isinstance(value, int) and value >= 0:
        return str(value)

    if isinstance(value, str):
        value = value.lower()

        if value in str_list:
            return value

    raise ValueError(f"{key} expects either a non-negative integer or one of {str_list}")


RE_PERCENT = re.compile('((?:\d+(?:\.\d+)?|\.\d+)\s*\%)')

def chk_perc_or_str(key, value, str_list):

    if isinstance(value, str):
        value = value.lower()

        if RE_PERCENT.fullmatch(value):
            value = value.replace(' ','')
            return value
        if value in str_list:
            return value

    raise ValueError(f'{key} should be a percentage or one of {str_list}')


def get_border_width(value):

    if value in ['thin', 'thick']:
        return value
    return get_pos_len(value)


def get_border_style(value):

    if value in ('none', 'hidden', 'dotted', 'dashed', 'solid', 'double', 'groove', 'ridge',
                'inset', 'outset'):
        return value
    return None


def get_border_color(value):

    if value == 'transparent':
        return value
    return get_color(value)


def get_border(value):

    if not isinstance(value, str):
        return None

    val_lst = value.split()
    if len(val_lst) > 3:
        return None

    a = []
    b = ''
    for v in val_lst:
        if (r := get_border_width(v)) is not None:
            a.append(r)
            b += 'w'
        elif (r:= get_border_style(v)) is not None:
            a.append(r)
            b += 's'
        elif (r:= get_border_color(v)) is not None:
            a.append(r)
            b += 'c'
        else:
            return None

    if  b not in ('', 'w', 'ws', 'wc', 'wsc', 's', 'sc', 'c'):
        return None

    if 'w' not in b:
        a.insert(0, '1pt')
        b = 'w' + b

    if 's' not in b:
        a.insert(1, 'solid')
        # b = 'wsc' if b[-1] == 'c' eise 'ws'


    return ' '.join(a)


def chk_border(key, value):

    if (value := get_border(value)) is None:
        raise ValueError(f"{key} a border should be a 'width type color' string")

    return value


def chk_shadow(key, value):
    ''' TODO STILL TO IMPLEMENT !!!
    '''

    return value


def chk_halign(key, val):

    if not isinstance(val, str):
        raise TypeError(f'{key} should be a string not {type(val).__name__}')

    lst = ('start', 'end', 'left', 'right', 'center', 'justify')
    if val not in lst:
        raise ValueError(f'{key}, {val} not one of {lst}')

    if val == 'left':  # libreoffice des not seem to support 'left' and 'right'
        return 'start'

    if val == 'right':
        return 'end'

    return val


# CSS3 named colors

# https://developer.mozilla.org/en-US/docs/Web/CSS/named-color

CSS3_NAMED_COLORS = {
    'black': '#000000',
    'silver': '#c0c0c0',
    'gray': '#808080',
    'white': '#ffffff',
    'maroon': '#800000',
    'red': '#ff0000',
    'purple': '#800080',
    'fuchsia': '#ff00ff',
    'green': '#008000',
    'lime': '#00ff00',
    'olive': '#808000',
    'yellow': '#ffff00',
    'navy': '#000080',
    'blue': '#0000ff',
    'teal': '#008080',
    'aqua': '#00ffff',
    'aliceblue': '#f0f8ff',
    'antiquewhite': '#faebd7',
    'aqua': '#00ffff',
    'aquamarine': '#7fffd4',
    'azure': '#f0ffff',
    'beige': '#f5f5dc',
    'bisque': '#ffe4c4',
    'black': '#000000',
    'blanchedalmond': '#ffebcd',
    'blue': '#0000ff',
    'blueviolet': '#8a2be2',
    'brown': '#a52a2a',
    'burlywood': '#deb887',
    'cadetblue': '#5f9ea0',
    'chartreuse': '#7fff00',
    'chocolate': '#d2691e',
    'coral': '#ff7f50',
    'cornflowerblue': '#6495ed',
    'cornsilk': '#fff8dc',
    'crimson': '#dc143c',
    'cyan': '#00ffff',
    'darkblue': '#00008b',
    'darkcyan': '#008b8b',
    'darkgoldenrod': '#b8860b',
    'darkgray': '#a9a9a9',
    'darkgreen': '#006400',
    'darkgrey': '#a9a9a9',
    'darkkhaki': '#bdb76b',
    'darkmagenta': '#8b008b',
    'darkolivegreen': '#556b2f',
    'darkorange': '#ff8c00',
    'darkorchid': '#9932cc',
    'darkred': '#8b0000',
    'darksalmon': '#e9967a',
    'darkseagreen': '#8fbc8f',
    'darkslateblue': '#483d8b',
    'darkslategray': '#2f4f4f',
    'darkslategrey': '#2f4f4f',
    'darkturquoise': '#00ced1',
    'darkviolet': '#9400d3',
    'deeppink': '#ff1493',
    'deepskyblue': '#00bfff',
    'dimgray': '#696969',
    'dimgrey': '#696969',
    'dodgerblue': '#1e90ff',
    'firebrick': '#b22222',
    'floralwhite': '#fffaf0',
    'forestgreen': '#228b22',
    'fuchsia': '#ff00ff',
    'gainsboro': '#dcdcdc',
    'ghostwhite': '#f8f8ff',
    'gold': '#ffd700',
    'goldenrod': '#daa520',
    'gray': '#808080',
    'green': '#008000',
    'greenyellow': '#adff2f',
    'grey': '#808080',
    'honeydew': '#f0fff0',
    'hotpink': '#ff69b4',
    'indianred': '#cd5c5c',
    'indigo': '#4b0082',
    'ivory': '#fffff0',
    'khaki': '#f0e68c',
    'lavender': '#e6e6fa',
    'lavenderblush': '#fff0f5',
    'lawngreen': '#7cfc00',
    'lemonchiffon': '#fffacd',
    'lightblue': '#add8e6',
    'lightcoral': '#f08080',
    'lightcyan': '#e0ffff',
    'lightgoldenrodyellow': '#fafad2',
    'lightgray': '#d3d3d3',
    'lightgreen': '#90ee90',
    'lightgrey': '#d3d3d3',
    'lightpink': '#ffb6c1',
    'lightsalmon': '#ffa07a',
    'lightseagreen': '#20b2aa',
    'lightskyblue': '#87cefa',
    'lightslategray': '#778899',
    'lightslategrey': '#778899',
    'lightsteelblue': '#b0c4de',
    'lightyellow': '#ffffe0',
    'lime': '#00ff00',
    'limegreen': '#32cd32',
    'linen': '#faf0e6',
    'magenta': '#ff00ff',
    'maroon': '#800000',
    'mediumaquamarine': '#66cdaa',
    'mediumblue': '#0000cd',
    'mediumorchid': '#ba55d3',
    'mediumpurple': '#9370db',
    'mediumseagreen': '#3cb371',
    'mediumslateblue': '#7b68ee',
    'mediumspringgreen': '#00fa9a',
    'mediumturquoise': '#48d1cc',
    'mediumvioletred': '#c71585',
    'midnightblue': '#191970',
    'mintcream': '#f5fffa',
    'mistyrose': '#ffe4e1',
    'moccasin': '#ffe4b5',
    'navajowhite': '#ffdead',
    'navy': '#000080',
    'oldlace': '#fdf5e6',
    'olive': '#808000',
    'olivedrab': '#6b8e23',
    'orange': '#ffa500',
    'orangered': '#ff4500',
    'orchid': '#da70d6',
    'palegoldenrod': '#eee8aa',
    'palegreen': '#98fb98',
    'paleturquoise': '#afeeee',
    'palevioletred': '#db7093',
    'papayawhip': '#ffefd5',
    'peachpuff': '#ffdab9',
    'peru': '#cd853f',
    'pink': '#ffc0cb',
    'plum': '#dda0dd',
    'powderblue': '#b0e0e6',
    'purple': '#800080',
    'rebeccapurple': '#663399',
    'red': '#ff0000',
    'rosybrown': '#bc8f8f',
    'royalblue': '#4169e1',
    'saddlebrown': '#8b4513',
    'salmon': '#fa8072',
    'sandybrown': '#f4a460',
    'seagreen': '#2e8b57',
    'seashell': '#fff5ee',
    'sienna': '#a0522d',
    'silver': '#c0c0c0',
    'skyblue': '#87ceeb',
    'slateblue': '#6a5acd',
    'slategray': '#708090',
    'slategrey': '#708090',
    'snow': '#fffafa',
    'springgreen': '#00ff7f',
    'steelblue': '#4682b4',
    'tan': '#d2b48c',
    'teal': '#008080',
    'thistle': '#d8bfd8',
    'tomato': '#ff6347',
    'turquoise': '#40e0d0',
    'violet': '#ee82ee',
    'wheat': '#f5deb3',
    'white': '#ffffff',
    'whitesmoke': '#f5f5f5',
    'yellow': '#ffff00',
    'yellowgreen': '#9acd32',
}



