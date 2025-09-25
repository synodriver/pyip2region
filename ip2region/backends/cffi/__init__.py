"""
Copyright (c) 2008-2022 synodriver <synodriver@gmail.com>
"""

# todo port cython to cffi
from pathlib import Path

from ip2region.backends.cffi._xdb import ffi, lib

xdb_structure_20 = lib.xdb_structure_20
xdb_structure_30 = lib.xdb_structure_30
xdb_header_info_length = lib.xdb_header_info_length
xdb_vector_index_rows = lib.xdb_vector_index_rows
xdb_vector_index_cols = lib.xdb_vector_index_cols
xdb_vector_index_size = lib.xdb_vector_index_size
xdb_v4_index_size = lib.xdb_v4_index_size
xdb_v6_index_size = lib.xdb_v6_index_size
xdb_ipv4_id = lib.xdb_ipv4_id
xdb_ipv6_id = lib.xdb_ipv6_id
xdb_ipv4_bytes = lib.xdb_ipv4_bytes
xdb_ipv6_bytes = lib.xdb_ipv6_bytes
xdb_vector_index_length = lib.xdb_vector_index_length
xdb_region_buffer_wrapper = lib.xdb_region_buffer_wrapper
xdb_region_buffer_auto = lib.xdb_region_buffer_auto


def ensure_bytes(inp: object) -> bytes:
    if isinstance(inp, str):
        return inp.encode()
    elif isinstance(inp, bytes):
        return inp
    elif isinstance(inp, Path):
        return str(inp).encode()
    else:
        return bytes(inp)


class Header:
    # cdef:
    #     lib.xdb_header_t * header
    #     Py_ssize_t[1] shape
    #     Py_ssize_t[1] strides

    @staticmethod
    def from_file(db_path: object) -> "Header":
        self = Header.__new__(Header)
        db_path_b = ensure_bytes(db_path)
        self.header = lib.xdb_load_header_from_file(ffi.cast("const char*", db_path_b))
        if self.header == ffi.NULL:
            raise RuntimeError(f"failed to load header from {db_path}")
        return self

    @property
    def version(self):
        return self.header.version

    @version.setter
    def version(self, value: int):
        self.header.version = value

    @property
    def index_policy(self):
        return self.header.index_policy

    @index_policy.setter
    def index_policy(self, value: int):
        self.header.index_policy = value

    @property
    def created_at(self):
        return self.header.created_at

    @created_at.setter
    def created_at(self, value: int):
        self.header.created_at = value

    @property
    def start_index_ptr(self):
        return self.header.start_index_ptr

    @start_index_ptr.setter
    def start_index_ptr(self, value: int):
        self.header.start_index_ptr = value

    @property
    def end_index_ptr(self):
        return self.header.end_index_ptr

    @end_index_ptr.setter
    def end_index_ptr(self, value: int):
        self.header.end_index_ptr = value

    @property
    def ip_version(self):
        return self.header.ip_version

    @ip_version.setter
    def ip_version(self, value: int):
        self.header.ip_version = value

    @property
    def runtime_ptr_bytes(self):
        return self.header.runtime_ptr_bytes

    @runtime_ptr_bytes.setter
    def runtime_ptr_bytes(self, value: int):
        self.header.runtime_ptr_bytes = value

    def getbuffer(self):
        return ffi.buffer(self.header.buffer, self.header.length)

    # def __getbuffer__(self, Py_buffer *buffer, int flags):
    #     cdef Py_ssize_t itemsize = sizeof(char)
    #     self.strides[0] = itemsize
    #     self.shape[0] = self.header.length
    #
    #     buffer.buf = <char *>self.header.buffer
    #     buffer.format = 'B'  # bytes
    #     buffer.internal = NULL  # see References
    #     buffer.itemsize = itemsize
    #     buffer.len =  self.header.length * itemsize  # product(shape) * itemsize
    #     buffer.ndim = 1
    #     buffer.obj = self
    #     buffer.readonly = 0
    #     buffer.shape = self.shape
    #     buffer.strides = self.strides
    #     buffer.suboffsets = NULL  # for pointer arrays only

    # def __releasebuffer__(self, Py_buffer *buffer):
    #     ...

    def __del__(self):
        if self.header != ffi.NULL:
            lib.xdb_free_header(self.header)


