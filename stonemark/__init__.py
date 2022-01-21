"""
a strict version of commonmark
"""

# Basic Syntax
# 
# Element               Markdown Syntax
#
# Heading	                          H1 Heading    H2 Heading   H3 Heading
# first = heading is a level 1,       ==========    ==========   ----------
# second and subsequent = headings
# are level 2
#
# Bold                  **bold text**
#
# Italic	            *italicized text*
#
# Bold & Italic         ***bold, italicized text***
#
# Blockquote	        > blockquote
#
# Ordered List	        1. First item
#                       2. Second item
#                       3. Third item
#
# Unordered	List        - First item
#                       - Second item
#                       - Third item
#
# Code	                `code`
#
# Horizontal Rule       --- or ***
#
# Link	     (in-line)  [title](https://www.example.com)
#
#           (separate)  [title]  or [titel][id]
#                       ...
#                       [title | id]: <https://www.example.com>
#
# Image	                ![alt text](image.jpg)
#
#
# Extended Syntax
# These elements extend the basic syntax by adding additional features. Not all Markdown applications support these elements.
# 
# Element               Markdown Syntax
#
# Table                 | Syntax | Description |
#                       | ----------- | ----------- |
#                       | Header | Title |
#                       | Paragraph | Text |
#
# Fenced Code Block     ``` or ~~~
#                       {
#                           "firstName": "John",
#                           "lastName": "Smith",
#                           "age": 25
#                       }
#                       ``` or ~~~
#
# Footnote	            Here's a sentence with a footnote. [^1]
# 
#                       [^1]: This is the footnote.
#
# Heading ID	        ### My Great Heading {#custom-id}
#
# Definition List	    term
#                       : definition
#
# Strikethrough	        ~~The world is flat.~~
#
# Underline             __Pay attention.__
#
# Task List	            - [x] Write the press release
#                       - [ ] Update the website
#                       - [ ] Contact the media
#
# Emoji                 That is so funny! :joy:
# (see also Copying and Pasting Emoji)
#
# Highlight	            I need to highlight these ==very important words==.
#
# Subscript	            H~2~O
# Superscript	        X^2^

# blocks: headings, blockquotes, lists, code blocks, fenced code blocks, separate links, footnotes, definition list
# all blocks may start at offset+0, lists may also start at offset+2; headings and separate links are at most two lines long

from abc import ABCMeta, abstractmethod
from aenum import Enum, Flag, IntFlag, auto, export
from scription import Var
import re

__all__ = [
        'FormatError', 'BadFormat', 'AmbiguousFormat', 'IndentError',
        'Node', 'Heading', 'Paragraph', 'List', 'ListItem', 'CodeBlock', 'BlockQuote', 'Rule',
        'Link', 'Image', 'FootNote', 'ID', 'Definition', 'Text',
        'document', 'to_html',
        ]


HEADING = PARAGRAPH = TEXT = QUOTE = O_LIST = U_LIST = LISTITEM = CODEBLOCK = RULE = IMAGE = FOOTNOTE = LINK = ID = DEFINITION = None
END = SAME = CHILD = CONCLUDE = ORDERED = UNORDERED = None
PLAIN = BOLD = ITALIC = STRIKE = UNDERLINE = HIGHLIGHT = SUB = SUPER = CODE = FOOT_NOTE = ALL_TEXT = None
TERMINATE = INCLUDE = RESET = WORD = NUMBER = WHITESPACE = PUNCTUATION = OTHER = None

class NodeType(ABCMeta):
    def __repr__(self):
        return "%s" % self.__name__


ABC = NodeType('ABC', (object, ), {})
module = globals()

class DocEnum(Enum):
    _init_ = 'value __doc__'
    def __repr__(self): return "<%s.%s>" % (self.__class__.__name__, self.name)

@export(module)
class NodeType(Flag):
    HEADING         = auto()
    PARAGRAPH       = auto()
    TEXT            = auto()
    QUOTE           = auto()
    O_LIST          = auto()
    U_LIST          = auto()
    LISTITEM        = auto()
    CODEBLOCK       = auto()
    RULE            = auto()
    IMAGE           = auto()
    FOOTNOTE        = auto()
    LINK            = auto()
    ID              = auto()
    DEFINITION      = auto()

@export(module)
class NodeStatus(DocEnum):
    """
    used by check() to determine effect of next line
    """
    END             = 'not part of the current node (typically a blank line)'
    SAME            = 'part of the current node' 
    CHILD           = 'begins a new child node'
    CONCLUDE        = 'last line of the current node (e.g. a fenced code block)'

