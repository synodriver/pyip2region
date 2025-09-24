# cython: language_level=3
# cython: cdivision=True
import cython

from cpython.bytes cimport (PyBytes_AS_STRING, PyBytes_FromString,
                            PyBytes_FromStringAndSize)
from cpython.unicode cimport PyUnicode_AsUTF8, PyUnicode_FromString
from cpython.mem cimport PyMem_Free, PyMem_Malloc
from libc.stdint cimport uint8_t
from libc.stdio cimport fopen, fclose, FILE
from ip2region.backends.cython cimport ip2region as xdb

xdb_structure_20           = xdb.xdb_structure_20
xdb_structure_30           = xdb.xdb_structure_30
xdb_header_info_length     = xdb.xdb_header_info_length
xdb_vector_index_rows      = xdb.xdb_vector_index_rows
xdb_vector_index_cols      = xdb.xdb_vector_index_cols
xdb_vector_index_size      = xdb.xdb_vector_index_size
xdb_v4_index_size     = xdb.xdb_v4_index_size
xdb_v6_index_size     = xdb.xdb_v6_index_size
xdb_ipv4_id                = xdb.xdb_ipv4_id
xdb_ipv6_id                = xdb.xdb_ipv6_id
xdb_ipv4_bytes             = xdb.xdb_ipv4_bytes
xdb_ipv6_bytes             = xdb.xdb_ipv6_bytes
xdb_vector_index_length    = xdb.xdb_vector_index_length
xdb_region_buffer_wrapper  = xdb.xdb_region_buffer_wrapper
xdb_region_buffer_auto     = xdb.xdb_region_buffer_auto

from pathlib import Path

cdef inline bytes ensure_bytes(object inp):
    if isinstance(inp, unicode):
        return inp.encode()
    elif isinstance(inp, bytes):
        return inp
    elif isinstance(inp, Path):
        return str(inp).encode()
    else:
        return bytes(inp)

@cython.final
@cython.no_gc
@cython.freelist(8)
cdef class Header:
    cdef:
        xdb.xdb_header_t * header
        Py_ssize_t[1] shape
        Py_ssize_t[1] strides

    @staticmethod
    def from_file(object db_path):
        cdef Header self = Header.__new__(Header)
        cdef bytes db_path_b = ensure_bytes(db_path)
        self.header = xdb.xdb_load_header_from_file(<const char*>db_path_b)
        if not self.header:
            raise RuntimeError(f"failed to load header from {db_path}")
        return self

    @property
    def version(self):
        return self.header.version
    @version.setter
    def version(self, unsigned short value):
        self.header.version = value

    @property
    def index_policy(self):
        return self.header.index_policy
    @index_policy.setter
    def index_policy(self, unsigned short value):
        self.header.index_policy = value

    @property
    def created_at(self):
        return self.header.created_at
    @created_at.setter
    def created_at(self, unsigned short value):
        self.header.created_at = value

    @property
    def start_index_ptr(self):
        return self.header.start_index_ptr
    @start_index_ptr.setter
    def start_index_ptr(self, unsigned short value):
        self.header.start_index_ptr = value

    @property
    def end_index_ptr(self):
        return self.header.end_index_ptr
    @end_index_ptr.setter
    def end_index_ptr(self, unsigned short value):
        self.header.end_index_ptr = value

    @property
    def ip_version(self):
        return self.header.ip_version
    @ip_version.setter
    def ip_version(self, unsigned short value):
        self.header.ip_version = value

    @property
    def runtime_ptr_bytes(self):
        return self.header.runtime_ptr_bytes
    @runtime_ptr_bytes.setter
    def runtime_ptr_bytes(self, unsigned short value):
        self.header.runtime_ptr_bytes = value

    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t itemsize = sizeof(char)
        self.strides[0] = itemsize
        self.shape[0] = self.header.length

        buffer.buf = <char *>self.header.buffer
        buffer.format = 'B'  # bytes
        buffer.internal = NULL  # see References
        buffer.itemsize = itemsize
        buffer.len =  self.header.length * itemsize  # product(shape) * itemsize
        buffer.ndim = 1
        buffer.obj = self
        buffer.readonly = 0
        buffer.shape = self.shape
        buffer.strides = self.strides
        buffer.suboffsets = NULL  # for pointer arrays only

    # def __releasebuffer__(self, Py_buffer *buffer):
    #     ...

    def __dealloc__(self):
        if self.header:
            xdb.xdb_free_header(self.header)