class VectorIndex:
    # cdef:
    #     lib.xdb_vector_index_t *index
    #     Py_ssize_t[1] shape
    #     Py_ssize_t[1] strides

    @staticmethod
    def from_file(db_path: object) -> "VectorIndex":
        self = VectorIndex.__new__(VectorIndex)
        db_path_b = ensure_bytes(db_path)
        self.index = lib.xdb_load_vector_index_from_file(
            ffi.cast("const char*", db_path_b)
        )
        if self.index == ffi.NULL:
            raise RuntimeError(f"failed to load vector index from {db_path}")
        return self

    def getbuffer(self):
        return ffi.buffer(self.index.buffer, self.index.length)

    # def __getbuffer__(self, Py_buffer *buffer, int flags):
    #     cdef Py_ssize_t itemsize = sizeof(char)
    #     self.strides[0] = itemsize
    #     self.shape[0] = self.index.length
    #
    #     buffer.buf = <char *>self.index.buffer
    #     buffer.format = 'B'  # bytes
    #     buffer.internal = NULL  # see References
    #     buffer.itemsize = itemsize
    #     buffer.len =  self.index.length * itemsize  # product(shape) * itemsize
    #     buffer.ndim = 1
    #     buffer.obj = self
    #     buffer.readonly = 0
    #     buffer.shape = self.shape
    #     buffer.strides = self.strides
    #     buffer.suboffsets = NULL  # for pointer arrays only

    def __del__(self):
        if self.index != ffi.NULL:
            lib.xdb_free_vector_index(self.index)


class Content:
    # cdef:
    #     lib.xdb_content_t *content
    #     Py_ssize_t[1] shape
    #     Py_ssize_t[1] strides

    @staticmethod
    def from_file(db_path: object):
        self = Content.__new__(Content)
        db_path_b = ensure_bytes(db_path)
        self.content = lib.xdb_load_content_from_file(
            ffi.cast("const char*", db_path_b)
        )
        if self.content == ffi.NULL:
            raise RuntimeError(f"failed to load xdb content from {db_path}")
        return self

    def getbuffer(self):
        return ffi.buffer(self.content.buffer, self.content.length)

    # def __getbuffer__(self, Py_buffer *buffer, int flags):
    #     cdef Py_ssize_t itemsize = sizeof(char)
    #     self.strides[0] = itemsize
    #     self.shape[0] = self.content.length
    #
    #     buffer.buf = self.content.buffer
    #     buffer.format = 'B'  # bytes
    #     buffer.internal = NULL  # see References
    #     buffer.itemsize = itemsize
    #     buffer.len =  self.content.length * itemsize  # product(shape) * itemsize
    #     buffer.ndim = 1
    #     buffer.obj = self
    #     buffer.readonly = 0
    #     buffer.shape = self.shape
    #     buffer.strides = self.strides
    #     buffer.suboffsets = NULL  # for pointer arrays only

    def __del__(self):
        if self.content != ffi.NULL:
            lib.xdb_free_content(self.content)


def verify(db_path: object) -> int:
    db_path_b = ensure_bytes(db_path)
    db_path_ptr = ffi.case("const char*", db_path_b)
    ret = lib.xdb_verify_from_file(db_path_ptr)
    if ret != 0:
        raise RuntimeError(f"failed to verify xdb file {db_path} with errno={ret}")
    return ret


def verify_from_header(db_path: object, header: Header) -> int:
    db_path_b = ensure_bytes(db_path)
    db_path_ptr = ffi.case("const char*", db_path_b)
    handle = lib.fopen(db_path_ptr, "rb")
    if handle == ffi.NULL:
        raise RuntimeError(f"failed to open {db_path}")
    ret = lib.xdb_verify_from_header(handle, header.header)
    lib.fclose(handle)
    if ret != 0:
        raise RuntimeError(f"failed to verify xdb file {db_path} with errno={ret}")
    return ret


