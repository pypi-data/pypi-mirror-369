#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import unittest

from waflibs import text

TIMES = 55


class TestText(unittest.TestCase):
    pass


class TestDivider(TestText):
    def test_divider_default(self):
        self.assertEqual(text.divider(), "=" * TIMES)

    def test_divider_char(self):
        self.assertEqual(text.divider(char="-"), "-" * TIMES)

    def test_divider_times(self):
        times = 8

        self.assertEqual(text.divider(times=times), "=" * times)

    def test_divider_all(self):
        times = 9

        self.assertEqual(text.divider(char="_", times=times), "_" * times)


if __name__ == "__main__":
    unittest.main()