@cython.final
@cython.no_gc
@cython.freelist(8)
cdef class VectorIndex:
    cdef:
        xdb.xdb_vector_index_t *index
        Py_ssize_t[1] shape
        Py_ssize_t[1] strides

    @staticmethod
    def from_file(object db_path):
        cdef VectorIndex  self = VectorIndex.__new__(VectorIndex)
        cdef bytes db_path_b = ensure_bytes(db_path)
        self.index = xdb.xdb_load_vector_index_from_file(<const char*>db_path_b)
        if not self.index:
            raise RuntimeError(f"failed to load vector index from {db_path}")
        return self

    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t itemsize = sizeof(char)
        self.strides[0] = itemsize
        self.shape[0] = self.index.length

        buffer.buf = <char *>self.index.buffer
        buffer.format = 'B'  # bytes
        buffer.internal = NULL  # see References
        buffer.itemsize = itemsize
        buffer.len =  self.index.length * itemsize  # product(shape) * itemsize
        buffer.ndim = 1
        buffer.obj = self
        buffer.readonly = 0
        buffer.shape = self.shape
        buffer.strides = self.strides
        buffer.suboffsets = NULL  # for pointer arrays only

    def __dealloc__(self):
        if self.index:
            xdb.xdb_free_vector_index(self.index)

@cython.final
@cython.no_gc
@cython.freelist(8)
cdef class Content:
    cdef:
        xdb.xdb_content_t *content
        Py_ssize_t[1] shape
        Py_ssize_t[1] strides

    @staticmethod
    def from_file(object db_path):
        cdef Content self = Content.__new__(Content)
        cdef bytes db_path_b = ensure_bytes(db_path)
        self.content = xdb.xdb_load_content_from_file(<const char*>db_path_b)
        if not self.content:
            raise RuntimeError(f"failed to load xdb content from {db_path}")
        return self

    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t itemsize = sizeof(char)
        self.strides[0] = itemsize
        self.shape[0] = self.content.length

        buffer.buf = self.content.buffer
        buffer.format = 'B'  # bytes
        buffer.internal = NULL  # see References
        buffer.itemsize = itemsize
        buffer.len =  self.content.length * itemsize  # product(shape) * itemsize
        buffer.ndim = 1
        buffer.obj = self
        buffer.readonly = 0
        buffer.shape = self.shape
        buffer.strides = self.strides
        buffer.suboffsets = NULL  # for pointer arrays only

    def __dealloc__(self):
        if self.content:
            xdb.xdb_free_content(self.content)


cpdef inline int verify(object db_path) except -1:
    cdef bytes db_path_b = ensure_bytes(db_path)
    cdef const char* db_path_ptr = <const char*>db_path_b
    cdef int ret
    with nogil:
        ret = xdb.xdb_verify_from_file(db_path_ptr)
    if ret != 0:
        raise RuntimeError(f"failed to verify xdb file {db_path} with errno={ret}")
    return ret


cpdef inline int verify_from_header(object db_path, Header header) except -1:
    cdef bytes db_path_b = ensure_bytes(db_path)
    cdef const char * db_path_ptr = <const char *> db_path_b
    cdef int ret
    cdef FILE * handle = NULL
    with nogil:
        handle = fopen(db_path_ptr, "rb")
        if not handle:
            with gil:
                raise RuntimeError(f"failed to open {db_path}")
        ret = xdb.xdb_verify_from_header(handle, header.header)
        fclose(handle)
    if ret != 0:
        raise RuntimeError(f"failed to verify xdb file {db_path} with errno={ret}")
    return ret