@export(module)
class ListType(DocEnum):
    ORDERED         = 'ordered list'
    UNORDERED       = 'unordered list'

@export(module)
class CharType(DocEnum):
    WORD        = 'letters and underscore'
    NUMBER      = 'arabic digits'
    WHITESPACE   = 'space, new-line, etc'
    PUNCTUATION = 'comma, period, etc'
    OTHER       = 'none of the above'

@export(module)
class TextType(int, Flag):
    _order_ = 'PLAIN BOLD_ITALIC BOLD ITALIC STRIKE UNDERLINE HIGHLIGHT SUB SUPER CODE FOOT_NOTE ALL_TEXT'

    def __new__(cls, docstring, open=None, close=None):
        value = 2 ** (len(cls.__members__) + 1)
        member = int.__new__(cls, value)
        member._value_ = value
        if close and open is None:
            close = open
        member.open = open
        member.close = close
        member.__doc__ = docstring
        cls._value2member_map_[open] = member
        return member

    def _missing_(cls, value):
        # support lookup by marker
        return cls._value2member_map_.get(value)


    PLAIN           = 'normal'
    BOLD_ITALIC     = '***really super important!***', '***'
    BOLD            = '**bolded stuff**', '**'
    ITALIC          = '*italic words*', '*'
    STRIKE          = '~~strike-through text~~', '~~'
    UNDERLINE       = '__underlined info__', '__'
    HIGHLIGHT       = '==highilighted words==', '=='
    SUB             = 'subscripted: H~2~O', '~'
    SUPER           = 'superscripted: x^2^', '^'
    CODE            = '`if blah is None`', '`'
    FOOT_NOTE       = 'a statement [^1]', '[^', ']'
    ALL_TEXT        = -1

@export(module)
class BlankLineType(DocEnum):
    TERMINATE       = 'a blank line terminates the node (e.g. paragraph)'
    INCLUDE         = 'a blank line is included in the node (e.g. fenced code block)'
    RESET           = 'may or may not indicate end of node'


class FormatError(Exception):
    def __init__(self, msg):
        self.msg = msg

class BadFormat(FormatError):
    pass

class AmbiguousFormat(FormatError):
    pass

class IndentError(FormatError):
    pass

class Node(ABC):

    allowed_blocks = ()
    allowed_text = PLAIN
    start_line = None
    end_line = None
    blank_line = TERMINATE
    blank_line_required = True
    parent = None
    children = False
    terminate_after_children = True
    links = {}

    def __init__(self, stream, indent=0, parent=None):
        self.parent = parent
        self.current_indent = indent
        self.stream = stream
        self.items = []
        self.final = False
        self.start_line = stream.line_no

    def __repr__(self):
        return "<%s: %r>" % (self.__class__.__name__, self.items[:1])

    def parse(self):
        # print(0, self.__class__.__name__)
        items = self.items
        stream = self.stream
        indent = self.current_indent
        reset = False
        #
        while stream:
            # print(1, self)
            line = stream.current_line.rstrip()
            if not line:
                if self.blank_line is TERMINATE:
                    # print(2)
                    status = END
                elif self.blank_line is INCLUDE:
                    # print(2.1)
                    items.append(line)
                    stream.skip_line()
                    continue
                elif self.blank_line is RESET:
                    # print(2.2)
                    self.reset = True
                    # save the line number in case this is the end
                    self.end_line = stream.line_no
                    stream.skip_line()
                    continue
            else:
                # print(3)
                ws, line = line[:indent], line[indent:]
                if ws.strip():
                    # no longer in this node
                    # print(3.1)
                    status = END
                    if self.blank_line_required:
                        # maybe raise, maybe okay
                        self.premature_end('%s%s' % (ws, line))
                else:
                    status = self.check(line)
                    # print('   %s' % (status, ))
            if status is SAME and self.children and terminate_after_children:
                raise BadFormat('ambiguous format at line %d' % stream.line_no)
            if status in (CONCLUDE, END):
                # print(4)
                self.end_line = self.end_line or stream.line_no
                if status is END:
                    self.end_line -= 1
                elif status is CONCLUDE:
                    # line was added by check(), skip the line here
                    stream.skip_line()
                # print(6)
                self.finalize()
                self.final = True
                break
            elif status is SAME:
                # line was added by check(); reset reset and end_line and skip line
                # print(7)
                stream.skip_line()
                self.reset = False
                self.end_line = None
            elif status is CHILD:
                # print(8)
                self.children = True
                self.reset = False
                self.end_line = None
                for child in self.allowed_blocks:
                    # print(9)
                    match, offset, kwds = child.is_type(line)
                    if match:
                        # print('  %d %r' % (offset, kwds))
                        new_indent = indent + offset
                        # print(10)
                        child = child(stream=stream, indent=new_indent, parent=self, **kwds)
                        # print('  added %r' % child)
                        items.append(child)
                        child.parse()
                        # print('  parsed: %r' % child)
                        break
                else:
                    # print(11)
                    # no valid child type found
                    raise BadFormat('failed match at line %d' % stream.line_no)
            else:
                raise Exception('unknown status: %r' % (status, ))
        # print(12)

    def premature_end(self, line):
        # by default, that's an error
        raise IndentError('bad indent at line %d (missing blank line above?)' % self.stream.line_no)

    def check(self, line):
        """
        return END, SAME, CHILD, or CONCLUDE depending on nature of next line
        """
        raise NotImplementedError

    @classmethod
    def is_type(cls, line):
        """
        checks if next line(s) are this node's type

        returns True, additional indent, {any keywords for __init__}; or
                NO_MATCH

        must leave stream at same location
        """
        raise NotImplementedError

    def finalize(self):
        """
        any final processing for the node goes here
        """
        pass

    def get_child_node():
        pass

    def to_html(self):
        raise NotImplementedError


