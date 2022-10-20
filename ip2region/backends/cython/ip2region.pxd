# cython: language_level=3
# cython: cdivision=True
from libc.stdio cimport FILE


cdef extern from "xdb_searcher.h" nogil:
    int xdb_header_info_length
    int xdb_vector_index_rows
    int xdb_vector_index_cols
    int xdb_vector_index_size
    int xdb_segment_index_size
    int xdb_vector_index_length

    ctypedef struct xdb_header_t

    xdb_header_t * xdb_load_header(FILE *)
    xdb_header_t *  xdb_load_header_from_file(char *)
    void xdb_close_header(void *)

    ctypedef struct  xdb_vector_index_t:
        pass

    xdb_vector_index_t * xdb_load_vector_index(FILE *)
    xdb_vector_index_t *  xdb_load_vector_index_from_file(char *)
    void xdb_close_vector_index(void *)

    ctypedef struct xdb_content_t:
        unsigned int length
        char *buffer

    xdb_content_t * xdb_load_content(FILE *)
    xdb_content_t * xdb_load_content_from_file(char *)
    void xdb_close_content(void *)

    ctypedef struct xdb_searcher_t:
        pass
    int xdb_new_with_file_only(xdb_searcher_t *, const char *)
    int xdb_new_with_vector_index(xdb_searcher_t *, const char *, const xdb_vector_index_t *)
    int xdb_new_with_buffer(xdb_searcher_t *, const xdb_content_t *)
    void xdb_close(void *)
    int xdb_search_by_string(xdb_searcher_t *, const char *, char *, size_t)
    int xdb_search(xdb_searcher_t *, unsigned int, char *, size_t)
    int xdb_get_io_count(xdb_searcher_t *)

    unsigned int  xdb_get_uint(const char *, int)
    int xdb_get_ushort(const char *, int)
    int xdb_check_ip(const char *, unsigned int *)
    void xdb_long2ip(unsigned int, char *)
    unsigned int xdb_mip(unsigned long, unsigned long)
    long xdb_now()