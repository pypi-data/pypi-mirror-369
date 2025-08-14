import unittest
from html2term.core import convert

class TestHtml2Term(unittest.TestCase):

    def test_simple_styles(self):
        self.assertEqual(convert("<b>bold</b>"), "\033[1mbold\033[0m\033[0m")
        self.assertEqual(convert("<i>italic</i>"), "\033[3mitalic\033[0m\033[0m")
        self.assertEqual(convert("<u>underline</u>"), "\033[4munderline\033[0m\033[0m")
        self.assertEqual(convert("<strike>strike</strike>"), "\033[9mstrike\033[0m\033[0m")
        self.assertEqual(convert("<blink>blink</blink>"), "\033[5mblink\033[0m\033[0m")

    def test_semantic_tags(self):
        self.assertEqual(convert("<strong>strong</strong>"), "\033[1mstrong\033[0m\033[0m")
        self.assertEqual(convert("<em>emphasis</em>"), "\033[3memphasis\033[0m\033[0m")

    def test_standard_colors(self):
        self.assertEqual(convert("<red>hello</red>"), "\033[31mhello\033[0m\033[0m")
        self.assertEqual(convert("<bg-green>world</bg-green>"), "\033[42mworld\033[0m\033[0m")

    def test_hex_colors(self):
        self.assertEqual(convert("<#ff0000>Red Text</#ff0000>"), "\033[38;2;255;0;0mRed Text\033[0m\033[0m")
        self.assertEqual(convert("<bg-#00ff00>Green BG</bg-#00ff00>"), "\033[48;2;0;255;0mGreen BG\033[0m\033[0m")
        self.assertEqual(convert("<#ABCDEF>Hex</#ABCDEF>"), "\033[38;2;171;205;239mHex\033[0m\033[0m")

    def test_layout_tags(self):
        self.assertEqual(convert("line 1<br>line 2"), "line 1\nline 2\033[0m")
        self.assertEqual(convert("line 1<br/>line 2"), "line 1\nline 2\033[0m")
        self.assertEqual(convert("line 1<br />line 2"), "line 1\nline 2\033[0m")
        self.assertEqual(convert("col1<tab/>col2"), "col1\tcol2\033[0m")

    def test_nested_tags(self):
        expected = "\033[1m\033[31mBold and Red\033[0m\033[1m just bold\033[0m\033[0m"
        self.assertEqual(convert("<b><red>Bold and Red</red> just bold</b>"), expected)
        expected = "\033[48;2;0;0;255m\033[38;2;255;255;0mYellow on Blue\033[0m\033[48;2;0;0;255m just blue bg\033[0m\033[0m"
        self.assertEqual(
            convert("<bg-#0000ff><#ffff00>Yellow on Blue</#ffff00> just blue bg</bg-#0000ff>"),
            expected
        )

    def test_unclosed_tags(self):
        self.assertEqual(convert("<b>unclosed bold"), "\033[1munclosed bold\033[0m")
        self.assertEqual(convert("<b><red>unclosed red"), "\033[1m\033[31munclosed red\033[0m")

    def test_malformed_tags(self):
        self.assertEqual(convert("<notatag>text</notatag>"), "<notatag>text</notatag>\033[0m")
        self.assertEqual(convert("text with < open tag"), "text with < open tag\033[0m")
        self.assertEqual(convert("<#12345>invalid hex</#12345>"), "<#12345>invalid hex</#12345>\033[0m")

    def test_complex_string(self):
        markup = "<b>Welcome to <green>html2term</green>!</b><br/>" \
                 "It supports <i><#ff7f50>nested</#ff7f50> and <bg-cyan>colored</bg-cyan></i> tags."
        expected = "\033[1mWelcome to \033[32mhtml2term\033[0m\033[1m!\033[0m\n" \
                   "It supports \033[3m\033[38;2;255;127;80mnested\033[0m\033[3m and \033[46mcolored\033[0m\033[3m\033[0m tags.\033[0m"
        self.assertEqual(convert(markup), expected)

if __name__ == '__main__':
    unittest.main()