class Heading(Node):
    type = HEADING
    allowed_text = PLAIN

    def finalize(self):
        print('heading', self.items)

    def to_html(self):
        start = '<h%d>' % self.level
        end = '</h%d>' % self.level
        return '%s%s%s' % (start, '\n'.join(self.items), end)


class Paragraph(Node):
    type = PARAGRAPH
    allowed_text = ALL_TEXT

    def check(self, line=0):
        # print('p.cn: %r' % (line, ))
        stream = self.stream
        self.items.append(line)
        if match(HD, line):
            # print('  header')
            # blank following line?
            blank_line = stream.peek_line()
            if blank_line.strip():
                # woops
                raise AmbiguousFormat(
                        'ambiguous line %d: add a subsequent blank line for a header, or have the first '
                        'non-blank character be a backslash (\\)' % (stream.line_no+1, )
                        )
            return CONCLUDE
        return SAME

    @classmethod
    def is_type(cls, line):
        if not line.strip() or not line[:1].strip():
            return NO_MATCH
        for regex in UL, OL, BQ, CB, FCB, HR, HD:
            if match(regex, line):
                return NO_MATCH
        return True, 0, {}

    def finalize(self):
        if match(HD, self.items[-1]):
            self.items.pop()
            self.level = 2 if match().group()[0] == '=' else 3
            self.__class__ = Heading
            self.finalize()
        else:
            # handle sub-elements
            print('paragraph', self.items)
            self.items = format('\n'.join(self.items), allowed_styles=self.allowed_text)

    def to_html(self):
        start = '<p>'
        end = '</p>'
        return '%s%s%s' % (start, ''.join([i.to_html() for i in self.items]), end)

