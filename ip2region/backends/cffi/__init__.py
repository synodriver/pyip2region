"""
Copyright (c) 2008-2022 synodriver <synodriver@gmail.com>
"""
from pathlib import Path

from ip2region.backends.cffi._xdb import ffi, lib


def ensure_bytes(inp: object) -> bytes:
    if isinstance(inp, str):
        return inp.encode()
    elif isinstance(inp, bytes):
        return inp
    elif isinstance(inp, Path):
        return str(inp).encode()
    else:
        return bytes(inp)


class VectorIndex:
    # cdef xdb_vector_index_t *index

    @staticmethod
    def from_file(db_path):
        self = VectorIndex()
        db_path_b: bytes = ensure_bytes(db_path)
        self.index = lib.xdb_load_vector_index_from_file(ffi.from_buffer(db_path_b))
        if self.index == ffi.NULL:
            raise RuntimeError("fail to create VectorIndex")
        return self

    def __del__(self):
        lib.xdb_close_vector_index(self.index)


class Searcher:
    # cdef:
    #     xdb_searcher_t searcher
    #     xdb_content_t buf  # pointer to pybuffer
    #     const uint8_t[::1] pybuffer

    @staticmethod
    def from_file(db_path: object):
        self: "Searcher" = Searcher()
        self.searcher = ffi.new("xdb_searcher_t *")
        db_path_b: bytes = ensure_bytes(db_path)
        err = lib.xdb_new_with_file_only(self.searcher, ffi.from_buffer(db_path_b))
        if err != 0:
            raise RuntimeError(
                "failed to create xdb searcher from `%s` with errno=%d" % (db_path, err)
            )
        return self

    @staticmethod
    def from_index(db_path: object, index: VectorIndex):
        self: "Searcher" = Searcher()
        self.searcher = ffi.new("xdb_searcher_t *")
        self.index = index
        db_path_b: bytes = ensure_bytes(db_path)
        err = lib.xdb_new_with_vector_index(
            self.searcher, ffi.from_buffer(db_path_b), index.index
        )
        if err != 0:
            raise RuntimeError(
                "failed to create vector index cached searcher with path=%s, errcode=%d"
                % (db_path, err)
            )
        return self

    @staticmethod
    def from_buffer(buffer: bytes):
        self: "Searcher" = Searcher()
        self.searcher = ffi.new("xdb_searcher_t *")
        self.pybuffer = buffer  # hold a ref
        self.buf = ffi.new("xdb_content_t*")
        self.buf.length = len(buffer)
        self.buf.buffer = ffi.cast("char*", ffi.from_buffer(buffer))
        err = lib.xdb_new_with_buffer(self.searcher, self.buf)
        if err != 0:
            raise RuntimeError("failed to create xdb searcher from buffer")
        return self

    def search_by_string(self, ip: object, size: int = 1000) -> bytes:
        region_buffer = ffi.new(f"char[{size}]")
        ip_b = ensure_bytes(ip)
        err = lib.xdb_search_by_string(
            self.searcher, ffi.from_buffer(ip_b), region_buffer, size
        )
        if err != 0:
            raise RuntimeError("failed search(%s) with errno=%d" % (ip, err))
        return ffi.string(region_buffer)

    def search_by_string_into(self, ip: object, region_buffer: bytearray):
        ip_b: bytes = ensure_bytes(ip)
        err = lib.xdb_search_by_string(
            self.searcher,
            ffi.from_buffer(ip_b),
            ffi.from_buffer(region_buffer),
            len(region_buffer),
        )
        if err != 0:
            raise RuntimeError("failed search(%s) with errno=%d" % (ip, err))

    def search(self, ip: int, size: int = 1000) -> bytes:
        region_buffer = ffi.new(f"char[{size}]")
        err = lib.xdb_search(self.searcher, ip, region_buffer, size)
        if err != 0:
            raise RuntimeError("failed search(%d) with errno=%d" % (ip, err))
        return ffi.string(region_buffer)

    def search_into(self, ip: int, region_buffer: bytearray):
        err = lib.xdb_search(
            self.searcher, ip, ffi.from_buffer(region_buffer), len(region_buffer)
        )
        if err != 0:
            raise RuntimeError("failed search(%s) with errno=%d" % (ip, err))

    def get_io_count(self) -> int:
        return lib.xdb_get_io_count(self.searcher)

    def __del__(self):
        lib.xdb_close(self.searcher)
