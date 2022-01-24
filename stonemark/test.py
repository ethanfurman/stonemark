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

    doc = Document(test_doc)
    assert shape(doc.nodes) == [Heading,  Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem, ]]], Paragraph, CodeBlock, CodeBlock]
    assert doc.to_html() == dedent("""\
            <h2>Document Title</h2>

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
            """).strip()

def test_simple_doc_2():
    test_doc = dedent("""\
            ==============
            Document Title
            ==============

            In this paragraph we see that we have multiple lines of a single
            sentence.

            - plus a two-line
            - list for good measure
              1) and a sublist
              2) for really good measure
            - back to main list


            ```
            and another code block!
            ```
            """)
    doc = Document(test_doc)
    assert shape(doc.nodes) == [Heading, Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem]], ListItem], CodeBlock]
    assert doc.to_html() == dedent("""\
            <h1>Document Title</h1>

            <p>In this paragraph we see that we have multiple lines of a single
            sentence.</p>

            <ul>
            <li>plus a two-line</li>
            <li>list for good measure</li>
                <ol>
                <li>and a sublist</li>
                <li>for really good measure</li>
                </ol>
            <li>back to main list</li>
            </ul>

            <pre><code>
            and another code block!
            </code></pre>
            """).strip()

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
    doc = Document(test_doc)
    assert shape(doc.nodes) == [Heading, Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem]]], Heading, CodeBlock, CodeBlock]
    assert doc.to_html() == dedent("""\
            <h2>Document Title</h2>

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
            """).strip()

def test_simple_doc_4():
    test_doc = dedent("""\
            ==============
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

    doc = Document(test_doc)
    assert shape(doc.nodes) == [Heading, Paragraph, List, [ListItem, ListItem], Rule, Paragraph, CodeBlock, CodeBlock]
    assert doc.to_html() == dedent("""\
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
            """).strip()

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

    try:
        doc = Document(test_doc)
    except BadFormat as exc:
        assert 'line 12' in exc.msg
    else:
        raise Exception('failure did not occur')

def test_format_nesting_1():
    test_doc = dedent("""\
            **this is **really important** important info**
            """)
    doc = Document(test_doc)
    assert doc.to_html() == "<p><b>this is really important important info</b></p>"

def test_format_nesting_2():
    test_doc = dedent("""\
            **this is *really important* important info**
            """)
    doc = Document(test_doc)
    assert doc.to_html() == "<p><b>this is <i>really important</i> important info</b></p>"

def test_format_footnote():
    test_doc = dedent("""\
            This is a paragraph talking about many things. [^1] The question is:
            how are those many things related?

            ---

            [^1]: Okay, maybe just the one thing.
            """)
    doc = Document(test_doc)
    assert shape(doc.nodes) == [Paragraph, Rule, IDLink]
    assert doc.to_html() == dedent("""\
            <p>This is a paragraph talking about many things. <sup><a href="#footnote-1">1</a></sup> The question is:
            how are those many things related?</p>

            <hr>

            <span id="footnote-1"><sup>1</sup> Okay, maybe just the one thing.</span>
            """).strip()

def test_format_exteral_link_1():
    test_doc = dedent("""\
            This is a paragraph talking about [board game resources][1].  How many of them
            are there, anyway?

            [1]: http://www.boardgamegeek.com
            """)
    doc = Document(test_doc)
    assert shape(doc.nodes) == [Paragraph]
    assert doc.to_html() == dedent("""\
            <p>This is a paragraph talking about <a href="http://www.boardgamegeek.com">board game resources</a>.  How many of them
            are there, anyway?</p>
            """).strip()

def test_format_exteral_link_2():
    test_doc = dedent("""\
            This is a paragraph talking about [board game resources](http://www.boardgamegeek.com).  How many of them
            are there, anyway?
            """)
    doc = Document(test_doc)
    assert shape(doc.nodes) == [Paragraph]
    assert doc.to_html() == dedent("""\
            <p>This is a paragraph talking about <a href="http://www.boardgamegeek.com">board game resources</a>.  How many of them
            are there, anyway?</p>
            """).strip()

def test_format_wiki_link():
    test_doc = dedent("""\
            Check the [Documentation] for more details.
            """)
    doc = Document(test_doc)
    assert shape(doc.nodes) == [Paragraph]
    assert doc.to_html() == dedent("""\
            <p>Check the <a href="Documentation">Documentation</a> for more details.</p>
            """).strip()


def test_format_image():
    test_doc = dedent("""\
            An introductory paragraph.

            ![*a riveting picture*](https://www.image_library/photos/rivets.png)

            A concluding paragraph.
            """)
    doc = Document(test_doc)
    assert shape(doc) == [Paragraph, Image, Paragraph]
    assert doc.to_html() == dedent("""\
            <p>An introductory paragraph.</p>

            <img src="https://www.image_library/photos/rivets.png" alt="<i>a riveting picture</i>">

            <p>A concluding paragraph.</p>
            """).strip()

def test_formatted_doc_1():
    test_doc = dedent("""\
            ==============
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
    doc = Document(test_doc)
    assert shape(doc.nodes) == [Heading, Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem]]], Paragraph, CodeBlock, CodeBlock]
    assert doc.to_html() == dedent("""\
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
            """).strip()

def shape(document, text=False):
    result = []
    if isinstance(document, Document):
        document = document.nodes
    for thing in document:
        if not text and isinstance(thing, Text):
            continue
        elif isinstance(thing, Node):
            result.append(thing.__class__)
            intermediate = shape(thing.items)
            if intermediate:
                result.append(intermediate)
    return result