class ListItem(Node):
    type = LISTITEM
    allowed_text = ALL_TEXT
    regex = None
    marker = None
    number = None
    blank_line_required = False

    def __init__(self, marker=None, list_type=None, text=None, **kwds):
        super(ListItem, self).__init__(**kwds)
        self.marker = marker
        self.list_type = list_type
        self.text = text
        if list_type is U_LIST:
            self.regex = UL
        else:
            self.regex = OL

    def check(self, line):
        # could be:
        # - a first line                --> if self.items is empty, SAME; else END
        #   a continuation line         --> SAME
        #   - a new sublist             --> END
        #       too much indent         --> exception
        #too little indent              --> if parent is a list, END; else excepttion
        # print('  checking: %r' % line)
        if not self.items:
            # print('  saving previous work')
            self.items.append(self.text)
            self.text = None
            return SAME
        #
        if match(self.regex, line):
            # if we match, it's either a new list item, or a sub-list
            if self.list_type is U_LIST:
                indent, marker, text = match().groups()
                if indent:
                    # sub-list
                    return CHILD
                return END
            elif self.list_type is O_LIST:
                indent, number, marker, text = match().groups()
                if indent:
                    # sub-list
                    return CHILD
                return END
            else:
                raise Exception('logic error: unknown list type at line %d' % self.stream.line_no)
        #
        c_indent = len(self.marker) + 1
        indent, text = match(CL, line).groups()
        # print('current_indent: %r  c_indent: %r  indent: %r  text: %r' % (self.current_indent, c_indent, indent, text))
        if not indent or len(indent) != c_indent:
            return END
        self.items.append(text)
        return SAME

    @classmethod
    def is_type(cls, line):
        if match(UL, line):
            indent, marker, text = match().groups()
            indent = indent and len(indent) or 0
            return True, indent, {'marker': marker, 'list_type': U_LIST, 'text': text}
        elif match(OL, line):
            indent, number, marker, text = match().groups()
            indent = indent and len(indent) or 0
            return True, indent, {'marker': '%s%s'%(number,marker), 'list_type': O_LIST, 'text': text}
        return NO_MATCH

    def finalize(self):
        print('listitem', self.items)
        self.items = format(self.items, allowed_styles=self.allowed_text)

    def to_html(self, indent=0):
        spacing = ' ' * indent
        start = '%s<li>' % spacing
        end =  '%s</li>' % spacing
        result = []
        list_item = []
        for i in self.items:
            if not isinstance(i, List):
                list_item.append(spacing+i.to_html())
            else:
                result.append('\n%s%s' % (spacing, i.to_html(indent+4)))
        result.insert(0, start + ''.join(list_item) + end)
        return ''.join(result)


class List(Node):
    type = O_LIST | U_LIST
    allowed_blocks = ListItem,
    blank_line = RESET
    terminate_after_children = False

    def __init__(self, marker, list_type, **kwds):
        super(List, self).__init__(**kwds)
        self.marker = marker
        self.list_type = list_type
        if list_type is U_LIST:
            self.regex = UL
        else:
            self.regex = OL

    def check(self, line):
        if not match(self.regex, line):
            return END
        if self.list_type is U_LIST:
            indent, marker, text = match().groups()
        elif self.list_type is O_LIST:
            indent, number, marker, text = match().groups()
        indent = indent and len(indent) or 0
        if indent == 2:
            raise Exception('huh')
        if marker == self.marker:
            return CHILD
        if self.reset:
            # we hit a blank line first, end this list and start a new one
            return END
        else:
            # different lists must be separated by a blank line
            raise BadFormat('attempt to change list marker inside a list at line %d' % self.stream.line_no)

    @classmethod
    def is_type(cls, line):
        if match(UL, line):
            indent, marker, text = match().groups()
            indent = indent and len(indent) or 0
            return True, indent, {'marker': marker, 'list_type': U_LIST}
        elif match(OL, line):
            indent, marker, text = match().groups()
            indent = indent and len(indent) or 0
            return True, indent, {'marker': marker, 'list_type': O_LIST}
        return NO_MATCH

    def premature_end(self, line):
        if isinstance(self.parent, ListItem):
            # if ending non-blank line is a part of an outer list, we're okay
            pass
        else:
            super(List, self).premature_end(line)

    def to_html(self, indent=0):
        spacing = ' ' * indent
        if self.regex == UL:
            start = spacing + '<ul>'
            end = spacing + '</ul>'
        else:
            start = spacing + '<ol>'
            end = spacing + '</ol>'
        result = [start]
        for item in self.items:
            result.append(spacing + item.to_html())
        result.append(end)
        return '\n'.join(result)

ListItem.allowed_blocks = List,


class CodeBlock(Node):
    type = CODEBLOCK
    allowed_text = PLAIN

    def __init__(self, block_type, language, **kwds):
        super(CodeBlock, self).__init__(**kwds)
        self.block_type = block_type
        self.language = language

    def check(self, line):
        # print('cb.0 %r' % line)
        if self.block_type == 'indented':
            # print('cb.1')
            self.items.append(line)
            return SAME
        else:
            if not self.items:
                # print('cb.2')
                self.items.append(line)
                return SAME
            # print('cb.3')
            self.items.append(line)
            if line.rstrip() == self.block_type:
                # print('cb.4')
                return CONCLUDE
            # print('cb.5')
            return SAME

    @classmethod
    def is_type(cls, line):
        if match(FCB, line):
            block_type, language = match().groups()
            return True, 0, {'block_type': block_type, 'language': language}
        if match(CB, line):
            return True, 4, {'block_type': 'indented', 'language': None}
        return NO_MATCH

    def finalize(self):
        if self.block_type != 'indented':
            if self.items[-1].rstrip() != self.block_type:
                raise BadFormat('missing code block fence %r at line %d' % (self.block_type, self.end_line))
            self.items.pop()
            self.items.pop(0)
        print('codeblock', self.items)

    def to_html(self):
        result = ['<pre><code>']
        result.extend(self.items)
        result.append('</code></pre>')
        print('************', result, '************')
        return '\n'.join(result)

