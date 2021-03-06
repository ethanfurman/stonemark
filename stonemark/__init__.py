"""
a strict version of commonmark

currently supported syntax:

    Element                 StoneMark Syntax

                            ==========
    Heading                 H1 Heading    H2 Heading   H3 Heading
                            ==========    ==========   ----------

    Bold                    **bold text**

    Italic                  *italicized text*

    Bold & Italic           ***bold, italicized text***

    Ordered List            1. First item
                            2. Second item
                            3. Third item

    Unordered List          - First item
                            - Second item
                            - Third item

    Blockquote              > three-score and seven years ago
                            > our forefathers ...

    Code                    `code`

    Horizontal Rule         --- or ***

    Link         (in-line)  [title](https://www.example.com)

                (separate)  [title]  or [title][id]
                            ...
                            [title | id]: <https://www.example.com>

    Image                   ![alt text](image.jpg)


    Fenced Code Block       ``` or ~~~
                            {
                              "firstName": "John",
                              "lastName": "Smith",
                              "age": 25
                            }
                            ``` or ~~~

    Footnote                Here's a sentence with a footnote. [^1]
    
                            [^1]: This is the footnote.

    Strikethrough           ~~The world is flat.~~

    Underline               __Pay attention.__

    Highlight               I need to highlight these ==very important words==.

    Subscript               H~2~O
    Superscript             X^2^
"""

from __future__ import print_function

# syntax still to do
# 
# Table                 | Syntax | Description |
#                       | ----------- | ----------- |
#                       | Header | Title |
#                       | Paragraph | Text |
#
# Heading ID            ### My Great Heading {#custom-id}
#
# Definition List       term
#                       : definition
#
# Task List             - [x] Write the press release
#                       - [ ] Update the website
#                       - [ ] Contact the media
#
# Emoji                 That is so funny! :joy:

# imports & globals
from abc import ABCMeta, abstractmethod
from aenum import Enum, Flag, IntFlag, auto, export
from scription import *
import re


__all__ = [
        'FormatError', 'BadFormat', 'AmbiguousFormat', 'IndentError',
        'Node', 'Heading', 'Paragraph', 'List', 'ListItem', 'CodeBlock', 'BlockQuote', 'Rule',
        'Link', 'Image', 'IDLink', 'ID', 'Definition', 'Text',
        'Document',
        ]

version = 0, 1, 9

HEADING = PARAGRAPH = TEXT = QUOTE = O_LIST = U_LIST = LISTITEM = CODEBLOCK = RULE = IMAGE = FOOTNOTE = LINK = ID = DEFINITION = None
END = SAME = CHILD = CONCLUDE = ORDERED = UNORDERED = None
PLAIN = BOLD = ITALIC = STRIKE = UNDERLINE = HIGHLIGHT = SUB = SUPER = CODE = FOOT_NOTE = ALL_TEXT = None
TERMINATE = INCLUDE = RESET = WORD = NUMBER = WHITESPACE = PUNCTUATION = OTHER = None

# classes

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
    _order_ = 'PLAIN ITALIC BOLD BOLD_ITALIC STRIKE UNDERLINE HIGHLIGHT SUB SUPER CODE FOOT_NOTE ALL_TEXT'

    def __new__(cls, value, docstring, open, close, whitespace, start, end):
        if value == -1:
            value = 2 ** (len(cls)-1) -1
        member = int.__new__(cls, value)
        member._value_ = value
        if close and open is None:
            close = open
        member.open = open
        member.close = close
        member.__doc__ = docstring
        member.start = start
        member.end = end
        cls._value2member_map_[open] = member
        return member

    @classmethod
    def _create_pseudo_member_values_(cls, members, *values):
        start = ''
        end = ''
        for m in members:
            start = start + m.start
            end = m.end + end
        return values + ('', '', '', False, start, end)

    @classmethod
    def _missing_(cls, value):
        # support lookup by marker
        if isinstance(value, basestring):
            return cls._value2member_map_.get(value)
        else:
            return super(TextType, cls)._missing_(value)


    PLAIN           = 0, 'normal', '', '', False, '', ''
    ITALIC          = '*italic words*', '*', '*', True, '<i>', '</i>'
    BOLD            = '**bolded stuff**', '**', '**', True, '<b>', '</b>'
    BOLD_ITALIC     = 3, '***really super important!***', '***', '***', True, '<b><i>', '</i></b>'
    STRIKE          = '~~strike-through text~~', '~~', '~~', True, '<del>', '</del>'
    UNDERLINE       = '__underlined info__', '__', '__', True, '<u>', '</u>'
    HIGHLIGHT       = '==highilighted words==', '==', '==', True, '<mark>', '</mark>'
    SUB             = 'subscripted: H~2~O', '~', '~', False, '<sub>', '</sub>'
    SUPER           = 'superscripted: x^2^', '^', '^', False, '<sup>', '</sup>'
    CODE            = '`if blah is None`', '`', '`', False, '<code>', '</code>'
    FOOT_NOTE       = 'a statement [^1]', '[^', ']', True, '<sup>', '</sup>'
    ALL_TEXT        = -1, 'no restrictions', '', '', False, '', ''

