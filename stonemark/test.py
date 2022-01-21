'''
Tests for StoneMark
'''

from __future__ import unicode_literals

from . import PPLCStream
from . import *
from textwrap import dedent

def test_get_char():
    sample = u'line one\nline two'
    stream = PPLCStream(sample)
    result = []
    line_no = 0
    while stream:
        assert stream.line_no == line_no
        ch = stream.get_char()
        result.append(ch)
        if ch == '\n':
            line_no += 1
    assert ''.join(result) == sample+'\n'
    assert line_no == 2
    assert line_no == stream.line_no

def test_get_line():
    sample = u'line one\nline two'
    stream = PPLCStream(sample)
    result = []
    line_no = 0
    while stream:
        assert stream.line_no == line_no
        line = stream.get_line()
        result.append(line)
        line_no += 1
    assert ''.join(result) == sample+'\n'
    assert line_no == 2
    assert line_no == stream.line_no

def test_peek_line():
    sample = u'line one\nline two'
    stream = PPLCStream(sample)
    assert stream.current_line == 'line one\n'
    assert stream.peek_line() == 'line two\n'
    assert stream.get_line() == 'line one\n'
    assert stream.current_line == 'line two\n'
    assert stream.peek_line() == ''
    assert stream.get_line() == 'line two\n'
    assert stream.current_line == ''
    try:
        stream.get_line()
    except EOFError:
        pass

def test_push_char():
    sample = u'line one\nline two'
    stream = PPLCStream(sample)
    result = []
    stream.push_char('2')
    stream.push_char('4')
    line_no = 0
    while stream:
        assert stream.line_no == line_no
        line = stream.get_line()
        result.append(line)
        line_no += 1
    assert ''.join(result) == '42'+sample+'\n'
    assert line_no == 2
    assert line_no == stream.line_no

def test_push_line():
    sample = u'line one\nline two'
    stream = PPLCStream(sample)
    result = []
    stream.push_line('line zero')
    line_no = 0
    while stream:
        assert stream.line_no == line_no
        ch = stream.get_char()
        result.append(ch)
        if ch == '\n':
            line_no += 1
    assert ''.join(result) == 'line zero\n'+sample+'\n'
    assert line_no == 3
    assert line_no == stream.line_no



def test_simple_doc_1():
    test_doc = dedent("""\
    Document Title
    ==============

    In this paragraph we see that we have multiple lines of a single
    sentence.

    - plus a two-line
    - list for good measure
      + and a sublist
      + for really good measure

    Now a tiny paragraph.

        and a code block!

    ```
    and another code block!
    ```
    """)

    s = PPLCStream(test_doc)
    p = Paragraph(s, 0)
    doc = document(test_doc)
    assert shape(doc) == [Heading,  Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem, ]]], Paragraph, CodeBlock, CodeBlock]
    assert to_html(doc) == dedent("""\
            <h1>Document Title</h1>

            <p>In this paragraph we see that we have multiple lines of a single
            sentence.</p>

            <ul>
            <li>plus a two-line</li>
            <li>list for good measure</li>
                <ul>
                <li>and a sublist</li>
                <li>for really good measure</li>
                </ul>
            </ul>

            <p>Now a tiny paragraph.</p>

            <pre><code>
            and a code block!
            </code></pre>

            <pre><code>
            and another code block!
            </code></pre>
            """)

def test_simple_doc_2():
    test_doc = dedent("""\
    Document Title
    ==============

    In this paragraph we see that we have multiple lines of a single
    sentence.

    - plus a two-line
    - list for good measure
      + and a sublist
      + for really good measure
    - back to main list


    ```
    and another code block!
    ```
    """)

    s = PPLCStream(test_doc)
    p = Paragraph(s, 0)
    doc = document(test_doc)
    assert shape(doc) == [Heading, Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem]], ListItem], CodeBlock]
    assert to_html(doc) == dedent("""\
            <h1>Document Title</h1>

            <p>In this paragraph we see that we have multiple lines of a single
            sentence.</p>

            <ul>
            <li>plus a two-line</li>
            <li>list for good measure</li>
                <ul>
                <li>and a sublist</li>
                <li>for really good measure</li>
                </ul>
            <li>back to main list</li>
            </ul>

            <pre><code>
            and another code block!
            </code></pre>
            """)