class Rule(Node):
    type = RULE
    allowed_text = None

    def check(self, line):
        blank_line = self.stream.peek_line()
        if blank_line.strip():
            # woops
            raise AmbiguousFormat(
                    'ambiguous line %d: Header? Rule?' % (self.stream.line_no, )
                    )
        self.items.append(line)
        return CONCLUDE

    @classmethod
    def is_type(cls, line):
        # print('r.0: %r' % line)
        if len(line) >= 3 and set(line).pop() in '-*':
            return True, 0, {}
        return NO_MATCH

    def to_html(self):
        return '<hr>'


class Text(Node):
    type = TEXT
    allowed_text = ALL_TEXT

    def __init__(self, text=None, single='!', style=PLAIN, parent=None): #, allowed=PLAIN, parent=None):
        self.items = []
        self.text = text
        self.char = single
        self.style = style
        self.parent = parent

    def __repr__(self):
        if self.text is None:
            return self.char
        elif self.text:
            return self.text
        return ("Text(style=%s,\n     items=[%s\n           ])"
                % (self.style, 
                    '\n           '.join(repr(i) for i in self.items)
                    ))

    def to_html(self):
        if self.text is not None:
            start = ''
            end = ''
            for mark, open, close in (
                    (BOLD_ITALIC, '<b><i>', '</i></b>'),
                    (BOLD, '<b>', '</b>'),
                    (ITALIC, '<i>', '</i>'),
                    (STRIKE, '<del>', '</del>'),
                    (UNDERLINE, '<u>', '</u>'),
                    (HIGHLIGHT, '<mark>', '</mark>'),
                    (SUB, '<sub>', '</sub>'),
                    (SUPER, '<sup>', '</sup>'),
                    (CODE, '<code>', '</code>'),
                    (FOOT_NOTE, '<sup>', '</sup>'),
                ):
                if mark in self.style:
                    start = start + open
                    end = close + end
            return '%s%s%s' % (start, self.text, end)
        else:
            result = []
            for txt in self.items:
                result.append(txt.to_html())
            return ''.join(result)



class FootNote(Text):
    type = FOOTNOTE
    allowed_text = PLAIN

    def __init__(self, marker, **kwds):
        super(FootNote, self).__init__(**kwds)
        self.marker = marker


class Link(Text):
    type = LINK
    allowed_text = PLAIN

    def __init__(self, text, marker=None, url=None, **kwds):
        super(Link, self).__init__(**kwds)
        self.items = text.split('\n')
        self.marker = marker
        self.url = url


class BlockQuote(Node):
    type = QUOTE
    allowed_blocks = ()
    allowed_text = ALL_TEXT

    def render(self):
        output.write('<blockquote>\n')
        super(BlockQuote, self).render()
        output.write('</blockquote>\n')


class Image(Node):
    type = IMAGE
    allowed_text = None

class ID(Node):
    type = ID
    allowed_text = None

class Definition(Node):
    type = DEFINITION
    allowed_text = ALL_TEXT


