"""
Copyright (c) 2008-2022 synodriver <synodriver@gmail.com>
"""
from unittest import TestCase
# import os
# os.environ["IP_USE_CFFI"] = "1"

from ip2region import Searcher, VectorIndex


class TestXdb(TestCase):
    def test_search_by_string(self):
        searcher = Searcher.from_file("F:\pyproject\ip2region\dep\data\ip2region.xdb")
        result = searcher.search_by_string("1.1.1.1")
        self.assertEqual(result.decode(), '澳大利亚|0|0|0|0')

    def test_search_by_string_into(self):
        searcher = Searcher.from_file("F:\pyproject\ip2region\dep\data\ip2region.xdb")
        buffer = bytearray(1000)
        searcher.search_by_string_into("1.1.1.1", buffer)
        self.assertEqual(buffer[:20], b'\xe6\xbe\xb3\xe5\xa4\xa7\xe5\x88\xa9\xe4\xba\x9a|0|0|0|0')

    def test_index(self):
        index = VectorIndex.from_file("F:\pyproject\ip2region\dep\data\ip2region.xdb")
        searcher = Searcher.from_index("F:\pyproject\ip2region\dep\data\ip2region.xdb", index)
        result = searcher.search_by_string("1.1.1.1")
        self.assertEqual(result.decode(), '澳大利亚|0|0|0|0')

    def test_buffer(self):
        with open("F:\pyproject\ip2region\dep\data\ip2region.xdb", "rb") as f:
            data = f.read()
        searcher = Searcher.from_buffer(data)
        result = searcher.search_by_string("1.1.1.1")
        self.assertEqual(result.decode(), '澳大利亚|0|0|0|0')


if __name__ == "__main__":
    import unittest

    unittest.main()