class Version:
    # cdef:
    #     lib.xdb_version_t *version

    @staticmethod
    def from_ptr(version) -> "Version":
        self = Version.__new__(Version)
        self.version = version
        return self

    @staticmethod
    def ipv4() -> "Version":
        self = Version.__new__(Version)
        self.version = lib.xdb_version_v4()
        if self.version == ffi.NULL:
            raise RuntimeError(f"failed to create version")
        return self

    @staticmethod
    def ipv6() -> "Version":
        self = Version.__new__(Version)
        self.version = lib.xdb_version_v6()
        if self.version == ffi.NULL:
            raise RuntimeError(f"failed to create version")
        return self

    @staticmethod
    def from_header(header: Header) -> "Version":
        self = Version.__new__(Version)
        self.version = lib.xdb_version_from_header(header.header)
        if self.version == ffi.NULL:
            raise RuntimeError(f"failed to create version")
        return self

    @property
    def segment_index_size(self):
        return self.version.segment_index_size

    def is_ipv4(self) -> bool:
        ret = lib.xdb_version_is_v4(self.version)
        return ret

    def is_ipv6(self) -> bool:
        ret = lib.xdb_version_is_v6(self.version)
        return ret


def init_winsock() -> int:
    ret = lib.xdb_init_winsock()
    return ret


def clean_winsock() -> None:
    lib.xdb_clean_winsock()


def now() -> int:
    ret = lib.xdb_now()
    return ret


def parse_ip(ip_string: str) -> tuple:
    str_p = ip_string.encode("utf-8")
    version = ffi.NULL
    buffer = bytes(16)
    buffer_ptr = ffi.case("const char*", buffer)
    version = lib.xdb_parse_ip(
        ffi.case("const char*", str_p), ffi.cast("unsigned char *", buffer_ptr), 16
    )
    if version == ffi.NULL:
        raise RuntimeError(f"failed to parse version")
    return Version.from_ptr(version), buffer[: version.bytes]


def parse_ip_into(ip_string: str, buffer: bytearray) -> Version:
    str_p = ip_string.encode("utf-8")
    version = ffi.NULL
    version = lib.xdb_parse_ip(
        ffi.case("const char*", str_p),
        ffi.cast("unsigned char *", ffi.from_buffer(buffer)),
        len(buffer),
    )
    if version == ffi.NULL:
        raise RuntimeError(f"failed to parse version")
    return Version.from_ptr(version)


def ip_to_string(buffer: bytes) -> str:
    ret = ffi.new("char[100]")
    lib.xdb_ip_to_string(
        ffi.cast("const unsigned char *", ffi.from_buffer(buffer)),
        len(buffer),
        ret,
        100,
    )
    return ffi.string(ret, 100).decode("utf-8")


def ip_sub_compare(ip1: bytes, ip2: bytes, offset: int) -> int:
    ret = lib.xdb_ip_sub_compare(
        ffi.cast("const unsigned char *", ffi.from_buffer(ip1)),
        len((ip1)),
        ffi.cast("const char *", ffi.from_buffer(ip2)),
        offset,
    )
    return ret


class RegionBuffer:
    # cdef:
    #     lib.xdb_region_buffer_t buffer
    #     char* region_buffer

    def __init__(self, size: int):
        self.buffer = ffi.new("xdb_region_buffer_t *")
        self.region_buffer = ffi.new(f"char[{size+1}]")  # +1 for NULL-end
        self.region_buffer[size] = "\0"  # NULL-end
        err = lib.xdb_region_buffer_init(
            self.buffer, ffi.cast("char*", self.region_buffer), size
        )
        if err != 0:
            self.region_buffer = ffi.NULL
            raise RuntimeError(f"failed to init the region buffer with err={err}")

    def __del__(self):
        if self.region_buffer:
            self.region_buffer = None