class PPLCStream(object):
    """
    Peekable, Pushable, Line & Character Stream
    """

    # line_no starts at zero and represents the line number of the line that is accessible by
    # current_line and would be returned by get_line()
    # calling get_line() increments line_no, while calling push_line() decrements it
    line_no = 0

    # current_line is the line pointed to by line_no, and the line that *_char functions deal with
    @property
    def current_line(self):
        return ''.join(self.chars)

    def __init__(self, text):
        self.data = text.split('\n')
        self.data.reverse()
        self.chars = []
        self.line_no = 0
        if self.data:
            self.chars = list(self.data.pop()) + ['\n']

    def __bool__(self):
        return bool(self.current_line) 
    __nonzero__ = __bool__

    def get_char(self):
        ch = self.chars.pop(0)
        if not self.chars:
            self.line_no += 1
            if self.data:
                self.chars = list(self.data.pop()) + ['\n']
        return ch

    def get_line(self):
        if not self.chars:
            raise EOFError
        line = ''.join(self.chars)
        self.chars = []
        self.line_no += 1
        if self.data:
            self.chars = list(self.data.pop()) + ['\n']
        return line

    def peek_line(self):
        "return line after current line, or an empty string"
        if self.data:
            return self.data[-1] + '\n'
        return ''

    def peek_char(self, skip=1, ignore=''):
        "return next char not in ignore after skipping skip number of chars"
        for ch in self.current_line:
            if skip > 0:
                skip -= 1
                continue
            if ch not in ignore:
                return ch
        for i in reversed(range(len(self.data))):
            for ch in (self.data[i]+'\n'):
                if skip > 0:
                    skip -= 1
                    continue
                if ch not in ignore:
                    return ch
        else:
            return ''

    def push_char(self, ch):
        if ch is None:
            return
        if ch == '\n':
            if self.chars:
                # convert existing chars to line, dropping newline char
                char_line = ''.join(self.chars[:-1])
                self.chars = []
                self.data.append(char_line)
                if self.line_no > 0:
                    # don't decrement past begining of file
                    self.line_no -= 1
            self.chars = [ch]
        else:
            self.chars.insert(0, ch)

    def push_line(self, line):
        if line is None:
            return
        char_line = ''.join(self.chars[:-1])
        self.data.append(char_line)
        if not line[-1:] == '\n':
            line += '\n'
        self.chars = list(line)
        if self.line_no > 0:
            # don't decrement past begining of file
            self.line_no -= 1

    def skip_blank_lines(self):
        while self:
            line = self.get_line()
            if line is None:
                break
            if line.strip():
                self.push_line(line)
                return True
        return False

    def skip_line(self, count=1):
        for _ in range(count):
            self.get_line()