@export(module)
class BlankLineType(DocEnum):
    TERMINATE       = 'a blank line terminates the node (e.g. paragraph)'
    INCLUDE         = 'a blank line is included in the node (e.g. fenced code block)'
    RESET           = 'may or may not indicate end of node'


class FormatError(Exception):
    pass

class BadFormat(FormatError):
    pass

class AmbiguousFormat(FormatError):
    pass

class IndentError(FormatError):
    pass

class MissingLink(FormatError):
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
    sequence = None
    links = {}

    def __init__(self, stream, indent=0, sequence=None, parent=None):
        self.node_id = next(UID)
        if parent is None:
            raise TypeError('parent cannot be None')
        self.parent = parent
        self.links = parent.links
        self.indent = indent
        self.stream = stream
        self.items = []
        self.final = False
        self.reset = None
        self.sequence = sequence
        if stream is not None:
            self.start_line = stream.line_no
        else:
            self.start_line = None
        while not isinstance(parent, Document):
            assert self.links is parent.links
            parent = parent.parent

    def __repr__(self):
        return "<%s: %r>" % (self.__class__.__name__, self.items)

    def parse(self):
        items = self.items
        stream = self.stream
        self.reset = False
        #
        i = 0
        while stream:
            line = stream.current_line.rstrip()
            if not line:
                if self.blank_line is TERMINATE:
                    status = END
                elif self.blank_line is INCLUDE:
                    items.append(line)
                    stream.skip_line()
                    continue
                elif self.blank_line is RESET:
                    self.reset = True
                    # save the line number in case this is the end
                    self.end_line = stream.line_no
                    stream.skip_line()
                    continue
            else:
                ws, line = line[:self.indent], line[self.indent:]
                if ws.strip():
                    # no longer in this node
                    status = END
                    if self.blank_line_required and not self.reset:
                        # maybe raise, maybe okay
                        self.premature_end('%s%s' % (ws, line))
                else:
                    status = self.check(line)
            if status is SAME and self.children and self.terminate_after_children:
                raise AmbiguousFormat('ambiguous format at line %d:\n%r' % (stream.line_no, line))
            if status in (CONCLUDE, END):
                self.reset = False
                self.end_line = self.end_line or stream.line_no
                if status is END:
                    self.end_line -= 1
                elif status is CONCLUDE:
                    # line was added by check(), skip the line here
                    stream.skip_line()
                keep = self.finalize()
                break
            elif status is SAME:
                # line was added by check(); reset reset and end_line and skip line
                stream.skip_line()
                self.reset = False
                self.end_line = None
            elif status is CHILD:
                self.children = True
                self.reset = False
                self.end_line = None
                for child in self.allowed_blocks:
                    match, offset, kwds = child.is_type(line)
                    if match:
                        new_indent = self.indent + offset
                        child = child(stream=stream, indent=new_indent, parent=self, **kwds)
                        items.append(child)
                        child.parse()
                        break
                else:
                    # no valid child type found
                    raise BadFormat('failed match at line %d\n%r' % (stream.line_no, line))
            else:
                raise Exception('unknown status: %r' % (status, ))
        else:
            keep = self.finalize()
            self.reset = False
        return keep

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
        self.final = True
        return True

    def get_child_node():
        pass

    def to_html(self):
        raise NotImplementedError