@cython.final
@cython.no_gc
@cython.freelist(8)
cdef class Version:
    cdef:
        xdb.xdb_version_t *version

    @staticmethod
    cdef inline Version from_ptr(xdb.xdb_version_t* version):
        cdef Version self = Version.__new__(Version)
        self.version = version
        return self


    @staticmethod
    def ipv4():
        cdef Version self = Version.__new__(Version)
        self.version = xdb.xdb_version_v4()
        if not self.version:
            raise RuntimeError(f"failed to create version")
        return self

    @staticmethod
    def ipv6():
        cdef Version self = Version.__new__(Version)
        self.version = xdb.xdb_version_v6()
        if not self.version:
            raise RuntimeError(f"failed to create version")
        return self

    @staticmethod
    def from_header(Header header):
        cdef Version self = Version.__new__(Version)
        self.version = xdb.xdb_version_from_header(header.header)
        if not self.version:
            raise RuntimeError(f"failed to create version")
        return self

    @property
    def segment_index_size(self):
        return self.version.segment_index_size

    cpdef inline bint is_ipv4(self):
        cdef bint ret
        with nogil:
            ret = xdb.xdb_version_is_v4(self.version)
        return ret

    cpdef inline bint is_ipv6(self):
        cdef bint ret
        with nogil:
            ret = xdb.xdb_version_is_v6(self.version)
        return ret

cpdef inline int init_winsock() noexcept:
    cdef int ret
    with nogil:
        ret = xdb.xdb_init_winsock()
    return ret


cpdef inline clean_winsock() noexcept:
    with nogil:
        xdb.xdb_clean_winsock()

cpdef inline long now() noexcept:
    cdef long ret
    with nogil:
        ret = xdb.xdb_now()
    return ret

cpdef inline tuple parse_ip(str ip_string):
    cdef const char* str_p = PyUnicode_AsUTF8(ip_string)
    cdef xdb.xdb_version_t *version = NULL
    cdef bytes buffer = PyBytes_FromStringAndSize(NULL, 16)
    cdef const char* buffer_ptr = <const char*>buffer
    with nogil:
        version = xdb.xdb_parse_ip(str_p, <unsigned char *>buffer_ptr, 16)
    if version == NULL:
        raise RuntimeError(f"failed to parse version")
    return Version.from_ptr(version), buffer[:version.bytes]


cpdef inline Version parse_ip_into(str ip_string, uint8_t[::1] buffer):
    cdef const char* str_p = PyUnicode_AsUTF8(ip_string)
    cdef xdb.xdb_version_t *version = NULL
    with nogil:
        version = xdb.xdb_parse_ip(str_p, <unsigned char *>&buffer[0], <size_t>buffer.shape[0])
    if version == NULL:
        raise RuntimeError(f"failed to parse version")
    return Version.from_ptr(version)

cpdef inline str ip_to_string(const uint8_t[::1] buffer):
    cdef char ret[100]
    with nogil:
        xdb.xdb_ip_to_string(<const unsigned char *>&buffer[0], <int>buffer.shape[0], ret, 100)
    return PyUnicode_FromString(<const char*>ret)

cpdef inline int ip_sub_compare(const uint8_t[::1] ip1, const uint8_t[::1] ip2, int offset):
    cdef int ret
    with nogil:
        ret = xdb.xdb_ip_sub_compare(<const unsigned char *>&ip1[0], <int>ip1.shape[0], <const char *>&ip2[0], offset)
    return ret

@cython.final
@cython.freelist(8)
@cython.no_gc
cdef class RegionBuffer:
    cdef:
        xdb.xdb_region_buffer_t buffer
        char* region_buffer

    def __cinit__(self, Py_ssize_t size):
        self.region_buffer = <char*>PyMem_Malloc(size+1)  # +1 for NULL-end
        if not self.region_buffer:
            raise MemoryError
        self.region_buffer[size] = '\0'  # NULL-end
        cdef int err = xdb.xdb_region_buffer_init(&self.buffer, self.region_buffer, size)
        if err != 0:
            PyMem_Free(self.region_buffer)
            self.region_buffer = NULL
            raise RuntimeError(f"failed to init the region buffer with err={err}")

    def __dealloc__(self):
        if self.region_buffer:
            PyMem_Free(self.region_buffer)
            self.region_buffer = NULL


