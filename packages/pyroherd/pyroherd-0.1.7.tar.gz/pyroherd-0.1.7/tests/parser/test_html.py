<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> c723d0e (update)
#  Pyroherd - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present OnTheHerd <https://github.com/OnTheHerd>
#
#  This file is part of Pyroherd.
#
#  Pyroherd is free software: you can redistribute it and/or modify
<<<<<<< HEAD
=======
=======
#  Pyroherd - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyroherd.
#
#  Pyroherd is free software: you can redistribute it and/or modify
>>>>>>> 47ad949 (update)
>>>>>>> c723d0e (update)
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
<<<<<<< HEAD
#  Pyroherd is distributed in the hope that it will be useful,
=======
<<<<<<< HEAD
#  Pyroherd is distributed in the hope that it will be useful,
=======
#  Pyroherd is distributed in the hope that it will be useful,
>>>>>>> 47ad949 (update)
>>>>>>> c723d0e (update)
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> c723d0e (update)
#  along with Pyroherd.  If not, see <http://www.gnu.org/licenses/>.

import pyroherd
from pyroherd.parser.html import HTML
<<<<<<< HEAD
=======
=======
#  along with Pyroherd.  If not, see <http://www.gnu.org/licenses/>.

import pyroherd
from pyroherd.parser.html import HTML
>>>>>>> 47ad949 (update)
>>>>>>> c723d0e (update)


# expected: the expected unparsed HTML
# text: original text without entities
# entities: message entities coming from the server

def test_html_unparse_bold():
    expected = "<b>bold</b>"
    text = "bold"
<<<<<<< HEAD
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.BOLD, offset=0, length=4)])
=======
<<<<<<< HEAD
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.BOLD, offset=0, length=4)])
=======
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.BOLD, offset=0, length=4)])
>>>>>>> 47ad949 (update)
>>>>>>> c723d0e (update)

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_italic():
    expected = "<i>italic</i>"
    text = "italic"
<<<<<<< HEAD
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.ITALIC, offset=0, length=6)])
=======
<<<<<<< HEAD
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.ITALIC, offset=0, length=6)])
=======
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.ITALIC, offset=0, length=6)])
>>>>>>> 47ad949 (update)
>>>>>>> c723d0e (update)

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_underline():
    expected = "<u>underline</u>"
    text = "underline"
<<<<<<< HEAD
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.UNDERLINE, offset=0, length=9)])
=======
<<<<<<< HEAD
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.UNDERLINE, offset=0, length=9)])
=======
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.UNDERLINE, offset=0, length=9)])
>>>>>>> 47ad949 (update)
>>>>>>> c723d0e (update)

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_strike():
    expected = "<s>strike</s>"
    text = "strike"
<<<<<<< HEAD
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.STRIKETHROUGH, offset=0, length=6)])
=======
<<<<<<< HEAD
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.STRIKETHROUGH, offset=0, length=6)])
=======
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.STRIKETHROUGH, offset=0, length=6)])
>>>>>>> 47ad949 (update)
>>>>>>> c723d0e (update)

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_spoiler():
    expected = "<spoiler>spoiler</spoiler>"
    text = "spoiler"
<<<<<<< HEAD
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.SPOILER, offset=0, length=7)])
=======
<<<<<<< HEAD
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.SPOILER, offset=0, length=7)])
=======
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.SPOILER, offset=0, length=7)])
>>>>>>> 47ad949 (update)
>>>>>>> c723d0e (update)

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_url():
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> c723d0e (update)
    expected = '<a href="https://pyroherd.org/">URL</a>'
    text = "URL"
    entities = pyroherd.types.List([pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.TEXT_LINK,
                                                                 offset=0, length=3, url='https://pyroherd.org/')])
<<<<<<< HEAD
=======
=======
    expected = '<a href="https://pyroherd.org/">URL</a>'
    text = "URL"
    entities = pyroherd.types.List([pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.TEXT_LINK,
                                                                 offset=0, length=3, url='https://pyroherd.org/')])
>>>>>>> 47ad949 (update)
>>>>>>> c723d0e (update)

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_code():
    expected = '<code>code</code>'
    text = "code"