class Heading(Node):
    type = HEADING
    allowed_text = ALL_TEXT
    level = None
    blank_line_required = False

    def __init__(self, level=None, **kwds):
        super(Heading, self).__init__(**kwds)
        self.level = level
        self.text = level

    def check(self, line):
        # this is only called when handling a level 1 header
        if self.text == self.level:
            self.text = None
            return SAME
        chars = set(line)
        self.items.append(line)
        if len(chars) == 1 and len(line) >= 3 and chars.pop() == '=':
            return CONCLUDE
        return SAME


    def finalize(self):
        first, second, third = self.parent.header_sizes
        line = self.items[-1].strip()
        chars = set(line)
        ch = chars.pop()
        # chars should now be empty
        if chars or len(line) < 3 or ch not in '=-':
            raise BadFormat('Heading must consist of = or - and be at least three characters long')
        if self.level == first and ch != '=':
            raise BadFormat('Top level Headings must end with at least three = characters')
        self.items.pop()
        if self.level == 'first':
            self.level = first
        elif not self.level:
            if self.parent.first_header_is_title and self.sequence == 0:
                self.level = first
            else:
                self.level = second if ch == '=' else third
        self.items = format('\n'.join(self.items), allowed_styles=self.allowed_text, parent=self)
        return super(Heading, self).finalize()

    @classmethod
    def is_type(cls, line):
        chars = set(line.strip())
        if len(chars) == 1 and len(line) >= 3 and chars.pop() == '=':
            return True, 0, {'level': 'first'}
        return NO_MATCH

    def to_html(self):
        start = '<h%d>' % self.level
        end = '</h%d>' % self.level
        result = []
        for txt in self.items:
            result.append(txt.to_html())
        return '%s%s%s' % (start, '\n'.join(result), end)


class Paragraph(Node):
    type = PARAGRAPH
    allowed_text = ALL_TEXT

    def check(self, line=0):
        stream = self.stream
        for regex in UL, OL, BQ, CB, FCB:
            if match(regex, line):
                return END
        if match(HD, line):
            # blank following line?
            blank_line = stream.peek_line()
            if blank_line.strip():
                for regex in UL, OL, BQ, CB, FCB:
                    if match(regex, blank_line):
                        break
                else:
                    # woops
                    raise AmbiguousFormat(
                            'ambiguous line %d: add a subsequent blank line for a header, or have the first '
                            'non-blank character be a backslash (\\)' % (stream.line_no+1, )
                            )
            self.items.append(line)
            return CONCLUDE
        if self.items and isinstance(self.items[-1], str) and self.items[-1].endswith('-'):
            self.items[-1] = self.items[-1][:-1] + line
        else:
            self.items.append(line)
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
            self.__class__ = Heading
            return self.finalize()
        else:
            # handle sub-elements
            self.items = format('\n'.join(self.items), allowed_styles=self.allowed_text, parent=self)
        return super(Paragraph, self).finalize()

    def to_html(self):
        start = '<p>'
        end = '</p>'
        result = []
        for txt in self.items:
            result.append(txt.to_html())
        return '%s%s%s' % (start, ''.join(result), end)


class CodeBlock(Node):
    type = CODEBLOCK
    allowed_text = PLAIN
    blank_line_required = False

    def __init__(self, block_type, attrs, **kwds):
        super(CodeBlock, self).__init__(**kwds)
        self.block_type = block_type
        self.language = None
        self.attrs = None
        return

        attrs = attrs and attrs.strip()
        if not attrs:
            return
        elif attrs[::(len(attrs)-1)] != '{}':
            l_count = attrs.count('{')
            r_count = attrs.count('}')
            if l_count != r_count or l_count > 1 or r_count > 1:
                raise BadFormat('mismatch {} in fenced block attributes %r' % attrs)
            if attrs.startswith('.'):
                raise BadFormat('leading . not allowed in %r when only language is specified' % attrs)
            if ' ' in language:
                raise BadFormat('invalid language specifier %r (no spaces allowed)' % language)
            attrs = '{ .%s }' % attrs
        #
        errors = []
        attrs = attrs[1:-1].strip().split()
        if not attrs:
            return
        language = attrs[0]
        attrs = attrs[1:]
        if not language.startswith('.'):
            raise BadForman('missing leading . in language specifier %r' % language)
        self.language = language
        for a in attrs:
            if not a.startswith('.'):
                raise BadForman('missing leading . in attribute %r' % a)
        self.attrs = ''.join(attrs)

    def check(self, line):
        if self.block_type == 'indented':
            self.items.append(line)
            return SAME
        else:
            if not self.items:
                self.items.append(line)
                return SAME
            self.items.append(line)
            if line.rstrip() == self.block_type:
                return CONCLUDE
            return SAME

    @classmethod
    def is_type(cls, line):
        if match(FCB, line):
            indent, block_type, attrs = match().groups()
            indent = indent and len(indent) or 0
            return True, indent, {'block_type': block_type, 'attrs': attrs}
        if match(CB, line):
            return True, 4, {'block_type': 'indented', 'attrs': None}
        return NO_MATCH

    def finalize(self):
        if self.block_type != 'indented':
            if self.items[-1].rstrip() != self.block_type:
                raise BadFormat('missing code block fence %r at line %d' % (self.block_type, self.end_line))
            self.items.pop()
            self.items.pop(0)
        return super(CodeBlock, self).finalize()

    def to_html(self):
        code = '<code>'
        pre = '<pre>'
        if self.language:
            code = '<pre><code class="language-%s">' % self.language
        if self.attrs:
            pre = '<pre class="%s">' % self.attrs
        start = '%s%s' % (pre, code)
        end = '</code></pre>'
        return start + escape('\n'.join(self.items)) + end


