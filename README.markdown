<h1 align="center"><i>✨ pyip2region ✨ </i></h1>

<h3 align="center">The python binding for <a href="https://github.com/lionsoul2014/ip2region">ip2region</a> </h3>


[![pypi](https://img.shields.io/pypi/v/ip2region.svg)](https://pypi.org/project/ip2region/)
![python](https://img.shields.io/pypi/pyversions/ip2region)
![implementation](https://img.shields.io/pypi/implementation/ip2region)
![wheel](https://img.shields.io/pypi/wheel/ip2region)
![license](https://img.shields.io/github/license/synodriver/pyip2region.svg)
![action](https://img.shields.io/github/workflow/status/synodriver/pyip2region/build%20wheel)


### 使用方式

### 完全基于文件的查询

```python
from ip2region import Searcher, VectorIndex, Header, Version
header = Header.from_file(r".\ip2region_v6.xdb")
version = Version.from_header(header)
# 备注：并发使用，每一个线程需要单独定义并且初始化一个 searcher 查询对象，或者加锁
searcher = Searcher.from_file(version, r"E:\pyproject\pyip2region\tests\ip2region_v6.xdb")
result = searcher.search_by_string("2001:0:2851:b9f0:3866:13a2:846f:c23b")
print(result)
```

### 缓存 `VectorIndex` 索引
```python
from ip2region import Searcher, VectorIndex, Header, Version
header = Header.from_file(r".\ip2region_v4.xdb")
version = Version.from_header(header)
index = VectorIndex.from_file(r".\ip2region_v4.xdb")
searcher = Searcher.from_index(version, r".\ip2region_v4.xdb", index)
result = searcher.search_by_string("1.1.1.1")
print(result)
```

### 缓存整个 `xdb` 数据

```python
from ip2region import Searcher, VectorIndex, Header, Version

header = Header.from_file(r".\ip2region_v4.xdb")
version = Version.from_header(header)
with open(r".\ip2region_v4.xdb", "rb") as f:
    data = f.read()
searcher = Searcher.from_buffer(version, data)
result = searcher.search_by_string("1.1.1.1")
print(result)
```

### 注意：
多线程模式下，只有纯内存的才是线程安全的，其他都需要用户自己加锁加锁，程序中没有任何机制保证线程安全