<<<<<<< HEAD
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.CODE, offset=0, length=4)])
=======
<<<<<<< HEAD
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.CODE, offset=0, length=4)])
=======
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.CODE, offset=0, length=4)])
>>>>>>> 47ad949 (update)
>>>>>>> c723d0e (update)

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_pre():
    expected = """<pre language="python">for i in range(10):
    print(i)</pre>"""

    text = """for i in range(10):
    print(i)"""

<<<<<<< HEAD
    entities = pyroherd.types.List([pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.PRE, offset=0,
=======
<<<<<<< HEAD
    entities = pyroherd.types.List([pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.PRE, offset=0,
=======
    entities = pyroherd.types.List([pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.PRE, offset=0,
>>>>>>> 47ad949 (update)
>>>>>>> c723d0e (update)
                                                                 length=32, language='python')])

    assert HTML.unparse(text=text, entities=entities) == expected


<<<<<<< HEAD
=======
<<<<<<< HEAD
=======
def test_html_unparse_blockquote():
    expected = """<blockquote>Quote text</blockquote>
    from pyroherd"""

    text = """Quote text
    from pyroherd"""

    entities = pyroherd.types.List([pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.BLOCKQUOTE, offset=0,
                                                                 length=10)])

    assert HTML.unparse(text=text, entities=entities) == expected


>>>>>>> 47ad949 (update)
>>>>>>> c723d0e (update)
def test_html_unparse_mixed():
    expected = "<b>aaaaaaa<i>aaa<u>bbbb</u></i></b><u><i>bbbbbbccc</i></u><u>ccccccc<s>ddd</s></u><s>ddddd<spoiler>dd" \
               "eee</spoiler></s><spoiler>eeeeeeefff</spoiler>ffff<code>fffggggggg</code>ggghhhhhhhhhh"
    text = "aaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeeeffffffffffgggggggggghhhhhhhhhh"
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> c723d0e (update)
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.BOLD, offset=0, length=14),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.ITALIC, offset=7, length=7),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.UNDERLINE, offset=10, length=4),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.UNDERLINE, offset=14, length=9),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.ITALIC, offset=14, length=9),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.UNDERLINE, offset=23, length=10),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.STRIKETHROUGH, offset=30, length=3),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.STRIKETHROUGH, offset=33, length=10),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.SPOILER, offset=38, length=5),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.SPOILER, offset=43, length=10),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.CODE, offset=57, length=10)])
<<<<<<< HEAD
=======
=======
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.BOLD, offset=0, length=14),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.ITALIC, offset=7, length=7),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.UNDERLINE, offset=10, length=4),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.UNDERLINE, offset=14, length=9),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.ITALIC, offset=14, length=9),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.UNDERLINE, offset=23, length=10),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.STRIKETHROUGH, offset=30, length=3),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.STRIKETHROUGH, offset=33, length=10),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.SPOILER, offset=38, length=5),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.SPOILER, offset=43, length=10),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.CODE, offset=57, length=10)])
>>>>>>> 47ad949 (update)
>>>>>>> c723d0e (update)

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_escaped():
    expected = "<b>&lt;b&gt;bold&lt;/b&gt;</b>"
    text = "<b>bold</b>"
<<<<<<< HEAD
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.BOLD, offset=0, length=11)])
=======
<<<<<<< HEAD
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.BOLD, offset=0, length=11)])
=======
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.BOLD, offset=0, length=11)])
>>>>>>> 47ad949 (update)
>>>>>>> c723d0e (update)

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_escaped_nested():
    expected = "<b>&lt;b&gt;bold <u>&lt;u&gt;underline&lt;/u&gt;</u> bold&lt;/b&gt;</b>"
    text = "<b>bold <u>underline</u> bold</b>"
<<<<<<< HEAD
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.BOLD, offset=0, length=33),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.UNDERLINE, offset=8, length=16)])
=======
<<<<<<< HEAD
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.BOLD, offset=0, length=33),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.UNDERLINE, offset=8, length=16)])
=======
    entities = pyroherd.types.List(
        [pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.BOLD, offset=0, length=33),
         pyroherd.types.MessageEntity(type=pyroherd.enums.MessageEntityType.UNDERLINE, offset=8, length=16)])
>>>>>>> 47ad949 (update)
>>>>>>> c723d0e (update)

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_no_entities():
    expected = "text"
    text = "text"
    entities = []

    assert HTML.unparse(text=text, entities=entities) == expected