class Image(Node):
    type = IMAGE
    allowed_text = ALL_TEXT

    def __init__(self, text, url, **kwds):
        super(Image, self).__init__(**kwds)
        self.items = format(text, allowed_styles=self.allowed_text, parent=self)
        self.url = url

    def check(self, line):
        return CONCLUDE

    @classmethod
    def is_type(cls, line):
        if match(IMAGE_LINK, line):
            alt_text, url = match().groups()
            return True, 0, {'text': alt_text, 'url': url}
        return NO_MATCH

    def to_html(self):
        alt_text = []
        for txt in self.items:
            alt_text.append(txt.to_html())
        alt_text = ''.join(alt_text)
        return '<img src="%s" alt="%s">' % (self.url, alt_text)


class List(Node):
    type = O_LIST | U_LIST
    allowed_blocks = ()             # ListItem added after definition
    blank_line = RESET
    terminate_after_children = False
    blank_line_required = False

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
            indent, number, marker, text = match().groups()
            indent = indent and len(indent) or 0
            return True, indent, {'marker': marker, 'list_type': O_LIST}
        return NO_MATCH

    def premature_end(self, line):
        pass

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

class ListItem(Node):
    type = LISTITEM
    allowed_blocks = CodeBlock, Image, List
    allowed_text = ALL_TEXT
    regex = None
    marker = None
    number = None
    blank_line_required = False
    blank_line = RESET
    terminate_after_children = False

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
        if not self.items:
            self.items.append(self.text)
            self.text = None
            return SAME
        c_indent = len(self.marker) + 1
        indent, text = match(CL, line).groups()
        if not indent or len(indent) < c_indent:
            return END
        text = line[c_indent:]  # preserve beginning whitespace of sub-items
        if self.reset:
            # get empty line back
            self.items.append('')
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
        # self.items = format(self.items, allowed_styles=self.allowed_text, parent=self)
        # remove paragraph status from item[0] if present
        # handle sub-elements
        final_items = []
        doc = []
        sub_doc = Document('\n'.join(self.items))
        final_items.extend(sub_doc.nodes)
        self.items = format(final_items, allowed_styles=self.allowed_text, parent=self)
        if self.items and isinstance(self.items[0], Paragraph):
            self.items[0:1] = self.items[0].items
        return super(ListItem, self).finalize()

        for item in self.items:
            if isinstance(item, unicode):
                # simple text, append it
                doc.append(item)
            else:
                # an embedded node, process any text lines
                if doc:
                    doc = Document('\n'.join(doc))
                    final_items.extend(doc.nodes)
                doc = []
                final_items.append(item)
        if doc:
            doc = Document('\n'.join(doc))
            final_items.extend(doc.nodes)
        self.items = format(final_items, allowed_styles=self.allowed_text, parent=self)
        if isinstance(self.items[0], Paragraph):
            self.items[0:1] = self.items[0].items
        return super(ListItem, self).finalize()

    def to_html(self, indent=0):
        spacing = ' ' * indent
        start = '%s<li>' % spacing
        end =  '%s</li>' % spacing
        result = []
        list_item = []
        last_style = None
        for i in self.items:
            if not isinstance(i, Text):
                last_style = None
            else:
                last_style = i.style
            if not isinstance(i, List):
                list_item.append(spacing+i.to_html())
            else:
                result.append('\n%s%s' % (spacing, i.to_html(indent+4)))
        result.insert(0, start + ''.join(list_item) + end)
        return ''.join(result)

