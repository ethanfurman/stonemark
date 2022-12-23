'''
Tests for StoneMark
'''

from __future__ import unicode_literals

from . import PPLCStream
from . import *
from textwrap import dedent
from unittest import TestCase, main


class TestCase(TestCase):

    def __init__(self, *args, **kwds):
        regex = getattr(self, 'assertRaisesRegex', None)
        if regex is None:
            self.assertRaisesRegex = getattr(self, 'assertRaisesRegexp')
        super(TestCase, self).__init__(*args, **kwds)


class TestPPLCStream(TestCase):

    def test_peek_line(self):
        sample = u'line one\nline two'
        stream = PPLCStream(sample)
        self.assertEqual(stream.current_line, 'line one\n')
        self.assertEqual(stream.peek_line(), 'line two\n')
        stream.skip_line()
        self.assertEqual(stream.current_line, 'line two\n')
        self.assertEqual(stream.peek_line(), '')
        stream.skip_line()
        self.assertEqual(stream.current_line, '')
        try:
            stream.skip_line()
        except EOFError:
            pass
        else:
            raise ValueError('EOFError not raised')

class TestStonemark(TestCase):
    def test_simple_doc_1(self):
        test_doc = dedent("""\
        ==============
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
        self.assertEqual( shape(doc.nodes), [Heading,  Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem, ]]], Paragraph, CodeBlock, CodeBlock])
        self.assertEqual( doc.to_html(), dedent("""\
                <h1>Document Title</h1>

                <p>In this paragraph we see that we have multiple lines of a single sentence.</p>

                <ul>
                <li>plus a two-line</li>
                <li>list for good measure</li>
                    <ul>
                    <li>and a sublist</li>
                    <li>for really good measure</li>
                    </ul>
                </ul>

                <p>Now a tiny paragraph.</p>

                <pre><code>and a code block!</code></pre>

                <pre><code>and another code block!</code></pre>
                """).strip())

    def test_simple_doc_2(self):
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
        self.assertEqual( shape(doc.nodes), [Heading, Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem]], ListItem], CodeBlock])
        self.assertEqual( doc.to_html(), dedent("""\
                <h1>Document Title</h1>

                <p>In this paragraph we see that we have multiple lines of a single sentence.</p>

                <ul>
                <li>plus a two-line</li>
                <li>list for good measure</li>
                    <ol>
                    <li>and a sublist</li>
                    <li>for really good measure</li>
                    </ol>
                <li>back to main list</li>
                </ul>

                <pre><code>and another code block!</code></pre>
                """).strip())

    def test_simple_doc_3(self):
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
        self.assertEqual( shape(doc.nodes), [Heading, Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem]]], Heading, CodeBlock, CodeBlock])
        self.assertEqual( doc.to_html(), dedent("""\
                <h2>Document Title</h2>

                <p>In this paragraph we see that we have multiple lines of a single sentence.</p>

                <ul>
                <li>plus a two-line</li>
                <li>list for good measure</li>
                    <ul>
                    <li>and a sublist</li>
                    <li>for really good measure</li>
                    </ul>
                </ul>

                <h3>Now a tiny paragraph I mean header</h3>

                <pre><code>and a code block!</code></pre>

                <pre><code>and another code block!</code></pre>
                """).strip())

    def test_simple_doc_4(self):
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
        doc = Document(test_doc, first_header_is_title=True)
        self.assertEqual( shape(doc.nodes), [Heading, Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem]]], Heading, CodeBlock, CodeBlock])
        self.assertEqual( doc.to_html(), dedent("""\
                <h1>Document Title</h1>

                <p>In this paragraph we see that we have multiple lines of a single sentence.</p>

                <ul>
                <li>plus a two-line</li>
                <li>list for good measure</li>
                    <ul>
                    <li>and a sublist</li>
                    <li>for really good measure</li>
                    </ul>
                </ul>

                <h3>Now a tiny paragraph I mean header</h3>

                <pre><code>and a code block!</code></pre>

                <pre><code>and another code block!</code></pre>
                """).strip())

    def test_simple_doc_5(self):
        test_doc = dedent("""\
                Document Title
                --------------

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
        doc = Document(test_doc, first_header_is_title=True)
        self.assertEqual( shape(doc.nodes), [Heading, Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem]]], Heading, CodeBlock, CodeBlock])
        self.assertEqual( doc.to_html(), dedent("""\
                <h1>Document Title</h1>

                <p>In this paragraph we see that we have multiple lines of a single sentence.</p>

                <ul>
                <li>plus a two-line</li>
                <li>list for good measure</li>
                    <ul>
                    <li>and a sublist</li>
                    <li>for really good measure</li>
                    </ul>
                </ul>

                <h3>Now a tiny paragraph I mean header</h3>

                <pre><code>and a code block!</code></pre>

                <pre><code>and another code block!</code></pre>
                """).strip())

    def test_simple_doc_6(self):
        self.maxDiff = None
        test_doc = dedent("""\
                Document Title
                --------------

                In this paragraph we see that we have multiple lines of a single
                sentence.

                - plus a two-line
                - list for good measure

                  ![and a generic image](some_image.png)

                ---

                Now a tiny paragraph.

                    and a code block!

                ```
                and another code block!
                ```
                """)

        doc = Document(test_doc)
        self.assertEqual( doc.to_html(), dedent("""\
                <h3>Document Title</h3>

                <p>In this paragraph we see that we have multiple lines of a single sentence.</p>

                <ul>
                <li>plus a two-line</li>
                <li>list for good measure
                <div><img src="some_image.png" alt="and a generic image"></div>
                </li>
                </ul>

                <hr>

                <p>Now a tiny paragraph.</p>

                <pre><code>and a code block!</code></pre>

                <pre><code>and another code block!</code></pre>
                """).strip())
        self.assertEqual( shape(doc.nodes), [Heading, Paragraph, List, [ListItem, ListItem, [Image]], Rule, Paragraph, CodeBlock, CodeBlock])

    def test_simple_doc_7(self):
        self.maxDiff = None
        test_doc = dedent("""\
                A Small Heading
                ...............

                The list of orders are color coded following this key:

                - Red -- Insufficient stock on hand to pull order [^1]
                - Yellow  --  Materials confirmed by warehouse

                [^1]: Within each order the specific ingredient with insufficient stock will display
                      in red while items with sufficient stock will display in black. 

                """)
        doc = Document(test_doc)
        self.assertEqual( doc.to_html(), dedent("""\
                <h4>A Small Heading</h4>

                <p>The list of orders are color coded following this key:</p>

                <ul>
                <li>Red -- Insufficient stock on hand to pull order<sup><a href="#footnote-1">1</a></sup></li>
                <li>Yellow  --  Materials confirmed by warehouse</li>
                </ul>

                <div class="footnote" id="footnote-1"><sup>1</sup>Within each order the specific ingredient with insufficient stock will display in red while items with sufficient stock will display in black.</div>
                """).strip())
        self.assertEqual( shape(doc.nodes), [Heading, Paragraph, List, [ListItem, ListItem], IDLink])

    def test_failure_1(self):
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

        with self.assertRaisesRegex(FormatError, 'no match found'):
            doc = Document(test_doc)

    def test_format_nesting_1(self):
        test_doc = dedent("""\
                **this is **really important** important info**
                """)
        doc = Document(test_doc)
        self.assertEqual( doc.to_html(), "<p><b>this is really important important info</b></p>")

    def test_format_nesting_2(self):
        test_doc = dedent("""\
                **this is *really important* important info**
                """)
        doc = Document(test_doc)
        self.assertEqual( doc.to_html(), "<p><b>this is <i>really important</i> important info</b></p>")

    def test_format_non_lspha(self):
        test_doc = dedent("""\
                **this is important info**!
                """)
        doc = Document(test_doc)
        self.assertEqual( doc.to_html(), "<p><b>this is important info</b>!</p>")

    def test_format_footnote(self):
        self.maxDiff = None
        test_doc = dedent("""\
                This is a paragraph talking about many things. [^1] The question is:
                how are those many things related?

                ---

                [^1]: Okay, maybe just the one thing.
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Paragraph, Rule, IDLink])
        self.assertEqual( doc.to_html(), dedent("""\
                <p>This is a paragraph talking about many things.<sup><a href="#footnote-1">1</a></sup> The question is: how are those many things related?</p>

                <hr>

                <div class="footnote" id="footnote-1"><sup>1</sup>Okay, maybe just the one thing.</div>
                """).strip())

    def test_format_external_link_1(self):
        test_doc = dedent("""\
                This is a paragraph talking about [board game resources][1].  How many of them
                are there, anyway?

                [1]: http://www.boardgamegeek.com
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Paragraph])
        self.assertEqual( doc.to_html(), dedent("""\
                <p>This is a paragraph talking about <a href="http://www.boardgamegeek.com">board game resources</a>.  How many of them are there, anyway?</p>
                """).strip())

    def test_format_external_link_2(self):
        test_doc = dedent("""\
                This is a paragraph talking about [board game resources](http://www.boardgamegeek.com).  How many of them
                are there, anyway?
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Paragraph])
        self.assertEqual( doc.to_html(), dedent("""\
                <p>This is a paragraph talking about <a href="http://www.boardgamegeek.com">board game resources</a>.  How many of them are there, anyway?</p>
                """).strip())

    def test_format_external_link_3(self):
        test_doc = dedent("""\
                This is a paragraph talking about [board game resources].  How many of them
                are there, anyway?

                [board game resources]: http://www.boardgamegeek.com
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Paragraph])
        self.assertEqual( doc.to_html(), dedent("""\
                <p>This is a paragraph talking about <a href="http://www.boardgamegeek.com">board game resources</a>.  How many of them are there, anyway?</p>
                """).strip())

    def test_format_external_link_4(self):
        test_doc = dedent("""\
                This is a paragraph talking about [](http://www.boardgamegeek.com).  How many of them
                are there, anyway?
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Paragraph])
        self.assertEqual( doc.to_html(), dedent("""\
                <p>This is a paragraph talking about <a href="http://www.boardgamegeek.com">http://www.boardgamegeek.com</a>.  How many of them are there, anyway?</p>
                """).strip())

    def test_format_wiki_link(self):
        test_doc = dedent("""\
                Check the [Documentation] for more details.
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Paragraph])
        self.assertEqual( doc.to_html(), dedent("""\
                <p>Check the <a href="Documentation">Documentation</a> for more details.</p>
                """).strip())

    def test_format_image(self):
        test_doc = dedent("""\
                An introductory paragraph.

                ![*a riveting picture*](https://www.image_library/photos/rivets.png "Rivets!")

                A concluding paragraph.
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc), [Paragraph, Image, Paragraph])
        self.assertEqual( doc.to_html(), dedent("""\
                <p>An introductory paragraph.</p>


                <div><img src="https://www.image_library/photos/rivets.png" title="Rivets!" alt="<i>a riveting picture</i>"></div>


                <p>A concluding paragraph.</p>
                """).strip())

    def test_format_split_parens(self):
        test_doc = dedent("""\
                A paragraph with a footnote[^1].

                [^1]: a command line parameter is available to set the location (and should be
                      used for production).
                """)
        doc = Document(test_doc)
        self.assertEqual(doc.to_html(), dedent("""\
                <p>A paragraph with a footnote<sup><a href="#footnote-1">1</a></sup>.</p>

                <div class="footnote" id="footnote-1"><sup>1</sup>a command line parameter is available to set the location (and should be used for production).</div>
                """).strip())


    def test_formatted_doc_1(self):
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
        self.assertEqual( shape(doc.nodes), [Heading, Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem]]], Paragraph, CodeBlock, CodeBlock])
        self.assertEqual( doc.to_html(), dedent("""\
                <h1>Document Title</h1>

                <p>In <b>this paragraph</b> we see that we have multiple lines of a <i>single sentence</i>.</p>

                <ul>
                <li>plus a <b><i>two-line</i></b></li>
                <li>list <code>for good</code> measure</li>
                    <ul>
                    <li>and <u>a sublist</u></li>
                    <li>for <del>really</del> good measure</li>
                    </ul>
                </ul>

                <p>Now a <mark>tiny paragraph</mark> that talks about water (H<sub>2</sub>O) raised 2<sup>4</sup> power.</p>

                <pre><code>and a code block!</code></pre>

                <pre><code>and another code block!</code></pre>
                """).strip())

    def test_html_chars(self):
        self.maxDiff = None
        test_doc = dedent("""\
                ===================
                Some Maths & Stuffs
                ===================

                1) a = 4
                2) b < 5
                3) c > 1

                To ~~everyone~~ *anyone* **who <hears> this** -- HELP![^jk]

                ```
                a < b >= c
                ```

                Is a < b ?  Yes.

                Is a >= b ?  Yes.

                Is a & b = a ?  Yes.

                ![someone sayd, "OReily?"](https://www.fake.com/images/123.png)

                ---

                [^jk]: Just a joke!  I'm >fine<!
                """)
        doc = Document(test_doc)
        self.assertEqual(
                doc.to_html(),
                dedent("""\
                <h1>Some Maths &amp; Stuffs</h1>

                <ol>
                <li>a = 4</li>
                <li>b &lt; 5</li>
                <li>c &gt; 1</li>
                </ol>

                <p>To <del>everyone</del> <i>anyone</i> <b>who &lt;hears&gt; this</b> -- HELP!<sup><a href="#footnote-jk">jk</a></sup></p>

                <pre><code>a &lt; b &gt;= c</code></pre>

                <p>Is a &lt; b ?  Yes.</p>

                <p>Is a &gt;= b ?  Yes.</p>

                <p>Is a &amp; b = a ?  Yes.</p>


                <div><img src="https://www.fake.com/images/123.png" alt="someone sayd, &quot;OReily?&quot;"></div>


                <hr>

                <div class="footnote" id="footnote-jk"><sup>jk</sup>Just a joke!  I&apos;m &gt;fine&lt;!</div>
                """).strip(), doc.to_html())

    def test_footnote_children(self):
        self.maxDiff = None
        test_doc = dedent("""\
                Step 1: Build your server
                =========================

                Either include the `OpenSSH` and `Postgres` packages when creating the server, or run the
                following commands after the server is operational [^1]:

                ``` sh
                apt-get install openssh-server postgresql-9.1
                # optional: denyhosts
                ```

                Now make sure your server has all the latest versions & patches by doing an update [^2]:

                ``` sh
                apt-get update
                apt-get dist-upgrade
                ```

                Although not always essential it's probably a good idea to reboot your server now and make
                sure it all comes back up and you can login via `ssh`.

                Now we're ready to start the OpenERP install.

                ----

                [^1]: Creating the server, whether with dedicated hardware or as a virtual machine, is not
                      covered by these instructions.

                [^2]: If the `update` command results in `failed to fetch` errors, you can try these commands:

                      ```
                      rm -rf /var/lib/apt/lists/*
                      apt-get clean
                      apt-get update
                      ```

                      And try the `update` command again.  If you are now having missing key errors, try:

                      ```sh
                      gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv <MISSING_KEY>
                      ```

                      Then try the `update` command one more time.

                      When `update` works correctly (no errors) run the `dist-upgrade` command.

                ----

                [Next](oe-install-step-2)
                """)
        expected = dedent("""\
                <h2>Step 1: Build your server</h2>

                <p>Either include the <code>OpenSSH</code> and <code>Postgres</code> packages when creating the server, or run the following commands after the server is operational<sup><a href="#footnote-1">1</a></sup>:</p>

                <pre><code>apt-get install openssh-server postgresql-9.1
                # optional: denyhosts</code></pre>

                <p>Now make sure your server has all the latest versions &amp; patches by doing an update<sup><a href="#footnote-2">2</a></sup>:</p>

                <pre><code>apt-get update
                apt-get dist-upgrade</code></pre>

                <p>Although not always essential it&apos;s probably a good idea to reboot your server now and make sure it all comes back up and you can login via <code>ssh</code>.</p>

                <p>Now we&apos;re ready to start the OpenERP install.</p>

                <hr>

                <div class="footnote" id="footnote-1"><sup>1</sup>Creating the server, whether with dedicated hardware or as a virtual machine, is not covered by these instructions.</div>

                <div class="footnote" id="footnote-2"><sup>2</sup>If the <code>update</code> command results in <code>failed to fetch</code> errors, you can try these commands:
                <pre><code>rm -rf /var/lib/apt/lists/*
                apt-get clean
                apt-get update</code></pre>
                <p>And try the <code>update</code> command again.  If you are now having missing key errors, try:</p>
                <pre><code>gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv &lt;MISSING_KEY&gt;</code></pre>
                <p>Then try the <code>update</code> command one more time.</p>
                <p>When <code>update</code> works correctly (no errors) run the <code>dist-upgrade</code> command.</p></div>

                <hr>

                <p><a href="oe-install-step-2">Next</a></p>
                """).strip()
        self.assertEqual(Document(test_doc).to_html(), expected)

    def test_optional_blank_lines(self):
        self.maxDiff = None
        test_doc = dedent("""\
                ===================
                Pulse Specification
                ===================

                Tracking
                ========

                - frequency
                  - daily
                  - weekly
                  - monthly
                  - yearly

                - status
                  - pass/fail
                  - percentage
                  - text
                  - tripline

                - device/job
                  - 11.16/sync
                  - 11.111/backup""")
        expected = dedent("""\
                <h1>Pulse Specification</h1>

                <h2>Tracking</h2>

                <ul>
                <li>frequency</li>
                    <ul>
                    <li>daily</li>
                    <li>weekly</li>
                    <li>monthly</li>
                    <li>yearly</li>
                    </ul>
                <li>status</li>
                    <ul>
                    <li>pass/fail</li>
                    <li>percentage</li>
                    <li>text</li>
                    <li>tripline</li>
                    </ul>
                <li>device/job</li>
                    <ul>
                    <li>11.16/sync</li>
                    <li>11.111/backup</li>
                    </ul>
                </ul>""").strip()
        self.assertEqual(Document(test_doc).to_html(), expected)

    def test_code_with_footnote(self):
        test_doc = dedent("""\
                Here is `some code`[^hah].

                [^hah]: and a footnote
                """)
        expected = dedent("""\
                <p>Here is <code>some code</code><sup><a href="#footnote-hah">hah</a></sup>.</p>

                <div class="footnote" id="footnote-hah"><sup>hah</sup>and a footnote</div>
                """).strip()
        self.assertEqual(Document(test_doc).to_html(), expected)

    def test_duplicate_footnote(self):
        test_doc = dedent("""\
                Here is `some code`[^hah].

                And then another [^hah].

                [^hah]: and a footnote
                """)
        expected = dedent("""\
                <p>Here is <code>some code</code><sup><a href="#footnote-hah">hah</a></sup>.</p>

                <p>And then another<sup><a href="#footnote-hah">hah</a></sup>.</p>

                <div class="footnote" id="footnote-hah"><sup>hah</sup>and a footnote</div>
                """).strip()
        self.assertEqual(Document(test_doc).to_html(), expected)

    def test_parens(self):
        test_doc = dedent("""\
                Here is (a parenthetical)[^hah].

                [^hah]: and a footnote
                """)
        expected = dedent("""\
                <p>Here is (a parenthetical)<sup><a href="#footnote-hah">hah</a></sup>.</p>

                <div class="footnote" id="footnote-hah"><sup>hah</sup>and a footnote</div>
                """).strip()
        self.assertEqual(Document(test_doc).to_html(), expected)

    def test_parens_in_code(self):
        test_doc = dedent("""\
                Helper for inserting `Enum` members into a namespace (usually `globals()`).
                """)
        expected = dedent("""\
                <p>Helper for inserting <code>Enum</code> members into a namespace (usually <code>globals()</code>).</p>
                """).strip()
        self.assertEqual(Document(test_doc).to_html(), expected)

    def test_editorial_comment(self):
        test_doc = dedent("""\
                Here is [[editor: wow]][^hah].

                [^hah]: and a footnote
                """)
        expected = dedent("""\
                <p>Here is [editor: wow]<sup><a href="#footnote-hah">hah</a></sup>.</p>

                <div class="footnote" id="footnote-hah"><sup>hah</sup>and a footnote</div>
                """).strip()
        self.assertEqual(Document(test_doc).to_html(), expected)

    def test_code_after_link(self):
        test_doc = dedent("""\
                [^1] `some code` and

                [wiki_page] `204` is the `No Content` status code, and indicates success.

                [^1]: blah
                """)
        expected = dedent("""\
                <p><sup><a href="#footnote-1">1</a></sup> <code>some code</code> and</p>

                <p><a href="wiki_page">wiki_page</a> <code>204</code> is the <code>No Content</code> status code, and indicates success.</p>

                <div class="footnote" id="footnote-1"><sup>1</sup>blah</div>
                """).strip()
        self.assertEqual(Document(test_doc).to_html(), expected)

    def test_coded_headers(self):
        test_doc = dedent("""\
                ================
                `Document Title`
                ================

                In this paragraph we see that we have multiple lines of a single
                sentence.

                - plus a two-line
                - list for good measure
                  + and a sublist
                  + for really good measure

                `stuff`
                -------

                Now a tiny paragraph.

                    and a code block!

                ```
                and another code block!
                ```
                """)

        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Heading,  Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem, ]]], Heading, Paragraph, CodeBlock, CodeBlock])
        self.assertEqual( doc.to_html(), dedent("""\
                <h1><code>Document Title</code></h1>

                <p>In this paragraph we see that we have multiple lines of a single sentence.</p>

                <ul>
                <li>plus a two-line</li>
                <li>list for good measure</li>
                    <ul>
                    <li>and a sublist</li>
                    <li>for really good measure</li>
                    </ul>
                </ul>

                <h3><code>stuff</code></h3>

                <p>Now a tiny paragraph.</p>

                <pre><code>and a code block!</code></pre>

                <pre><code>and another code block!</code></pre>
                """).strip())

    def test_not_html_headers(self):
        test_doc = dedent("""\
                =========
                Why X < Y
                =========

                a bunch of stuff
                """)

        doc = Document(test_doc)
        self.assertEqual(doc.to_html(), dedent("""\
                <h1>Why X &lt; Y</h1>

                <p>a bunch of stuff</p>
                """).strip())

    def test_header_sizes(self):
        test_doc = dedent("""\
                =========
                Why X < Y
                =========

                a bunch of stuff

                Summary
                =======

                blah blah

                Notes
                -----

                more blah
                """)

        doc = Document(test_doc, header_sizes=(2,4,5))
        self.assertEqual(doc.to_html(), dedent("""\
                <h2>Why X &lt; Y</h2>

                <p>a bunch of stuff</p>

                <h4>Summary</h4>

                <p>blah blah</p>

                <h5>Notes</h5>

                <p>more blah</p>
                """).strip())


    def test_quotation_1(self):
        test_doc = dedent("""\
                > single level quote

                > level 1 and
                >> level 2
                > level 1 again
                """)
        doc = Document(test_doc, header_sizes=(2,4,5))
        self.assertEqual(doc.to_html(), dedent("""\
                <blockquote>
                            <p>single level quote</p>
                </blockquote>

                <blockquote>
                            <p>level 1 and</p>
                            <blockquote>
                                        <p>level 2</p>
                            </blockquote>
                            <p>level 1 again</p>
                </blockquote>
                """).strip(),
                doc.to_html(),
                )

    def test_quotation_2(self):
        test_doc = dedent("""\
                >>> third level quote
                >>> still third
                >> second
                > first

                > level 1 and
                >> level 2
                > level 1 again
                """)
        doc = Document(test_doc, header_sizes=(2,4,5))
        self.assertEqual(doc.to_html(), dedent("""\
                <blockquote>
                            <blockquote>
                                        <blockquote>
                                                    <p>third level quote still third</p>
                                        </blockquote>
                                        <p>second</p>
                            </blockquote>
                            <p>first</p>
                </blockquote>

                <blockquote>
                            <p>level 1 and</p>
                            <blockquote>
                                        <p>level 2</p>
                            </blockquote>
                            <p>level 1 again</p>
                </blockquote>
                """).strip(),
                doc.to_html(),
                )

    def test_quotation_3(self):
        test_doc = dedent("""\
                > A Title
                > =======
                >
                > Then some text, followed by
                >
                > - list item 1
                > - list item 2
                >
                > ``` python
                > and some code
                >
                > and more code
                > ```
                >> another quote block
                > and done

                so there.
                """)
        doc = Document(test_doc)
        self.assertEqual(dedent(doc.to_html()), dedent("""\
                <blockquote>
                            <h2>A Title</h2>
                            <p>Then some text, followed by</p>
                            <ul>
                            <li>list item 1</li>
                            <li>list item 2</li>
                            </ul>
                            <pre><code>and some code

                            and more code</code></pre>
                            <blockquote>
                                        <p>another quote block</p>
                            </blockquote>
                            <p>and done</p>
                </blockquote>

                <p>so there.</p>
                """).strip(),
                doc.to_html(),
                )

    def test_code_block_with_blank_line(self):
        test_doc = dedent("""\
                ``` python
                and some code

                and more code
                ```
                """)
        doc = Document(test_doc)
        self.assertEqual(doc.to_html(), dedent("""\
                <pre><code>and some code

                and more code</code></pre>
                """).strip(),
                doc.to_html(),
                )

    def test_code_block_in_list(self):
        test_doc = dedent("""\
                Other documents can be linked to from here, or just created.

                Quick rundown of features:

                - `*italic*` --> *italic*
                - `**bold**` --> **bold**
                - `***bold italic***` --> ***bold italic***
                - `__underline__` --> __underline__
                - `~~strike-through~~` --> ~~strike-through~~
                - `==highlight==` --> ==highlight==

                Headings
                ========

                - level 1 heading
                  ```
                  =========
                  Heading 1
                  =========
                  ```

                - level 2 heading
                  ```
                  Heading 2
                  =========
                  ```

                - level 3 heading
                  ```
                  Heading 3
                  ---------
                  ```
                  """)
        doc = Document(test_doc)
        self.assertEqual(doc.to_html(), dedent("""\
                <p>Other documents can be linked to from here, or just created.</p>

                <p>Quick rundown of features:</p>

                <ul>
                <li><code>*italic*</code> --&gt; <i>italic</i></li>
                <li><code>**bold**</code> --&gt; <b>bold</b></li>
                <li><code>***bold italic***</code> --&gt; <b><i>bold italic</i></b></li>
                <li><code>__underline__</code> --&gt; <u>underline</u></li>
                <li><code>~~strike-through~~</code> --&gt; <del>strike-through</del></li>
                <li><code>==highlight==</code> --&gt; <mark>highlight</mark></li>
                </ul>

                <h2>Headings</h2>

                <ul>
                <li>level 1 heading<pre><code>=========
                Heading 1
                =========</code></pre></li>
                <li>level 2 heading<pre><code>Heading 2
                =========</code></pre></li>
                <li>level 3 heading<pre><code>Heading 3
                ---------</code></pre></li>
                </ul>
                """).strip(),
                doc.to_html(),
                )

    def test_combined_text_formatting(self):
        self.maxDiff = None
        test_doc = dedent("""\
                __*underlined italic*__

                *__italicized underline__*

                **~~bolded strike-through~~**

                ~~**struck-through bold**~~

                With **punctuation**: In *various ways*(oops).
                """)
        doc = Document(test_doc)
        self.assertEqual(doc.to_html(), dedent("""\
                <p><u><i>underlined italic</i></u></p>

                <p><i><u>italicized underline</u></i></p>
                
                <p><b><del>bolded strike-through</del></b></p>
                
                <p><del><b>struck-through bold</b></del></p>
                
                <p>With <b>punctuation</b>: In *various ways*(oops).</p>
                """).strip(),
                )

    def test_heading_vs_hr(self):
        self.maxDiff = None
        test_doc = dedent("""\
                a heading
                ---------

                another heading
                --------------
                and a paragraph

                followed by a paragraph
                (because they have at least two lines)
                --------------------------------------
                and a new paragraph after a header
                - a list
                should be a paragraph followed by an hr
                --------------------
                    """)
        doc = Document(test_doc)
        self.assertEqual(dedent(doc.to_html()), dedent("""\
                <h3>a heading</h3>

                <h3>another heading</h3>

                <p>and a paragraph</p>

                <p>followed by a paragraph (because they have at least two lines)</p>

                <hr>

                <p>and a new paragraph after a header</p>

                <ul>
                <li>a list</li>
                </ul>

                <p>should be a paragraph followed by an hr</p>

                <hr>
                """).strip(),
                # doc.to_html(),
                )

    def test_heading_in_code_block(self):
        test_doc = dedent("""\
                Headings
                ========

                    =========
                    Heading 1
                    =========

                    Heading 2
                    =========

                    Heading 3
                    ---------
                    """)
        doc = Document(test_doc)
        self.assertEqual(dedent(doc.to_html()), dedent("""\
                <h2>Headings</h2>

                <pre><code>=========
                Heading 1
                =========

                Heading 2
                =========

                Heading 3
                ---------</code></pre>
                """).strip(),
                # doc.to_html(),
                )

    def test_backslash_disappears(self):
        test_doc = dedent("""\
                \\*italic\\* --> *italic*
                """)
        doc = Document(test_doc)
        self.assertEqual(doc.to_html(), dedent("""\
                <p>*italic* --&gt; <i>italic</i></p>
                """).strip(),
                doc.to_html(),
                )

    def test_backslash_remains(self):
        self.maxDiff = None
        test_doc = dedent("""\
                \\\\*italic\\\\* --> \\\\*italic\\\\*
                """)
        doc = Document(test_doc)
        self.assertEqual(doc.to_html(), dedent("""\
                <p>\\<i>italic\\</i> --&gt; \\<i>italic\\</i></p>
                """).strip(),
                # doc.to_html(),
                )

    def test_proper_spacing(self):
        test_doc = dedent("""\
                A paragraph
                - with a list
                - immediately after
                  which has a multi-
                  line entry
                  """)
        doc = Document(test_doc)
        self.assertEqual(doc.to_html(), dedent("""\
                <p>A paragraph</p>

                <ul>
                <li>with a list</li>
                <li>immediately after which has a multiline entry</li>
                </ul>
                """).strip(),
                doc.to_html(),
                )

    def test_two_paragraphs(self):
        test_doc = dedent("""\
                a test of multiple

                paragraphs
                  """)
        doc = Document(test_doc)
        self.assertEqual(doc.to_html(), dedent("""\
                <p>a test of multiple</p>

                <p>paragraphs</p>
                """).strip(),
                doc.to_html(),
                )

    def test_backtick_in_code_block(self):
        test_doc = dedent("""\
                `a test of \\` escaping backticks`
                  """)
        doc = Document(test_doc)
        self.assertEqual(doc.to_html(), dedent("""\
                <p><code>a test of ` escaping backticks</code></p>
                """).strip(),
                doc.to_html(),
                )
        test_doc = dedent("""\
                ```
                a test of \\` escaping backticks
                ```
                  """)
        doc = Document(test_doc)
        self.assertEqual(doc.to_html(), dedent("""\
                <pre><code>a test of \\` escaping backticks</code></pre>
                """).strip(),
                doc.to_html(),
                )

        test_doc = dedent("""\
                ```
                a test of ` backticks in code blocks
                ```
                  """)
        doc = Document(test_doc)
        self.assertEqual(doc.to_html(), dedent("""\
                <pre><code>a test of ` backticks in code blocks</code></pre>
                """).strip(),
                doc.to_html(),
                )

    def test_a_bunch(self):
        self.maxDiff = None
        test_doc = dedent("""\
                1. Start Nutritional Server

                   ```
                   # ssh root@192.168.11.68
                   # ps -efw|grep -i vbox
                   ...
                   root      4262  4247 12 Dec07 ?        14:33:22 /usr/lib/virtualbox/VBoxHeadless --comment Nutritional Server - Master --startvm ...
                   ...
                   ```

                   + if not running,
                     ```
                     # fnx_start_nutritional_server
                     ```
                     * (This starts virtual machine 10.39, without a connection to your display)

                     * (For troubleshooting, remove --type headless and it will come up on your display)

                2. Enable shared drive access to L:

                   + VNC to 10.39 and verify L: is browsable (enter password probably) and then answer N

                   + the L: drive should be connected to 11.254/Labels using the standard password.

                3. Print Nutritional Labels

                   + To print nutritional labels, ssh to 11.16 and execute:
                     ```
                     /usr/local/lib/python2.7/dist-packages/fenx/prepNutriPanelFromSSs.py
                     ```
                4. Override selected label percentage values

                   + When printing nutritional panels the option now exists to override the calculated percentages which,
                     as we've detailed, occasionally result in wrong values due to the specific implementation used.  To
                     compensate, I've added the ability to override specific values when requesting the label to print.
                     The application prompt, which previously read:
                     ```
                     LOF to quit or enter as ITEMNO<comma>QTY<space>ITEMNO<space><etc>:
                     ```
                     now reads:
                     ```
                     LOF to quit or enter as ITEMNO[:nutrient=xx[:nutrient=xx]][,qty]:
                     ```

                   This allows you to respond with a command like:
                   `006121:FAT_PERC=22:VITD_PER=13,2`

                   This command will print the nutritional label for item 006121 and will show the fat percentage as 22%, the vitamin D percentage as 13%, and will print 2 labels.

                   You can still use the space to separate multiple items.  For example,

                   `007205 006121 006121:FAT_PERC=22:VITD_PER=13,2 007205:POT_PER=4,2 007205 006121`

                   The above command will print item 007205, then 006121, then 2 copies each of both 006121 ahnd 007205 with the changed fat and vit_D percentages, and finally 007205 and 006121 again.  Note that percentage changes made to an item will persist while the application is still running (ie, until you LOF out), so the final two labels show the last overridden values entered during the run cycle.

                   This should allow labels to be corrected until a more permanent automatic method can be integrated into the utility.

                   Note: it is possible to set an override percent value that doesn't conform to the rounding rules that may on subsequent printing within the current run session result in the entered value being rounded.  For example, specifying 13% will print 13% the first pass through, but an immediate reprint will show 15% as the rounding rules specify that values in the 10-50 range be rounded to the nearest 5%.  To avoid this you should only specify valid conforming values as overrides.
                  """)
        doc = Document(test_doc)
        self.assertEqual(doc.to_html(), dedent("""\
                    <ol>
                    <li>Start Nutritional Server<pre><code># ssh root@192.168.11.68
                    # ps -efw|grep -i vbox
                    ...
                    root      4262  4247 12 Dec07 ?        14:33:22 /usr/lib/virtualbox/VBoxHeadless --comment Nutritional Server - Master --startvm ...
                    ...</code></pre></li>
                        <ul>
                        <li>if not running,<pre><code># fnx_start_nutritional_server</code></pre></li>
                        <ul>
                        <li>(This starts virtual machine 10.39, without a connection to your display)</li>
                        <li>(For troubleshooting, remove --type headless and it will come up on your display)</li>
                        </ul>
                        </ul>
                    <li>Enable shared drive access to L:</li>
                        <ul>
                        <li>VNC to 10.39 and verify L: is browsable (enter password probably) and then answer N</li>
                        <li>the L: drive should be connected to 11.254/Labels using the standard password.</li>
                        </ul>
                    <li>Print Nutritional Labels</li>
                        <ul>
                        <li>To print nutritional labels, ssh to 11.16 and execute:<pre><code>/usr/local/lib/python2.7/dist-packages/fenx/prepNutriPanelFromSSs.py</code></pre></li>
                        </ul>
                    <li>Override selected label percentage values<p>This allows you to respond with a command like: <code>006121:FAT_PERC=22:VITD_PER=13,2</code></p><p>This command will print the nutritional label for item 006121 and will show the fat percentage as 22%, the vitamin D percentage as 13%, and will print 2 labels.</p><p>You can still use the space to separate multiple items.  For example,</p><p><code>007205 006121 006121:FAT_PERC=22:VITD_PER=13,2 007205:POT_PER=4,2 007205 006121</code></p><p>The above command will print item 007205, then 006121, then 2 copies each of both 006121 ahnd 007205 with the changed fat and vit_D percentages, and finally 007205 and 006121 again.  Note that percentage changes made to an item will persist while the application is still running (ie, until you LOF out), so the final two labels show the last overridden values entered during the run cycle.</p><p>This should allow labels to be corrected until a more permanent automatic method can be integrated into the utility.</p><p>Note: it is possible to set an override percent value that doesn&apos;t conform to the rounding rules that may on subsequent printing within the current run session result in the entered value being rounded.  For example, specifying 13% will print 13% the first pass through, but an immediate reprint will show 15% as the rounding rules specify that values in the 10-50 range be rounded to the nearest 5%.  To avoid this you should only specify valid conforming values as overrides.</p></li>
                        <ul>
                        <li>When printing nutritional panels the option now exists to override the calculated percentages which, as we&apos;ve detailed, occasionally result in wrong values due to the specific implementation used.  To compensate, I&apos;ve added the ability to override specific values when requesting the label to print. The application prompt, which previously read:<pre><code>LOF to quit or enter as ITEMNO&lt;comma&gt;QTY&lt;space&gt;ITEMNO&lt;space&gt;&lt;etc&gt;:</code></pre><p>now reads:</p><pre><code>LOF to quit or enter as ITEMNO[:nutrient=xx[:nutrient=xx]][,qty]:</code></pre></li>
                        </ul>
                    </ol>
                """).strip(),
                # doc.to_html(),
                )

    def test_a_bunch_more(self):
        self.maxDiff = None
        test_doc = dedent("""\
                1: Start Nutritional Server
                ---------------------------

                ```
                # ssh root@192.168.11.68
                # ps -efw|grep -i vbox
                ...
                root      4262  4247 12 Dec07 ?        14:33:22 /usr/lib/virtualbox/VBoxHeadless --comment Nutritional Server - Master --startvm ...
                ...
                ```
                if not running,
                ```
                # fnx_start_nutritional_server
                ```
                (This starts virtual machine 10.39, without a connection to your display)

                (For troubleshooting, remove --type headless and it will come up on your display)

                2: Enable shared drive access to L:
                -----------------------------------

                VNC to 10.39 and verify L: is browsable (enter password probably) and then answer N

                the L: drive should be connected to 11.254/Labels using the standard password.


                3: Print Nutritional Labels
                ---------------------------

                To print nutritional labels, ssh to 11.16 and execute:
                ```
                /usr/local/lib/python2.7/dist-packages/fenx/prepNutriPanelFromSSs.py
                ```

                4: Override selected label percentage values
                --------------------------------------------

                When printing nutritional panels the option now exists to override the calculated percentages which, as we've detailed, occasionally result in wrong values due to the specific implementation used.  To compensate, I've added the ability to override specific values when requesting the label to print.  The application prompt, which previously read:
                    LOF to quit or enter as ITEMNO<comma>QTY<space>ITEMNO<space><etc>:
                now reads:
                    LOF to quit or enter as ITEMNO[:nutrient=xx[:nutrient=xx]][,qty]:

                This allows you to respond with a command like:
                    006121:FAT_PERC=22:VITD_PER=13,2

                This command will print the nutritional label for item 006121 and will show the fat percentage as 22%, the vitamin D percentage as 13%, and will print 2 labels.

                You can still use the space to separate multiple items.  For example,
                    007205 006121 006121:FAT_PERC=22:VITD_PER=13,2 007205:POT_PER=4,2 007205 006121

                The above command will print item 007205, then 006121, then 2 copies each of both 006121 ahnd 007205 with the changed fat and vit_D percentages, and finally 007205 and 006121 again.  Note that percentage changes made to an item will persist while the application is still running (ie, until you LOF out), so the final two labels show the last overridden values entered during the run cycle.

                This should allow labels to be corrected until a more permanent automatic method can be integrated into the utility.

                Note: it is possible to set an override percent value that doesn't conform to the rounding rules that may on subsequent printing within the current run session result in the entered value being rounded.  For example, specifying 13% will print 13% the first pass through, but an immediate reprint will show 15% as the rounding rules specify that values in the 10-50 range be rounded to the nearest 5%.  To avoid this you should only specify valid conforming values as overrides.
                  """)
        doc = Document(test_doc)
        self.assertEqual(doc.to_html(), dedent("""\
                <h3>1: Start Nutritional Server</h3>

                <pre><code># ssh root@192.168.11.68
                # ps -efw|grep -i vbox
                ...
                root      4262  4247 12 Dec07 ?        14:33:22 /usr/lib/virtualbox/VBoxHeadless --comment Nutritional Server - Master --startvm ...
                ...</code></pre>

                <p>if not running,</p>

                <pre><code># fnx_start_nutritional_server</code></pre>

                <p>(This starts virtual machine 10.39, without a connection to your display)</p>

                <p>(For troubleshooting, remove --type headless and it will come up on your display)</p>

                <h3>2: Enable shared drive access to L:</h3>

                <p>VNC to 10.39 and verify L: is browsable (enter password probably) and then answer N</p>

                <p>the L: drive should be connected to 11.254/Labels using the standard password.</p>

                <h3>3: Print Nutritional Labels</h3>

                <p>To print nutritional labels, ssh to 11.16 and execute:</p>

                <pre><code>/usr/local/lib/python2.7/dist-packages/fenx/prepNutriPanelFromSSs.py</code></pre>

                <h3>4: Override selected label percentage values</h3>

                <p>When printing nutritional panels the option now exists to override the calculated percentages which, as we&apos;ve detailed, occasionally result in wrong values due to the specific implementation used.  To compensate, I&apos;ve added the ability to override specific values when requesting the label to print.  The application prompt, which previously read:</p>

                <pre><code>LOF to quit or enter as ITEMNO&lt;comma&gt;QTY&lt;space&gt;ITEMNO&lt;space&gt;&lt;etc&gt;:</code></pre>

                <p>now reads:</p>

                <pre><code>LOF to quit or enter as ITEMNO[:nutrient=xx[:nutrient=xx]][,qty]:</code></pre>

                <p>This allows you to respond with a command like:</p>

                <pre><code>006121:FAT_PERC=22:VITD_PER=13,2</code></pre>

                <p>This command will print the nutritional label for item 006121 and will show the fat percentage as 22%, the vitamin D percentage as 13%, and will print 2 labels.</p>

                <p>You can still use the space to separate multiple items.  For example,</p>

                <pre><code>007205 006121 006121:FAT_PERC=22:VITD_PER=13,2 007205:POT_PER=4,2 007205 006121</code></pre>

                <p>The above command will print item 007205, then 006121, then 2 copies each of both 006121 ahnd 007205 with the changed fat and vit_D percentages, and finally 007205 and 006121 again.  Note that percentage changes made to an item will persist while the application is still running (ie, until you LOF out), so the final two labels show the last overridden values entered during the run cycle.</p>

                <p>This should allow labels to be corrected until a more permanent automatic method can be integrated into the utility.</p>

                <p>Note: it is possible to set an override percent value that doesn&apos;t conform to the rounding rules that may on subsequent printing within the current run session result in the entered value being rounded.  For example, specifying 13% will print 13% the first pass through, but an immediate reprint will show 15% as the rounding rules specify that values in the 10-50 range be rounded to the nearest 5%.  To avoid this you should only specify valid conforming values as overrides.</p>
                """).strip(),
                # doc.to_html(),
                )

    def test_markers_split_across_lines(self):
        test_doc = dedent("""\
                From [Stackoverflow]:

                By default attachments are stored in the database, but you may choose to store
                them on the filesystem by setting a System Parameter (via //Settings > Technical
                \> Parameters > System Parameters//) named `ir_attachment.location`. In order
                to see this menu you need the `Technical Features` access right.

                This parameter should have the format: `protocol://URI`, and the only supported
                protocol by default is the local `file://`, for example `file:///filestore`.

                N.B. *The path for the `file://` protocol is taken relative to the OpenERP root
                path* (location of the OpenERP server), so with `ir_attachment.location` set to
                `file:///filestore` the attachments will be stored under `<openerp_path>/filestore`.

                The new system also uses a SHA1 hash to generate the filename, so that duplicate
                files don't take any space.

                In database mode the file content is stored in the `ir_attachment.db_datas column.
                In filestore mode the file name is stored in the ``ir_attachment.db_datas_fname` column.
                (The cryptic names are for backwards compatibility)

                ***Warning:***

                - *No automatic conversion mechanism exists between storage methods*.

                - When you set this parameter existing attachments remain stored in the
                  database, only new ones will be stored in the filesystem. The system
                  will try both locations so it's not a problem (first looking for
                  database storage, then filesystem storage).

                - If you remove this parameter you should manually store back the files
                  in the database because the system will only look in the database.

                [Stackoverflow]: http://stackoverflow.com/a/14960494/208880
                """)
        doc = Document(test_doc)
        self.assertEqual( doc.to_html(), dedent("""\
                <p>From <a href="http://stackoverflow.com/a/14960494/208880">Stackoverflow</a>:</p>

                <p>By default attachments are stored in the database, but you may choose to store them on the filesystem by setting a System Parameter (via //Settings &gt; Technical &gt; Parameters &gt; System Parameters//) named <code>ir_attachment.location</code>. In order to see this menu you need the <code>Technical Features</code> access right.</p>

                <p>This parameter should have the format: <code>protocol://URI</code>, and the only supported protocol by default is the local <code>file://</code>, for example <code>file:///filestore</code>.</p>

                <p>N.B. <i>The path for the <code>file://</code> protocol is taken relative to the OpenERP root path</i> (location of the OpenERP server), so with <code>ir_attachment.location</code> set to <code>file:///filestore</code> the attachments will be stored under <code>&lt;openerp_path&gt;/filestore</code>.</p>

                <p>The new system also uses a SHA1 hash to generate the filename, so that duplicate files don&apos;t take any space.</p>

                <p>In database mode the file content is stored in the <code>ir_attachment.db_datas column. In filestore mode the file name is stored in the </code><code>ir_attachment.db_datas_fname</code> column. (The cryptic names are for backwards compatibility)</p>

                <p><b><i>Warning:</i></b></p>

                <ul>
                <li><i>No automatic conversion mechanism exists between storage methods</i>.</li>
                <li>When you set this parameter existing attachments remain stored in the database, only new ones will be stored in the filesystem. The system will try both locations so it&apos;s not a problem (first looking for database storage, then filesystem storage).</li>
                <li>If you remove this parameter you should manually store back the files in the database because the system will only look in the database.</li>
                </ul>
                """).strip(),
                )

    def test_table(self):
        test_doc = dedent("""\
                | Version | Enum | "Fast Enum" | Global Enum |
                |-----|-----|-----|-----|
                | 3.9 | 2.31 | 0.80 | 0.40 |
                | 3.10 | 2.57 | 0.86 | 0.49 |
                | 3.11 | 7.22 | 0.70 | 0.21 |
                | 3.12 | 4.50 | 0.69 | 0.15 |
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Table])
        self.assertEqual( doc.to_html(), dedent("""\
                <table>
                    <thead>
                        <tr>
                            <th>Version</th>
                            <th>Enum</th>
                            <th>&quot;Fast Enum&quot;</th>
                            <th>Global Enum</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>3.9</td>
                            <td>2.31</td>
                            <td>0.80</td>
                            <td>0.40</td>
                        </tr>
                        <tr>
                            <td>3.10</td>
                            <td>2.57</td>
                            <td>0.86</td>
                            <td>0.49</td>
                        </tr>
                        <tr>
                            <td>3.11</td>
                            <td>7.22</td>
                            <td>0.70</td>
                            <td>0.21</td>
                        </tr>
                        <tr>
                            <td>3.12</td>
                            <td>4.50</td>
                            <td>0.69</td>
                            <td>0.15</td>
                        </tr>
                    </tbody>
                </table>
                """).strip(),
                doc.to_html(),
                )


    def test_detail(self):
        test_doc = dedent("""\
                --| - detail 1
                --| - detail 2
                --| - detail 3
                """)
        doc = Document(test_doc)
        self.assertEqual(doc.to_html().strip(), dedent("""\
                <details>
                <ul>
                <li>detail 1</li>
                <li>detail 2</li>
                <li>detail 3</li>
                </ul>
                </details>
                """).strip(),
                )

    def test_detail_summary(self):
        self.maxDiff = None
        test_doc = dedent("""\
                --> A Summary
                --| - detail 1
                --| - detail 2
                --| - detail 3
                """)
        doc = Document(test_doc)
        self.assertEqual(doc.to_html().strip(), dedent("""\
                <details>
                <summary>A Summary</summary>
                <ul>
                <li>detail 1</li>
                <li>detail 2</li>
                <li>detail 3</li>
                </ul>
                </details>
                """).strip(),
                )
        #
        test_doc = dedent("""\
                --> `A Summary`
                --| - detail 1
                --| - detail 2
                --| - detail 3
                """)
        doc = Document(test_doc)
        self.assertEqual(doc.to_html().strip(), dedent("""\
                <details>
                <summary><code>A Summary</code></summary>
                <ul>
                <li>detail 1</li>
                <li>detail 2</li>
                <li>detail 3</li>
                </ul>
                </details>
                """).strip(),
                )
        #
        test_doc = dedent("""\
                --> A Summary
                --| ```
                --| - detail 1
                --| - detail 2
                --| - detail 3
                --| ```
                """)
        doc = Document(test_doc)
        self.assertEqual(doc.to_html().strip(), dedent("""\
                <details>
                <summary>A Summary</summary>
                <pre><code>- detail 1
                - detail 2
                - detail 3</code></pre>
                </details>
                """).strip(),
                )
        #
        test_doc = dedent("""\
                --> `A Summary`
                --| ```
                --| - detail 1
                --| - detail 2
                --| - detail 3
                --| ```
                """)
        doc = Document(test_doc)
        self.assertEqual(doc.to_html().strip(), dedent("""\
                <details>
                <summary><code>A Summary</code></summary>
                <pre><code>- detail 1
                - detail 2
                - detail 3</code></pre>
                </details>
                """).strip(),
                )

        test_doc = dedent("""\
                crontab output
                ==============

                error output
                ------------

                --> `/usr/local/bin/fetch_pdf_scans`
                --| ```
                --| user=mamador;host=192.168.11.96;dir=/home/autoscan
                --|
                --| 20220819-222401
                --| Permission denied, please try again.
                --| Permission denied, please try again.
                --| Permission denied (publickey,password).
                --| rsync: connection unexpectedly closed (0 bytes received so far) [Receiver=3.1.1]
                --| rsync error: unexplained error (code 255) at io.c(226) [Receiver=3.1.1]
                --| ```
                """)
        doc = Document(test_doc)
        self.assertEqual(dedent(doc.to_html()).strip(), dedent("""\
                <h2>crontab output</h2>

                <h3>error output</h3>


                <details>
                <summary><code>/usr/local/bin/fetch_pdf_scans</code></summary>
                <pre><code>user=mamador;host=192.168.11.96;dir=/home/autoscan

                20220819-222401
                Permission denied, please try again.
                Permission denied, please try again.
                Permission denied (publickey,password).
                rsync: connection unexpectedly closed (0 bytes received so far) [Receiver=3.1.1]
                rsync error: unexplained error (code 255) at io.c(226) [Receiver=3.1.1]</code></pre>
                </details>
                """).strip(),
                )

    def test_link_href_not_escaped(self):
        test_doc = dedent("""\
                [ <main_file>.py ]
                """)
        doc = Document(test_doc)
        self.assertEqual(dedent(doc.to_html()).strip(), dedent("""\
                <p><a href="<main_file>.py">&lt;main_file&gt;.py</a></p>
                """).strip())

    def test_multiple_lists(self):
        test_doc = dedent("""\
                - 192.168.11.x  traditional pajaro network.  labeltime accepts connections from this network

                + 192.168.8-11.x expanded pajaro network.
                + /21 netmask, aka 255.255.248.0.
                + printers are moved to 192.168.10.x generally, and cameras to 192.168.8.x.  workstation can talk to devices on this network

                * 192.168.1.x north bay network.  openvpn to 192.168.11.254
                """)
        doc = Document(test_doc)
        self.assertEqual(doc.to_html().strip(), dedent("""\
                <ul>
                <li>192.168.11.x  traditional pajaro network.  labeltime accepts connections from this network</li>
                </ul>

                <ul>
                <li>192.168.8-11.x expanded pajaro network.</li>
                <li>/21 netmask, aka 255.255.248.0.</li>
                <li>printers are moved to 192.168.10.x generally, and cameras to 192.168.8.x.  workstation can talk to devices on this network</li>
                </ul>

                <ul>
                <li>192.168.1.x north bay network.  openvpn to 192.168.11.254</li>
                </ul>
                """).strip())

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

main()