@cython.final
@cython.freelist(8)
cdef class Searcher:
    cdef:
        xdb.xdb_searcher_t searcher
        xdb.xdb_content_t buf  # pointer to pybuffer
        const uint8_t[::1] pybuffer
        VectorIndex index

    @staticmethod
    def from_file(Version version, object db_path):
        cdef Searcher self = Searcher.__new__(Searcher)
        cdef bytes db_path_b = ensure_bytes(db_path)
        cdef int err
        cdef const char *db_path_ptr = <const char *> db_path_b
        with nogil:
            err = xdb.xdb_new_with_file_only(version.version, &self.searcher, db_path_ptr)
        if err != 0:
            raise RuntimeError(f"failed to create xdb searcher from {db_path} with errno={err}")
        return self

    @staticmethod
    def from_index(Version version, object db_path, VectorIndex index):
        cdef Searcher self = Searcher.__new__(Searcher)
        cdef bytes db_path_b = ensure_bytes(db_path)
        cdef int err
        cdef const char *db_path_ptr = <const char *> db_path_b
        self.index = index # hold a ref
        with nogil:
            err = xdb.xdb_new_with_vector_index(version.version, &self.searcher, db_path_ptr, index.index)
        if err != 0:
            raise RuntimeError("failed to create vector index cached searcher with path=%s, errcode=%d" % (db_path, err))
        return self

    @staticmethod
    def from_buffer(Version version, const uint8_t[::1] buffer):
        cdef Searcher self = Searcher.__new__(Searcher)
        self.pybuffer = buffer # hold a ref
        self.buf.length = <unsigned int >buffer.shape[0]
        self.buf.buffer = <char*>&buffer[0]
        cdef int err
        with nogil:
            err =  xdb.xdb_new_with_buffer(version.version, &self.searcher, &self.buf)
        if err != 0:
            raise RuntimeError("failed to create xdb searcher from buffer")
        return self

    cpdef inline str search_by_string(self, object ip, Py_ssize_t size = 1000):
        cdef RegionBuffer region_buffer = RegionBuffer(size)
        cdef bytes ip_b = ensure_bytes(ip)
        cdef int err
        cdef const char *ip_ptr = <const char*>ip_b
        with nogil:
            err = xdb.xdb_search_by_string(&self.searcher, ip_ptr,  &region_buffer.buffer)
        if err != 0:
            raise RuntimeError(f"failed search {ip} with errno={err}")
        return PyUnicode_FromString(<const char*>region_buffer.buffer.value)

    cpdef inline search_by_string_into(self, object ip, uint8_t[::1] region_buffer):
        cdef xdb.xdb_region_buffer_t region
        xdb.xdb_region_buffer_init(&region, <char*>&region_buffer[0], <size_t>region_buffer.shape[0])

        cdef bytes ip_b = ensure_bytes(ip)
        cdef const char *ip_ptr = <const char *> ip_b
        cdef int err
        with nogil:
            err = xdb.xdb_search_by_string(&self.searcher, ip_ptr, &region)
        if err != 0:
            raise RuntimeError(f"failed search {ip} with errno={err}")

    cpdef inline str search(self, const uint8_t[::1] ip, Py_ssize_t size = 1000):
        cdef RegionBuffer region_buffer = RegionBuffer(size)
        cdef int err
        with nogil:
            err = xdb.xdb_search(&self.searcher, <const unsigned char *>&ip[0], <int>ip.shape[0], &region_buffer.buffer)
        if err != 0:
            raise RuntimeError(f"failed search {ip} with errno={err}")
        return PyUnicode_FromString(<const char*>region_buffer.buffer.value)

    cpdef inline search_into(self, const uint8_t[::1] ip, uint8_t[::1] region_buffer):
        cdef xdb.xdb_region_buffer_t region
        xdb.xdb_region_buffer_init(&region, <char *> &region_buffer[0], <size_t> region_buffer.shape[0])
        cdef int err
        with nogil:
            err = xdb.xdb_search(&self.searcher, <const unsigned char *>&ip[0], <int>ip.shape[0], &region)
        if err != 0:
            raise RuntimeError(f"failed search {ip} with errno={err}")

    cpdef inline int get_io_count(self):
        with nogil:
            return xdb.xdb_get_io_count(&self.searcher)

    cpdef inline Version get_version(self):
        cdef xdb.xdb_version_t* version
        with nogil:
            version = xdb.xdb_get_version(&self.searcher)
        if not version:
            raise RuntimeError("failed to get version from searcher")
        return Version.from_ptr(version)

    def __dealloc__(self):
        xdb.xdb_close(&self.searcher)