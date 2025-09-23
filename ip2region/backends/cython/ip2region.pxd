# cython: language_level=3
# cython: cdivision=True
from libc.stdio cimport FILE

cdef extern from "xdb_api.h" nogil:
    int xdb_structure_20
    int xdb_structure_30
    int xdb_header_info_length
    int xdb_vector_index_rows
    int xdb_vector_index_cols
    int xdb_vector_index_size
    int xdb_segment_index_size

    # --- ip version info
    int xdb_ipv4_id
    int xdb_ipv6_id
    int xdb_ipv4_bytes
    int xdb_ipv6_bytes
    # cache of vector_index_row × vector_index_rows × vector_index_size
    int xdb_vector_index_length

    ctypedef struct xdb_header_t:
        unsigned short version
        unsigned short index_policy
        unsigned int created_at
        unsigned int start_index_ptr
        unsigned int end_index_ptr

        # since 3.0+ with IPv6 supporting
        unsigned short ip_version
        unsigned short runtime_ptr_bytes

        # the original buffer
        unsigned int length
        char *buffer# char buffer[xdb_header_info_length]

    xdb_header_t * xdb_load_header(FILE *)
    xdb_header_t * xdb_load_header_from_file(const char *)
    void xdb_free_header(void *)
    # --- vector index buffer
    ctypedef struct xdb_vector_index_t:
        unsigned int length
        char *buffer# char buffer[xdb_vector_index_length]

    xdb_vector_index_t * xdb_load_vector_index(FILE *)
    xdb_vector_index_t * xdb_load_vector_index_from_file(const char *)
    void xdb_free_vector_index(void *)

    # content buffer
    ctypedef struct xdb_content_t:
        unsigned int length
        char *buffer

    xdb_content_t * xdb_load_content(FILE *)
    xdb_content_t * xdb_load_content_from_file(const char *)
    void xdb_free_content(void *)
    # xdb verify
    int xdb_verify(FILE *)
    int xdb_verify_from_header(FILE *handle, xdb_header_t *)
    int xdb_verify_from_file(const char *)
    #
    ctypedef int(*ip_compare_fn_t)(const unsigned char *, int, const char *, int)

    ctypedef struct xdb_version_t:
        int id                 # version id 4 or 6
        char *name             # version name Literal IPv4 or IPv6
        int bytes              # ip bytes number, the length of ip byte array, 4 or 16
        int segment_index_size # segment index size in bytes
        # function to compare two ips
        ip_compare_fn_t ip_compare
    xdb_version_t * xdb_version_v4()
    xdb_version_t * xdb_version_v6()
    int xdb_version_is_v4(const xdb_version_t *)
    int xdb_version_is_v6(const xdb_version_t *)
    xdb_version_t * xdb_version_from_name(char *)
    xdb_version_t * xdb_version_from_header(xdb_header_t *)
    # to compatiable with the windows
    int xdb_init_winsock()
    void xdb_clean_winsock()
    long xdb_now()
    # get unsigned long (4bytes) from a specified buffer start from the specified offset with little-endian
    unsigned int xdb_le_get_uint32(const char *, int)
    # get unsigned short (2bytes) from a specified buffer start from the specified offset with little-endian
    int xdb_le_get_uint16(const char *, int)

    # parse the specified IP address to byte array.
    # returns: xdb_version_t for valid ipv4 / ipv6, or NULL for failed
    xdb_version_t * xdb_parse_ip(const char *, unsigned char *, size_t)

    # parse the specified IPv4 address to byte array
    # returns: xdb_version_t for valid ipv4, or NULL for failed
    xdb_version_t * xdb_parse_v4_ip(const char *, unsigned char *, size_t)

    # parse the specified IPv6 address to byte array
    # returns: xdb_version_t for valid ipv6, or NULL for failed
    xdb_version_t * xdb_parse_v6_ip(const char *, unsigned char *, size_t)

    # convert a specified ip bytes to humen-readable string.
    # returns: 0 for success or -1 for failed.
    int xdb_ip_to_string(const unsigned char *, int, char *, size_t)

    # ipv4 bytes to string
    int xdb_v4_ip_to_string(const unsigned char *, char *, size_t)

    # ipv6 bytes to string
    int xdb_v6_ip_to_string(const unsigned char *, char *, size_t)

    # compare the specified ip bytes with another ip bytes in the specified buff from offset.
    # ip args must be the return value from #xdb_parse_ip.
    # returns: -1 if ip1 < ip2, 1 if ip1 > ip2 or 0
    int xdb_ip_sub_compare(const unsigned char *, int, const char *, int)
    #
    int xdb_region_buffer_wrapper
    int xdb_region_buffer_auto
    ctypedef struct xdb_region_buffer_t:
        int type           # buffer type
        char *value        # region value
        size_t length      # buffer length

    # wrapper the region from a local stack buffer.
    # returns: 0 for succeed or failed
    int xdb_region_buffer_init(xdb_region_buffer_t *, char *, size_t)

    # do the buffer alloc.
    # returns: 0 for ok or failed
    int xdb_region_buffer_alloc(xdb_region_buffer_t *, int)

    void xdb_region_buffer_free(xdb_region_buffer_t *)

    # xdb searcher structure
    ctypedef struct xdb_searcher_t:
        # ip version
        xdb_version_t *version
        # xdb file handle
        FILE *handle
        # header info
        const char *header
        int io_count
        # vector index buffer cache.
        # preload the vector index will reduce the number of IO operations
        # thus speedup the search process.
        const xdb_vector_index_t *v_index
        # content buffer.
        # cache the whole xdb content.
        const xdb_content_t *content

    # xdb searcher new api define
    int xdb_new_with_file_only(xdb_version_t *, xdb_searcher_t *, const char *)
    int xdb_new_with_vector_index(xdb_version_t *, xdb_searcher_t *, const char *, const xdb_vector_index_t *)
    int xdb_new_with_buffer(xdb_version_t *, xdb_searcher_t *, const xdb_content_t *)
    void xdb_close(void *)
    # xdb searcher search api define
    int xdb_search_by_string(xdb_searcher_t *, const char *, xdb_region_buffer_t *)
    int xdb_search(xdb_searcher_t *, const unsigned char *, int, xdb_region_buffer_t *)
    xdb_version_t * xdb_get_version(xdb_searcher_t *)
    int xdb_get_io_count(xdb_searcher_t *)


