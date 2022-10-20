# cython: language_level=3
# cython: cdivision=True
import cython

from cpython.bytes cimport (PyBytes_AS_STRING, PyBytes_FromString,
                            PyBytes_FromStringAndSize)
from cpython.mem cimport PyMem_Free, PyMem_Malloc
from libc.stdint cimport uint8_t

from ip2region.backends.cython.ip2region cimport (
    xdb_close, xdb_close_header, xdb_close_vector_index, xdb_content_t,
    xdb_get_io_count, xdb_header_t, xdb_load_vector_index_from_file,
    xdb_new_with_buffer, xdb_new_with_file_only, xdb_new_with_vector_index,
    xdb_now, xdb_search, xdb_search_by_string, xdb_searcher_t,
    xdb_vector_index_t)

from pathlib import Path

IF UNAME_SYSNAME != "Windows":
    cpdef inline long now() nogil:
        return xdb_now()

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
    cdef xdb_header_t * header

    def __dealloc__(self):
        xdb_close_header(self.header)

@cython.final
@cython.no_gc
@cython.freelist(8)
cdef class VectorIndex:
    cdef xdb_vector_index_t *index

    @staticmethod
    def from_file(object db_path):
        cdef VectorIndex  self = VectorIndex.__new__(VectorIndex)
        cdef bytes db_path_b = ensure_bytes(db_path)
        self.index = xdb_load_vector_index_from_file(<char*>db_path_b)
        if not self.index:
            raise RuntimeError("fail to create VectorIndex")
        return self

    def __dealloc__(self):
        xdb_close_vector_index(self.index)

@cython.final
@cython.freelist(8)
cdef class Searcher:
    cdef:
        xdb_searcher_t searcher
        xdb_content_t buf  # pointer to pybuffer
        const uint8_t[::1] pybuffer
        VectorIndex index

    @staticmethod
    def from_file(object db_path):
        cdef Searcher self = Searcher.__new__(Searcher)
        cdef bytes db_path_b = ensure_bytes(db_path)
        cdef int err
        cdef char *db_path_ptr = <char *> db_path_b
        with nogil:
            err = xdb_new_with_file_only(&self.searcher, db_path_ptr)
        if err != 0:
            raise RuntimeError("failed to create xdb searcher from `%s` with errno=%d" % (db_path, err))
        return self


    @staticmethod
    def from_index(object db_path, VectorIndex index):
        cdef Searcher self = Searcher.__new__(Searcher)
        cdef bytes db_path_b = ensure_bytes(db_path)
        cdef int err
        cdef char *db_path_ptr = <char *> db_path_b
        self.index = index # hold a ref
        with nogil:
            err = xdb_new_with_vector_index(&self.searcher, db_path_ptr, index.index)
        if err != 0:
            raise RuntimeError("failed to create vector index cached searcher with path=%s, errcode=%d" % (db_path, err))
        return self

    @staticmethod
    def from_buffer(const uint8_t[::1] buffer):
        cdef Searcher self = Searcher.__new__(Searcher)
        self.pybuffer = buffer # hold a ref
        self.buf.length = <unsigned int >buffer.shape[0]
        self.buf.buffer = <char*>&buffer[0]
        cdef int err
        with nogil:
            err =  xdb_new_with_buffer(&self.searcher, &self.buf)
        if err != 0:
            raise RuntimeError("failed to create xdb searcher from buffer")
        return self

    cpdef inline bytes search_by_string(self, object ip,Py_ssize_t size = 1000):
        cdef char* region_buffer = <char*>PyMem_Malloc(size)
        if not region_buffer:
            raise MemoryError
        cdef bytes ip_b
        cdef int err
        cdef char *ip_ptr
        try:
            ip_b = ensure_bytes(ip)
            ip_ptr = <char*>ip_b
            with nogil:
                err=xdb_search_by_string(&self.searcher, ip_ptr,  region_buffer, <size_t>size)
            if err!=0:
                raise RuntimeError("failed search(%s) with errno=%d"%(ip, err))
            return PyBytes_FromString(region_buffer)
        finally:
            PyMem_Free(region_buffer)

    cpdef inline search_by_string_into(self, object ip, uint8_t[::1] region_buffer):
        cdef bytes ip_b = ensure_bytes(ip)
        cdef char *ip_ptr = <char *> ip_b
        cdef int err
        with nogil:
            err = xdb_search_by_string(&self.searcher, ip_ptr, <char*>&region_buffer[0],<size_t>region_buffer.shape[0])
        if err != 0:
            raise RuntimeError("failed search(%s) with errno=%d" % (ip, err))

    cpdef inline bytes search(self, unsigned int ip,Py_ssize_t size = 1000):
        cdef char * region_buffer = <char *> PyMem_Malloc(size)
        if not region_buffer:
            raise MemoryError
        cdef int err
        try:
            with nogil:
                err = xdb_search(&self.searcher,ip, region_buffer , <size_t>size)
            if err != 0:
                raise RuntimeError("failed search(%d) with errno=%d" % (ip, err))
            return PyBytes_FromString(region_buffer)
        finally:
            PyMem_Free(region_buffer)

    cpdef inline search_into(self, unsigned int ip, uint8_t[::1] region_buffer):
        cdef int err
        with nogil:
            err = xdb_search(&self.searcher, ip, <char*>&region_buffer[0],<size_t>region_buffer.shape[0])
        if err != 0:
            raise RuntimeError("failed search(%s) with errno=%d" % (ip, err))

    cpdef inline int get_io_count(self):
        with nogil:
            return xdb_get_io_count(&self.searcher)

    def __dealloc__(self):
        xdb_close(&self.searcher)