class Searcher:
    # cdef:
    #     lib.xdb_searcher_t searcher
    #     lib.xdb_content_t buf  # pointer to pybuffer
    #     const uint8_t[::1] pybuffer
    #     VectorIndex index

    @staticmethod
    def from_file(version: Version, db_path: object):
        self = Searcher.__new__(Searcher)
        self.searcher = ffi.new("xdb_searcher_t *")
        db_path_b = ensure_bytes(db_path)
        db_path_ptr = ffi.cast("const char *", db_path_b)
        err = lib.xdb_new_with_file_only(version.version, self.searcher, db_path_ptr)
        if err != 0:
            raise RuntimeError(
                f"failed to create xdb searcher from {db_path} with errno={err}"
            )
        return self

    @staticmethod
    def from_index(version: Version, db_path: object, index: VectorIndex):
        self = Searcher.__new__(Searcher)
        self.searcher = ffi.new("xdb_searcher_t *")
        db_path_b = ensure_bytes(db_path)
        db_path_ptr = ffi.cast("const char *", db_path_b)
        self.index = index  # hold a ref
        err = lib.xdb_new_with_vector_index(
            version.version, self.searcher, db_path_ptr, index.index
        )
        if err != 0:
            raise RuntimeError(
                "failed to create vector index cached searcher with path=%s, errcode=%d"
                % (db_path, err)
            )
        return self

    @staticmethod
    def from_buffer(version: Version, buffer: bytes):
        self = Searcher.__new__(Searcher)
        self.searcher = ffi.new("xdb_searcher_t *")
        self.pybuffer = buffer  # hold a ref
        self.buf = ffi.new("xdb_content_t *")
        self.buf.length = len(buffer)
        self.buf.buffer = ffi.cast("char*", buffer)
        err = lib.xdb_new_with_buffer(version.version, self.searcher, self.buf)
        if err != 0:
            raise RuntimeError("failed to create xdb searcher from buffer")
        return self

    def search_by_string(self, ip: object, size: int = 1000) -> str:
        region_buffer = RegionBuffer(size)
        ip_b = ensure_bytes(ip)
        ip_ptr = ffi.cast("const char*", ip_b)
        err = lib.xdb_search_by_string(self.searcher, ip_ptr, region_buffer.buffer)
        if err != 0:
            raise RuntimeError(f"failed search {ip} with errno={err}")
        return ffi.string(ffi.cast("const char*", region_buffer.buffer.value)).decode(
            "utf-8"
        )

    def search_by_string_into(self, ip: object, region_buffer: bytearray) -> None:
        # cdef lib.xdb_region_buffer_t region
        region = ffi.new("xdb_region_buffer_t *")
        lib.xdb_region_buffer_init(
            region,
            ffi.cast("char*", ffi.from_buffer(region_buffer)),
            len(region_buffer),
        )

        ip_b = ensure_bytes(ip)
        ip_ptr = ffi.cast("const char*", ip_b)
        err = lib.xdb_search_by_string(self.searcher, ip_ptr, region)
        if err != 0:
            raise RuntimeError(f"failed search {ip} with errno={err}")

    def search(self, ip: bytes, size: int = 1000) -> str:
        region_buffer = RegionBuffer(size)
        err = lib.xdb_search(
            self.searcher,
            ffi.cast("const unsigned char *", ffi.from_buffer(ip)),
            len(ip),
            region_buffer.buffer,
        )
        if err != 0:
            raise RuntimeError(f"failed search {ip} with errno={err}")
        return ffi.string(ffi.cast("const char*", region_buffer.buffer.value)).decode(
            "utf-8"
        )

    def search_into(self, ip: bytes, region_buffer: bytearray) -> None:
        # cdef lib.xdb_region_buffer_t region
        region = ffi.new("xdb_region_buffer_t *")
        lib.xdb_region_buffer_init(
            region,
            ffi.cast("char *", ffi.from_buffer(region_buffer)),
            len(region_buffer),
        )
        err = lib.xdb_search(
            self.searcher,
            ffi.cast("const unsigned char *", ffi.from_buffer(ip)),
            len(ip),
            region,
        )
        if err != 0:
            raise RuntimeError(f"failed search {ip} with errno={err}")

    def get_io_count(self) -> int:
        return lib.xdb_get_io_count(self.searcher)

    def get_version(self) -> Version:
        # cdef lib.xdb_version_t* version
        version = lib.xdb_get_version(self.searcher)
        if version == ffi.NULL:
            raise RuntimeError("failed to get version from searcher")
        return Version.from_ptr(version)

    def __del__(self):
        lib.xdb_close(self.searcher)