def test_simple_doc_3():
    test_doc = dedent("""\
    Document Title
    ==============

    In this paragraph we see that we have multiple lines of a single
    sentence.

    - plus a two-line
    - list for good measure
      + and a sublist
      + for really good measure

    Now a tiny paragraph I mean header
    ----------------------------------

        and a code block!

    ```
    and another code block!
    ```
    """)

    s = PPLCStream(test_doc)
    p = Paragraph(s, 0)
    doc = document(test_doc)
    assert shape(doc) == [Heading, Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem]]], Heading, CodeBlock, CodeBlock]
    assert to_html(doc) == dedent("""\
            <h1>Document Title</h1>

            <p>In this paragraph we see that we have multiple lines of a single
            sentence.</p>

            <ul>
            <li>plus a two-line</li>
            <li>list for good measure</li>
                <ul>
                <li>and a sublist</li>
                <li>for really good measure</li>
                </ul>
            </ul>

            <h3>Now a tiny paragraph I mean header</h3>

            <pre><code>
            and a code block!
            </code></pre>

            <pre><code>
            and another code block!
            </code></pre>
            """)

def test_simple_doc_4():
    test_doc = dedent("""\
    Document Title
    ==============

    In this paragraph we see that we have multiple lines of a single
    sentence.

    - plus a two-line
    - list for good measure

    ---

    Now a tiny paragraph.

        and a code block!

    ```
    and another code block!
    ```
    """)

    s = PPLCStream(test_doc)
    p = Paragraph(s, 0)
    doc = document(test_doc)
    assert shape(doc) == [Heading, Paragraph, List, [ListItem, ListItem], Rule, Paragraph, CodeBlock, CodeBlock]
    assert to_html(doc) == dedent("""\
            <h1>Document Title</h1>

            <p>In this paragraph we see that we have multiple lines of a single
            sentence.</p>

            <ul>
            <li>plus a two-line</li>
            <li>list for good measure</li>
            </ul>

            <hr>

            <p>Now a tiny paragraph.</p>

            <pre><code>
            and a code block!
            </code></pre>

            <pre><code>
            and another code block!
            </code></pre>
            """)

def test_failure_1():
    test_doc = dedent("""\
    Document Title
    ==============

    In this paragraph we see that we have multiple lines of a single
    sentence.

    - plus a two-line
    - list for good measure
      + and a sublist
      + for really good measure
    - back to main list

        and a code block!

    ```
    and another code block!
    ```
    """)

    s = PPLCStream(test_doc)
    p = Paragraph(s, 0)
    try:
        doc = document(test_doc)
    except BadFormat as exc:
        assert 'line 12' in exc.msg
    else:
        raise Exception('failure did not occur')

def test_format_nesting():
    test_doc = dedent("""\
            **this is **really important** important info**
            """)
    doc = document(test_doc)
    assert to_html(doc) == "<p><b>this is really important important info</b></p>"

def test_formatted_doc_1():
    test_doc = dedent("""\
    Document Title
    ==============

    In **this paragraph** we see that we have multiple lines of a *single
    sentence*.

    - plus a ***two-line***
    - list `for good` measure
      + and __a sublist__
      + for ~~really~~ good measure

    Now a ==tiny paragraph== that talks about water (H~2~O) raised 2^4^ power.

        and a code block!

    ```
    and another code block!
    ```
    """)

    s = PPLCStream(test_doc)
    p = Paragraph(s, 0)
    doc = document(test_doc)
    assert shape(doc) == [Heading, Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem]]], Paragraph, CodeBlock, CodeBlock]
    assert to_html(doc) == dedent("""\
            <h1>Document Title</h1>

            <p>In <b>this paragraph</b> we see that we have multiple lines of a <i>single
            sentence</i>.</p>

            <ul>
            <li>plus a <b><i>two-line</i></b></li>
            <li>list <code>for good</code> measure</li>
                <ul>
                <li>and <u>a sublist</u></li>
                <li>for <del>really</del> good measure</li>
                </ul>
            </ul>

            <p>Now a <mark>tiny paragraph</mark> that talks about water (H<sub>2</sub>O) raised 2<sup>4</sup> power.</p>

            <pre><code>
            and a code block!
            </code></pre>

            <pre><code>
            and another code block!
            </code></pre>
            """)

def shape(document, text=False):
    result = []
    for thing in document:
        if not text and isinstance(thing, Text):
            continue
        elif isinstance(thing, Node):
            result.append(thing.__class__)
            intermediate = shape(thing.items)
            if intermediate:
                result.append(intermediate)
    return result