def format(texts, allowed_styles):
    def f(open, close=None, start=0, end=None, ws_needed=True):
        print("      f(open=%r, close=%r, start=%r, end=%r, ws_needed=%r" % (open, close, start, end, ws_needed))
        if end is None:
            end = len(chars)
        target = close or open
        match_len = len(target)
        open_count = 1
        close_count = 0
        i = start
        while i < end:
            if chars[i].char == '\\':
                i += 2
                continue
            possible = ''.join(c.char for c in chars[i:i+match_len])
            print("        %r   %r   %r" % (possible, open, target))
            if possible == open and open != target:
                print(50)
                open_count += 1
                i += match_len
                continue
            elif possible == target:
                if target == open:
                    print(51)
                    return i
                else:
                    print(52)
                    close_count += 1
                    if close_count == open_count:
                        print(53)
                        return i
                    i += 1
                    continue
            else:
                i += 1
        else:
            return -1
    def s(start=None, ws=False, forward=True):
        print('start is %r' % start)
        print('forward is %r' % forward)
        if start is None:
            start = pos
        if forward:
            for ch in chars[start:]:
                print('         looking at %r' % ch.char)
                if ch.char in '*~_=^.,?!\'"':
                    continue
                if ws and ch.char in ' \t\n':
                    print('            returning True')
                    return True
                if not ws and ch.char not in ' \t\n':
                    print('            returning True')
                    return True
                print('            returning False')
                return False
            print('            returning %s' % ws)
            return ws
        else:
            if start == 0:
                return ws
            print('chars:', [c.char for c in chars])
            print('target chars:', chars[start-1::-1])
            for ch in chars[start-1::-1]:
                print('         looking at %r' % ch.char)
                if ch.char in '*~_=^.,?!\'"':
                    continue
                if ws and ch.char in ' \t\n':
                    print('            returning True')
                    return True
                if not ws and ch.char not in ' \t\n':
                    print('            returning True')
                    return True
                print('            returning False')
                return False
            print('            returning %s' % ws)
            return ws
    ws = lambda start, forward=True: s(start, ws=True, forward=forward)
    non_ws = lambda start, forward=True: s(start, ws=False, forward=forward)
    find = Var(f)
    peek_char = Var(lambda index, len=1: ''.join(c.char for c in chars[index:index+len]))

    if isinstance(texts, str):
        texts = [texts]
    result = []
    print(0, texts)
    for text in texts:
        print(1)
        if isinstance(text, Node):
            print(2)
            # already processed
            result.append(text)
            continue
        if not isinstance(text, list):
            print(3)
            chars = [Text(single=c) for c in text]
        else:
            print(4)
            chars = text
        # look for subgroups: parentheticals, editorial comments, links, etc
        # link types: internal, wiki, external, footnote
        pos = 0
        print(5)
        while pos < len(chars):
            print(6)
            start = pos
            ch = chars[pos]
            if ch.char == '\\':
                print(7)
                pos += 2
                continue
            if ch.char == "`":
                print(8)
                # code
                end = find("`", "`", start+1)
                if end == -1:
                    # oops
                    raise BadFormat(
                            'failed to find matching "`" starting near %r'
                            % (chars[pos-10:pos+10], ))
                print('replacing %r ' % ''.join(c.char for c in chars[start:end+1]), end=' ')
                chars[start:end+1] = [Text(
                        ''.join([c.char for c in chars[start+1:end]]),
                        style=CODE,
                        )]
                print('with %r' % chars[start])
                pos += 3
                continue
            if ch.char == '(':
                print(9)
                # parens
                end = find('(', ')', start+1)
                if end == -1:
                    # oops
                    raise BadFormat(
                            "failed to find matching `)` starting near %r"
                            % (chars[pos-10:pos+10], ))
                # chars[start+1:end] = [Text(''.join(format(chars[start+1:end], allowed_styles)))]
                chars[start+1:end] = format([chars[start+1:end]], allowed_styles)
                pos += 3
                continue
            if ch.char == '[':
                print(10)
                # link
                if chars[pos+1].char == '[':
                    print(11)
                    # possible editoral comment
                    end = find('[[', ']]', start=pos+2)
                    if end == -1:
                        # oops
                        raise BadFormat(
                                "failed to find matching `]]` starting near %r"
                                % (chars[pos-10:pos+10], ))
                    # chars[start+1:end+1] = [Text(''.join(format(chars[start+1:end+1], allowed_styles)))]
                    chars[start+1:end+1] = format([chars[start+1:end+1]], allowed_styles)
                    pos += 3
                    continue
                # look for closing bracket and process link
                end = find('[', ']', start+1)
                if end == -1:
                    print(12)
                    # oops
                    raise BadFormat(
                            "failed to find matching `]` starting near %r"
                            % (chars[pos-10:pos+10], ))
                # what kind of link do we have?
                if chars[start+1].char == '^':
                    print(13)
                    # a foot note
                    marker = ''.join([c.char for c in chars[start+2:end]])
                    fn = FootNote(marker)
                    chars[start:end+1] = fn
                    pos = end + 1
                    continue
                elif end+1 == len(chars) or peek_char(end+1) not in '[(':
                    print(14)
                    # simple wiki page link
                    text = ''.join([c.char for c in chars[start+1:end]])
                    link = Link(text=text, url=text)
                    chars[start:end+1] = link
                    pos = end + 1
                    continue
                else:
                    print(15)
                    text = ''.join([c.char for c in chars[start+1:end]])
                    second = end + 2
                    if peek_char(end+1) == '[':
                        # url is listed separately, save the marker
                        end = find('[', ']', start=second)
                        if end == -1:
                            # oops
                            raise BadFormat(
                                    "failed to find matching `]` starting near %r"
                                    % (chars[pos-10:pos+10], ))
                        marker = ''.join([c.char for c in chars[second:end]])
                        link = Link(text=text, marker=marker)
                        chars[start:end+1] = link
                        pos += 1
                        continue
                    else:
                        print(16)
                        # url is between ( and )
                        end = find('(', ')', start=second)
                        if end == -1:
                            # oops
                            raise BadFormat(
                                    "failed to find matching `)` starting near %r"
                                    % (chars[pos-10:pos+10], ))
                        url = ''.join([c.char for c in chars[second:end]])
                        link = Link(text=text, url=url)
                        chars[start:end+1] = link
                        pos += 1
                        continue
            # stars, tildes, underscores, equals, carets
            if ch.char not in "*~_=^":
                print(17, ch.char)
                pos += 1
                continue
            print(18, ch.char)
            single = ch.char
            double = peek_char(pos, 2)
            triple = peek_char(pos, 3)
            print('%r %r %r' % (single, double, triple))
            if triple == '***':
                # bold italic
                marker = '***'
                ws_needed = True
            elif double == '**':
                # bold
                marker = '**'
                ws_needed = True
            elif single == '*':
                # italic
                marker = '*'
                ws_needed = True
            elif double == '__':
                # underline
                marker = '__'
                ws_needed = True
            elif double == '==':
                # highlight
                marker = '=='
                ws_needed = True
            elif double == '~~':
                # strike-through
                marker = '~~'
                ws_needed = True
            elif single == '~':
                # subscript
                marker = '~'
                ws_needed = False
            elif single == '^':
                # superscript
                marker = '^'
                ws_needed = False
            print('marker: %r' % marker)
            # to be the start of formatting, the previous (non-mark) character must be white space
            if ws_needed and not ws(pos, forward=False):
                print(19)
                pos += len(marker)
                continue
            # even if preceding white-space is not needed, a succeeding non-whitespace is
            if not non_ws(pos+len(marker)):
                print(20)
                pos += len(marker)
                continue
            # at this point, we have a valid starting marker, but only if we can find a valid ending marker as well
            end = find(marker, marker, pos+len(marker))
            print('end is', end, 'with', chars[end:end+5])
            if end == -1:
                print(21)
                # found nothing
                pos += len(marker)
                continue
            # found something -- does it meet the other criteria?
            print(repr([c.char for c in chars[end:end+5]]))
            if ws_needed and not ws(end+len(marker)):
                print(22)
                # failed the white space test
                pos += len(marker)
                continue
            # again, even if succedding white-space is not needed, a preceding non-whitespace is
            if not non_ws(end, forward=False):
                print(23)
                pos += len(marker)
                continue
            # we have matching markers!
            print('using style', TextType(marker))
            txt = Text(style=TextType(marker))
            items = format([chars[start+len(marker):end]], allowed_styles)
            if len(items) == 1:
                txt.text = items[0].text
            else:
                txt.items = items
            chars[start:end+len(marker)] = [txt]
            pos += 1
            continue
        # made it through the string!
        # TODO: condense styles if possible; for now, just return it
        print('=' * 25)
        print(result)
        print('-' * 25)
        print(text)
        print('-' * 25)

        string = []
        for ch in chars:
            if ch.text is not None:
                if string:
                    print(30, string)
                    result.append(Text(''.join(string)))
                    string = []
                result.append(ch)
            else:
                string.append(ch.char)
                print(31, string)
        if string:
            print(32, string)
            result.append(Text(''.join(string)))
        print(result)
        print('=' * 25)
    print('leaving format with', result)
    return result