# cdef extern from "xdb_searcher.h" nogil:
#     int xdb_header_info_length
#     int xdb_vector_index_rows
#     int xdb_vector_index_cols
#     int xdb_vector_index_size
#     int xdb_segment_index_size
#     int xdb_vector_index_length
#
#     ctypedef struct xdb_header_t
#
#     xdb_header_t * xdb_load_header(FILE *)
#     xdb_header_t *  xdb_load_header_from_file(char *)
#     void xdb_close_header(void *)
#
#     ctypedef struct  xdb_vector_index_t:
#         pass
#
#     xdb_vector_index_t * xdb_load_vector_index(FILE *)
#     xdb_vector_index_t *  xdb_load_vector_index_from_file(char *)
#     void xdb_close_vector_index(void *)
#
#     ctypedef struct xdb_content_t:
#         unsigned int length
#         char *buffer
#
#     xdb_content_t * xdb_load_content(FILE *)
#     xdb_content_t * xdb_load_content_from_file(char *)
#     void xdb_close_content(void *)
#
#     ctypedef struct xdb_searcher_t:
#         pass
#     int xdb_new_with_file_only(xdb_searcher_t *, const char *)
#     int xdb_new_with_vector_index(xdb_searcher_t *, const char *, const xdb_vector_index_t *)
#     int xdb_new_with_buffer(xdb_searcher_t *, const xdb_content_t *)
#     void xdb_close(void *)
#     int xdb_search_by_string(xdb_searcher_t *, const char *, char *, size_t)
#     int xdb_search(xdb_searcher_t *, unsigned int, char *, size_t)
#     int xdb_get_io_count(xdb_searcher_t *)
#
#     unsigned int  xdb_get_uint(const char *, int)
#     int xdb_get_ushort(const char *, int)
#     int xdb_check_ip(const char *, unsigned int *)
#     void xdb_long2ip(unsigned int, char *)
#     unsigned int xdb_mip(unsigned long, unsigned long)
#     long xdb_now()