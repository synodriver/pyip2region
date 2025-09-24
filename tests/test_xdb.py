"""
Copyright (c) 2008-2022 synodriver <synodriver@gmail.com>
"""
from unittest import TestCase
from concurrent.futures import ThreadPoolExecutor, wait
# import os
# os.environ["IP_USE_CFFI"] = "1"

from ip2region import Searcher, VectorIndex, init_winsock, clean_winsock, Header, Version, parse_ip


class TestXdb(TestCase):
    def setUp(self):
        init_winsock()
    
    def tearDown(self):
        clean_winsock()

    def test_search_by_string_v6(self):
        header = Header.from_file(r"E:\pyproject\pyip2region\tests\ip2region_v6.xdb")
        version = Version.from_header(header)

        searcher = Searcher.from_file(version, r"E:\pyproject\pyip2region\tests\ip2region_v6.xdb")
        result = searcher.search_by_string("2001:0:2851:b9f0:3866:13a2:846f:c23b")
        version, buf = parse_ip("2001:0:2851:b9f0:3866:13a2:846f:c23b")
        ret = searcher.search(buf)
        self.assertEqual(result, '美国|加利福尼亚州|洛杉矶|专线用户')
        
    def test_search_by_string_v6_into(self):
        header = Header.from_file(r"E:\pyproject\pyip2region\tests\ip2region_v6.xdb")
        version = Version.from_header(header)

        searcher = Searcher.from_file(version, r"E:\pyproject\pyip2region\tests\ip2region_v6.xdb")
        result = searcher.search_by_string("2001:0:2851:b9f0:3866:13a2:846f:c23b")
        version, buf = parse_ip("2001:0:2851:b9f0:3866:13a2:846f:c23b")
        region_buf = bytearray(100)
        ret = searcher.search_into(buf, region_buf)
        self.assertEqual(region_buf.decode()[:18], '美国|加利福尼亚州|洛杉矶|专线用户')
    
    def test_search_by_string(self):
        header = Header.from_file(r"E:\pyproject\pyip2region\tests\ip2region_v4.xdb")
        version = Version.from_header(header)
        
        searcher = Searcher.from_file(version, r"E:\pyproject\pyip2region\tests\ip2region_v4.xdb")
        result = searcher.search_by_string("1.1.1.1")
        self.assertEqual(result, '澳大利亚|0|0|0')

    def test_search_by_string_into(self):
        header = Header.from_file(r"E:\pyproject\pyip2region\tests\ip2region_v4.xdb")
        version = Version.from_header(header)
        searcher = Searcher.from_file( version, r"E:\pyproject\pyip2region\tests\ip2region_v4.xdb")
        buffer = bytearray(100)
        searcher.search_by_string_into("1.1.1.1", buffer)
        self.assertEqual(buffer.decode()[:10], '澳大利亚|0|0|0')

    def test_index(self):
        header = Header.from_file(r"E:\pyproject\pyip2region\tests\ip2region_v4.xdb")
        version = Version.from_header(header)
        index = VectorIndex.from_file(r"E:\pyproject\pyip2region\tests\ip2region_v4.xdb")
        searcher = Searcher.from_index(version, r"E:\pyproject\pyip2region\tests\ip2region_v4.xdb", index)
        result = searcher.search_by_string("1.1.1.1")
        self.assertEqual(result, '澳大利亚|0|0|0')

    def test_buffer(self):
        header = Header.from_file(r"E:\pyproject\pyip2region\tests\ip2region_v4.xdb")
        version = Version.from_header(header)
        with open(r"E:\pyproject\pyip2region\tests\ip2region_v4.xdb", "rb") as f:
            data = f.read()
        searcher = Searcher.from_buffer(version, data)
        result = searcher.search_by_string("1.1.1.1")
        self.assertEqual(result, '澳大利亚|0|0|0')
        
    def test_thread(self):
        header = Header.from_file(r"E:\pyproject\pyip2region\tests\ip2region_v4.xdb")
        version = Version.from_header(header)
        with open(r"E:\pyproject\pyip2region\tests\ip2region_v4.xdb", "rb") as f:
            data = f.read()
        searcher = Searcher.from_buffer(version, data)
        def worker():
            result = searcher.search_by_string("1.1.1.1")
            self.assertEqual(result, '澳大利亚|0|0|0')
        futs = []
        with ThreadPoolExecutor(max_workers=32) as executor:
            for i in range(1000000):
                futs.append(executor.submit(worker))
            wait(futs)
            


if __name__ == "__main__":
    import unittest

    unittest.main()