def document(text):
    # blocks = Heading, Quote, List, CodeBlock, Rule, Image, Definition
    blocks = List, CodeBlock, Rule, Paragraph
    stream = PPLCStream(text)
    nodes = []
    # print('d.0')
    while stream.skip_blank_lines():
        # print('d.1')
        for nt in blocks:
            # print('d.2')
            line = stream.current_line.rstrip()
            match, indent, kwds = nt.is_type(line)
            # print('checking %r' % line)
            # print('  with %r, %r, and %r' % (match, indent, kwds))
            if match:
                # print('d.3')
                if nodes and nt is List:
                    if indent != 0 and isinstance(nodes[-1], CodeBlock) and nodes[-1].block_type == 'indented':
                        raise BadFormat('lists that follow indented code blocks cannot be indented (line %d)' % stream.line_no)
                elif nodes and nt is CodeBlock:
                    if indent != 0 and isinstance(nodes[-1], List):
                        raise BadFormat('indented code blocks cannot follow lists (line %d)' % stream.line_no)
                node = nt(stream=stream, indent=indent, parent=None, **kwds)
                break
        else:
            # print('d.4')
            raise Exception('no match found at line %d' % stream.line_no)
        # print('d.5')
        nodes.append(node)
        node.parse()
    # print('d.6')
    if isinstance(nodes[0], Heading) and nodes[0].level == 2:
        nodes[0].level = 1
    return nodes

def to_html(nodes):
    result = []
    for node in nodes:
        result.append(node.to_html())
    return '\n\n'.join(result) + '\n'



match = Var(re.match)

UL = r'(  )?(-|\+|\*) (.*)'
OL = r'(  )?(\d+)(\.|\)) (.*)'
CL = r'( *)?(.*)'
BQ = r'> (.*)'
CB = r'    (.*)'
FCB = r'(```|~~~) ?(.*)'
HR = r'(---+|\*\*\*+)'
HD = r'(===+|---+)'
ID_LINK = r'\b\[((?!^).*?)\]\[(.*?)\]\b'
EXT_LINK = r'\b\[((?!^).*?)\]\((.*?)\)\b' 
WIKI_LINK = r'\b\[((?!^).*?)\]\b' 
FOOT_NOTE_LINK = r'\[^(.*?)\]' 

NO_MATCH = False, 0, {}
WHITE_SPACE = ' \t\n'
MARKS = "*~_^`[]"