List.allowed_blocks = ListItem,

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
        chars = set(line)
        if len(line) >= 3 and len(chars) == 1 and chars.pop() in '-*':
            return True, 0, {}
        return NO_MATCH

    def to_html(self):
        return '<hr>'


class Text(Node):
    type = TEXT
    allowed_text = ALL_TEXT

    def __init__(self, text=None, single='!', style=PLAIN, **kwds):
        if 'stream' not in kwds:
            kwds['stream'] = None
        self.text = text
        self.char = single
        self.style = style
        super(Text, self).__init__(**kwds)

    def __repr__(self):
        if self.text is None and not self.items:
            return self.char
        elif self.text:
            return "%s(%s: %s)" % (self.__class__.__name__, self.style.name, self.text)
        else:
            return ("%s(style=%s,\n     items=%r)"
                    % (self.__class__.__name__, self.style, self.items))

    def to_html(self):
        start = ''
        end = ''
        for mark, open, close in (
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
        if self.text is not None:
            body = escape(self.text)
        else:
            result = []
            for txt in self.items:
                try:
                    result.append(txt.to_html())
                except AttributeError:
                    print('v' * 50)
                    print(self)
                    print('^' * 50)
                    raise
            body = ''.join(result)
        return '%s%s%s' % (start, body, end)


class IDLink(Node):
    type = LINK
    allowed_blocks = CodeBlock, List, Image, Paragraph
    allowed_text = ALL_TEXT
    blank_line = RESET
    blank_line_required = False

    def __init__(self, marker, text, **kwds):
        super(IDLink, self).__init__(**kwds)
        if marker[0] == '^':
            self.type = 'footnote'
        else:
            #external link
            self.type = 'link'
        self.marker = marker
        self.text = text

    def check(self, line):
        if not self.items:
            self.indent += len(self.marker) + 4
            self.items.append(self.text)
            self.text = None
            return SAME
        if match(ID_LINK, line):
            return END
        self.items.append('\n')
        if self.reset:
            return CHILD
        self.items.append(line)
        return SAME

    def finalize(self):
        if self.type == 'footnote':
            self.items = format(self.items, allowed_styles=self.allowed_text, parent=self)
            for link in self.links[self.marker]:
                link.final = True
            keep = True
        else:
            for link in self.links[self.marker]:
                link.text %= ''.join(self.items)
                link.final = True
            keep = False
        return keep

    @classmethod
    def is_type(cls, line):
        if match(ID_LINK, line):
            marker, text = match().groups()
            return True, 0, {'marker': marker, 'text': text}
        return NO_MATCH

    def premature_end(self, line):
        if match(ID_LINK, line):
            # if ending non-blank line is another footnote, we're okay
            pass
        else:
            super(IDLink, self).premature_end(line)

    def to_html(self):
        s_marker = self.marker[1:]
        start = '<div id="footnote-%s"><table><tr><td style="vertical-align: top"><sup>%s</sup></td><td>' % (s_marker, s_marker)
        end = '</td></tr></table></div>'
        result = []
        for item in self.items:
            if self.type == 'footnote' and not isinstance(item, Text):
                result.append('\n')
            result.append(item.to_html())
        if result[-1][-1] == '\n':
            result[-1][-1] = ''
        return "%s%s%s" % (start, ''.join(result), end)


class Link(Text):
    # Wiki, external, and footnote
    type = LINK
    allowed_text = PLAIN

    def __init__(self, text=None, url=None, marker=None, **kwds):
        """
        text: stuff between the <a href...> and the </a>
        url: stuff in the href="..."
        marker: identifier for footnotes and separate external links
        """
        super(Link, self).__init__(**kwds)
        self.marker = marker
        self.url = url
        if marker is not None:
            s_marker = escape(marker[1:])
            if marker[0] == '^':
                self.type = 'footnote'
                self.text = '<sup><a href="#footnote-%s">[%s]</a></sup>' % (s_marker, s_marker)
                self.links.setdefault(marker, []).append(self)
            else:
                self.type = 'separate'
                self.text = '<a href="%%s">%s</a>' % (escape(text), )
                self.links.setdefault(marker, []).append(self)
        if url is not None:
            self.type = 'simple'
            self.text = '<a href="%s">%s</a>' % (escape(self.url), escape(text))
            self.final = True

    def to_html(self):
        if not self.final:
            raise MissingLink('link %r never found' % (self.marker, ))
        return self.text

class BlockQuote(Node):
    type = QUOTE
    # allowed_blocks = CodeBlock, Image, List, ListItem, Paragraph
    allowed_text = ALL_TEXT
    terminate_after_children = False
    blank_line_required = False

    def __init__(self, **kwds):
        super(BlockQuote,self).__init__(**kwds)
        self.level = 1
        if isinstance(self.parent, self.__class__):
            self.level += self.parent.level

    def check(self, line):
        if match(BQ, line):
            level = len(match.groups()[0])
            line = line[level:]
            if line and line[0] != ' ':
                raise BadFormat('a space is needed in %r' % line)
            line = line[1:]
            if level == self.level:
                self.items.append(line)
                return SAME
            elif level > self.level:
                return CHILD
            else: # level < self.level
                return END
        return END


    @classmethod
    def is_type(cls, line):
        if match(BQ, line):
            return True, 0, {}
        return NO_MATCH

    def finalize(self):
        # handle sub-elements
        final_items = []
        doc = []
        for item in self.items:
            if isinstance(item, unicode):
                # simple text, append it
                doc.append(item)
            else:
                # an embedded node, process any text lines
                if doc:
                    doc = Document('\n'.join(doc))
                    final_items.extend(doc.nodes)
                doc = []
                final_items.append(item)
        if doc:
            doc = Document('\n'.join(doc))
            final_items.extend(doc.nodes)
        self.items = format(final_items, allowed_styles=self.allowed_text, parent=self)
        return super(BlockQuote, self).finalize()

    def to_html(self):
        lead_space = ' ' * 12 * (self.level-1)
        mid_space = '\n' + ' ' * 12
        start = '<blockquote>'
        end = '\n</blockquote>'
        result = []
        result.append(start)
        for item in self.items:
            if isinstance(item, Node):
                result.append(mid_space + mid_space.join(item.to_html().split('\n')))
            else:
                result.append(mid_space + item)
        result.append(end)
        return ''.join(result)
BlockQuote.allowed_blocks = (BlockQuote, )

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

def format(texts, allowed_styles, parent):
    def f(open, close, start=0, ws_needed=True):
        end = len(chars)
        match_len = len(close or open)
        open_count = 1
        close_count = 0
        i = start
        while i < end:
            if chars[i].char == '\\':
                del chars[i]
                i += 1
                continue
            possible = ''.join(c.char for c in chars[i:i+match_len])
            if possible == close:
                # count must be the same
                # whitespace setting must match
                if not ws_needed:
                    if open == close:
                        # count doesn't matter
                        # whitespace doesn't matter
                        return i
                    close_count += 1
                    if open_count == close_count:
                        return i
                # check for needed whitespace
                if ws(i+1):
                    close_count += 1
                    if open_count == close_count:
                        return i
            # check for valid open tag
            if possible == open:
                if not ws_needed or ws(i, forward=False):
                    open_count += 1
                    i += match_len - 1
            i += 1
        else:
            return -1
    def s(start=None, ws=False, forward=True):
        if start is None:
            start = pos
        if forward:
            for ch in chars[start:]:
                if ch.char in '*~_=^.,?!\'"':
                    continue
                if ws and ch.char in ' \t\n':
                    return True
                if not ws and ch.char not in ' \t\n':
                    return True
                return False
            return ws
        else:
            if start == 0:
                return ws
            for ch in chars[start-1::-1]:
                if ch.char in '*~_=^.,?!\'"':
                    continue
                if ws and ch.char in ' \t\n':
                    return True
                if not ws and ch.char not in ' \t\n':
                    return True
                return False
            return ws
    ws = lambda start, forward=True: s(start, ws=True, forward=forward)
    non_ws = lambda start, forward=True: s(start, ws=False, forward=forward)
    find = Var(f)
    peek_char = Var(lambda index, len=1: ''.join(c.char for c in chars[index:index+len]))

    if isinstance(texts, basestring):
        texts = [texts]
    result = []
    for text in texts:
        if isinstance(text, Node):
            # already processed
            result.append(text)
            continue
        if not isinstance(text, list):
            chars = [Text(single=c, parent=parent) for c in text]
        else:
            chars = text
        # look for subgroups: parentheticals, editorial comments, links, etc
        # link types: internal, wiki, external, footnote
        pos = 0
        while pos < len(chars):
            start = pos
            ch = chars[pos]
            if ch.char == '\\':
                del chars[pos]
                pos += 1
                continue
            if ch.char == "`":
                # code
                end = find("`", "`", start+1, False)
                if end == -1:
                    # oops
                    raise BadFormat( 'failed to find matching "`" starting near %r between %r and %r' % (chars[pos-10:pos+10], parent.start_line, parent.end_line))
                chars[start:end+1] = [Text(
                        ''.join([c.char for c in chars[start+1:end]]),
                        style=CODE,
                        parent=parent,
                        )]
                pos += 1
                continue
            if ch.char == '(':
                # parens
                end = find('(', ')', start+1, False)
                if end == -1:
                    # oops
                    raise BadFormat(
                            "failed to find matching `)` starting near %r between %r and %r"
                            % (chars[pos-10:pos+10], parent.start_line, parent.end_line))
                chars[start+1:end] = format([chars[start+1:end]], allowed_styles, parent=parent)
                pos += 3
                continue
            if ch.char == '[':
                # link
                if ''.join(c.char for c in chars[pos:pos+2]) == '[[':
                    # possible editoral comment
                    end = find('[[', ']]', pos+2, False)
                    if end == -1:
                        # oops
                        raise BadFormat(
                                "failed to find matching `]]` starting near %r between %r and %r"
                                % (chars[pos-10:pos+10], parent.start_line, parent.end_line))
                    chars[start+1:end+1] = format([chars[start+2:end]], allowed_styles, parent=parent)
                    pos += 3
                    continue
                # look for closing bracket and process link
                end = find('[', ']', start+1, False)
                if end == -1:
                    # oops
                    raise BadFormat(
                            "failed to find matching `]` starting near %r between %r and %r"
                            % (chars[pos-10:pos+10], parent.start_line, parent.end_line))
                # what kind of link do we have?
                if chars[start+1].char == '^':
                    # a foot note
                    # remove previous spaces
                    while chars[start-1].char == ' ':
                        chars.pop(start-1)
                        start -= 1
                        end -=1
                    marker = ''.join([c.char for c in chars[start+1:end]])
                    fn = Link(marker=marker, parent=parent)
                    chars[start:end+1] = [fn]
                    pos += 1
                    continue
                elif end+1 == len(chars) or peek_char(end+1) not in '[(':
                    # simple wiki page link
                    text = ''.join([c.char for c in chars[start+1:end]])
                    link = Link(text=text, url=text, parent=parent)
                    chars[start:end+1] = [link]
                    pos += 1
                    continue
                else:
                    text = ''.join([c.char for c in chars[start+1:end]])
                    second = end + 2
                    if peek_char(end+1) == '[':
                        # url is listed separately, save the marker
                        end = find('[', ']', second)
                        if end == -1:
                            # oops
                            raise BadFormat(
                                    "failed to find matching `]` starting near %r between %r and %r"
                                    % (chars[pos-10:pos+10], parent.start_line, parent.end_line))
                        marker = ''.join([c.char for c in chars[second:end]])
                        link = Link(text=text, marker=marker, parent=parent)
                        chars[start:end+1] = [link]
                        pos += 1
                        continue
                    else:
                        # url is between ( and )
                        end = find('(', ')', second)
                        if end == -1:
                            # oops
                            raise BadFormat(
                                    "failed to find matching `)` starting near %r between %r and %r"
                                    % (chars[pos-10:pos+10], parent.start_line, parent.end_line))
                        url = ''.join([c.char for c in chars[second:end]])
                        link = Link(text=text, url=url, parent=parent)
                        chars[start:end+1] = [link]
                        pos += 1
                        continue
            # stars, tildes, underscores, equals, carets
            if ch.char not in "*~_=^":
                pos += 1
                continue
            single = ch.char
            double = peek_char(pos, 2)
            triple = peek_char(pos, 3)
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
            else:
                # no possible match, continue on
                pos += 1
                continue
            # to be the start of formatting, the previous (non-mark) character must be white space
            if ws_needed and not ws(pos, forward=False):
                pos += len(marker)
                continue
            # even if preceding white-space is not needed, a succeeding non-whitespace is
            if not non_ws(pos+len(marker)):
                pos += len(marker)
                continue
            # at this point, we have a valid starting marker, but only if we can find a valid ending marker as well
            end = find(marker, marker, pos+len(marker), ws_needed)
            if end == -1:
                # found nothing
                pos += len(marker)
                continue
            # found something -- does it meet the other criteria?
            if ws_needed and not ws(end+len(marker)):
                # failed the white space test
                pos += len(marker)
                continue
            # again, even if succedding white-space is not needed, a preceding non-whitespace is
            if not non_ws(end, forward=False):
                pos += len(marker)
                continue
            # we have matching markers!

            txt = Text(style=TextType(marker), parent=parent)
            mask = ~txt.style
            items = format([chars[start+len(marker):end]], allowed_styles, parent=parent)
            if len(items) == 1:
                # txt.style = items[0].style
                txt.text = items[0].text
            else:
                for item in items:
                    item.style &= mask
                txt.items = items

            chars[start:end+len(marker)] = [txt]
            pos += 1
            continue
        # made it through the string!
        # TODO: condense styles if possible; for now, just return it

        string = []
        for ch in chars:
            if ch.text is not None or ch.items:
                if string:
                    result.append(Text(''.join(string), parent=parent))
                    string = []
                result.append(ch)
            else:
                string.append(ch.char)
        if string:
            result.append(Text(''.join(string), parent=parent))
    return result


class Document(object):

    def __init__(self, text, first_header_is_title=False, header_sizes=(1, 2, 3)):
        self.links = {}
        self.first_header_is_title = first_header_is_title
        self.header_sizes = header_sizes
        #
        blocks = CodeBlock, Heading, List, Rule, IDLink, Image, Paragraph, BlockQuote
        stream = PPLCStream(text)
        nodes = []
        count = 0
        while stream.skip_blank_lines():
            for nt in blocks:
                line = stream.current_line.rstrip()
                match, indent, kwds = nt.is_type(line)
                if match:
                    if nodes and nt is List:
                        if indent != 0 and isinstance(nodes[-1], CodeBlock) and nodes[-1].block_type == 'indented':
                            raise BadFormat('lists that follow indented code blocks cannot be indented (line %d)' % stream.line_no)
                    node = nt(stream=stream, indent=indent, parent=self, sequence=count, **kwds)
                    count += 1
                    break
            else:
                raise FormatError('no match found at line %d\n%r' % (stream.line_no, line))
            keep = node.parse()
            if nodes and nt is CodeBlock and node.block_type == 'indented' and isinstance(nodes[-1], List):
                raise BadFormat('indented code blocks cannot follow lists (line %d)\n%r' % (node.start_line, line))
            if keep:
                nodes.append(node)
        self.nodes = nodes

    def to_html(self):
        result = []
        for node in self.nodes:
            result.append(node.to_html())
        return '\n\n'.join(result)


def escape(s, quote=True):
    """
    Replace special characters "&", "<" and ">" to HTML-safe sequences.
    If the optional flag quote is true (the default), the quotation mark
    characters, both double quote (") and single quote (') characters are also
    translated.
    """
    s = s.replace("&", "&amp;") # Must be done first!
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
        s = s.replace('\'', "&apos;")
    return s

def UID():
    i = 0
    while True:
        i += 1
        yield i
UID = UID()
match = Var(re.match)

UL = r'(  )?(-|\+|\*) (.*)'
OL = r'(  )?(\d+)(\.|\)) (.*)'
CL = r'( *)?(.*)'
BQ = r'(>+)'
CB = r'    (.*)'
FCB = r'( *)(```|~~~) ?(.*)'
HR = r'(---+|\*\*\*+)'
HD = r'(===+|---+)'
ID_LINK = r'^\[(\^?.*?)\]: (.*)'
EXT_LINK = r'\b\[((?!^).*?)\]\((.*?)\)\b' 
WIKI_LINK = r'\b\[((?!^).*?)\]\b' 
FOOT_NOTE_LINK = r'\[(\^.*?)\]:' 
IMAGE_LINK = r'^!\[([^]]*)]\((.*)\)$'

NO_MATCH = False, 0, {}
WHITE_SPACE = ' \t\n'
MARKS = "*~_^`[]"
