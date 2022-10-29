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
from ip2region import Searcher, VectorIndex
# 备注：并发使用，每一个线程需要单独定义并且初始化一个 searcher 查询对象，或者加锁
searcher = Searcher.from_file("F:\pyproject\ip2region\dep\data\ip2region.xdb")
result = searcher.search_by_string("1.1.1.1")
print(result.decode)
```

### 缓存 `VectorIndex` 索引
```python
from ip2region import Searcher, VectorIndex

index = VectorIndex.from_file("F:\pyproject\ip2region\dep\data\ip2region.xdb")
searcher = Searcher.from_index("F:\pyproject\ip2region\dep\data\ip2region.xdb", index)
result = searcher.search_by_string("1.1.1.1")
print(result.decode)
```

### 缓存整个 `xdb` 数据

```python
from ip2region import Searcher, VectorIndex

with open("F:\pyproject\ip2region\dep\data\ip2region.xdb", "rb") as f:
    data = f.read()
searcher = Searcher.from_buffer(data)
result = searcher.search_by_string("1.1.1.1")
print(result.decode)
```