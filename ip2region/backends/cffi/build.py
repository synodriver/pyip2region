import glob
import sys

from cffi import FFI

ffibuilder = FFI()
ffibuilder.cdef(
    """
// public constants define
// extern int xdb_structure_20;
// extern int xdb_structure_30;
// extern int xdb_header_info_length;
// extern int xdb_vector_index_rows;
// extern int xdb_vector_index_cols;
// extern int xdb_vector_index_size;
// extern int xdb_v4_index_size;    // 4 + 4 + 2 + 4
// extern int xdb_v6_index_size;    // 16 + 16 + 2 + 4

// --- ip version info
// extern int xdb_ipv4_id;
// extern int xdb_ipv6_id;
// extern int xdb_ipv4_bytes;
// extern int xdb_ipv6_bytes;
// cache of vector_index_row × vector_index_rows × vector_index_size
// extern int xdb_vector_index_length;

// --- xdb buffer functions

// use the following buffer struct to wrap the binary buffer data
// since the buffer data could not be operated with the string API.
struct xdb_header {
    unsigned short version;
    unsigned short index_policy;
    unsigned int created_at;
    unsigned int start_index_ptr;
    unsigned int end_index_ptr;
    
    // since 3.0+ with IPv6 supporting
    unsigned short ip_version;
    unsigned short runtime_ptr_bytes;

    // the original buffer
    unsigned int length;
    char buffer[256];
};
typedef struct xdb_header xdb_header_t;

xdb_header_t * xdb_load_header(FILE *);

xdb_header_t * xdb_load_header_from_file(const char *);

void xdb_free_header(void *);


// --- vector index buffer
struct xdb_vector_index {
    unsigned int length;
    char buffer[524288];
};
typedef struct xdb_vector_index xdb_vector_index_t;

xdb_vector_index_t * xdb_load_vector_index(FILE *);

xdb_vector_index_t * xdb_load_vector_index_from_file(const char *);

void xdb_free_vector_index(void *);


// --- content buffer
struct xdb_content {
    unsigned int length;
    char *buffer;
};
typedef struct xdb_content xdb_content_t;

xdb_content_t * xdb_load_content(FILE *);

xdb_content_t * xdb_load_content_from_file(const char *);

void xdb_free_content(void *);

// --- xdb verify

// Verify if the current Searcher could be used to search the specified xdb file.
// Why do we need this check ?
// The future features of the xdb impl may cause the current searcher not able to work properly.
//
// @Note: You Just need to check this ONCE when the service starts
// Or use another process (eg, A command) to check once Just to confirm the suitability.
int xdb_verify(FILE *);

int xdb_verify_from_header(FILE *handle, xdb_header_t *);

int xdb_verify_from_file(const char *);

// --- End xdb buffer


// types type define
typedef char string_ip_t;
typedef unsigned char bytes_ip_t;

// --- ip version
typedef int (* ip_compare_fn_t) (const bytes_ip_t *, int, const char *, int);
struct xdb_ip_version_entry {
    int id;                 // version id
    char *name;             // version name
    int bytes;              // ip bytes number
    int segment_index_size; // segment index size in bytes

    // function to compare two ips
    ip_compare_fn_t ip_compare;
};
typedef struct xdb_ip_version_entry xdb_version_t;

xdb_version_t * xdb_version_v4();
xdb_version_t * xdb_version_v6();

int xdb_version_is_v4(const xdb_version_t *);
int xdb_version_is_v6(const xdb_version_t *);

xdb_version_t * xdb_version_from_name(char *);
xdb_version_t * xdb_version_from_header(xdb_header_t *);

// --- END ip version

// --- xdb util functions

// to compatiable with the windows
// returns: 0 for ok and -1 for failed
int xdb_init_winsock();
void xdb_clean_winsock();

// get the current time in microseconds
long xdb_now();

// get unsigned long (4bytes) from a specified buffer start from the specified offset with little-endian
unsigned int xdb_le_get_uint32(const char *, int);

// get unsigned short (2bytes) from a specified buffer start from the specified offset with little-endian
int xdb_le_get_uint16(const char *, int);


// parse the specified IP address to byte array.
// returns: xdb_version_t for valid ipv4 / ipv6, or NULL for failed
xdb_version_t * xdb_parse_ip(const string_ip_t *, bytes_ip_t *, size_t);

// parse the specified IPv4 address to byte array
// returns: xdb_version_t for valid ipv4, or NULL for failed
xdb_version_t * xdb_parse_v4_ip(const string_ip_t *, bytes_ip_t *, size_t);

// parse the specified IPv6 address to byte array
// returns: xdb_version_t for valid ipv6, or NULL for failed
xdb_version_t * xdb_parse_v6_ip(const string_ip_t *, bytes_ip_t *, size_t);

// convert a specified ip bytes to humen-readable string.
// returns: 0 for success or -1 for failed.
int xdb_ip_to_string(const bytes_ip_t *, int, char *, size_t);

// ipv4 bytes to string
int xdb_v4_ip_to_string(const bytes_ip_t *, char *, size_t);

// ipv6 bytes to string
int xdb_v6_ip_to_string(const bytes_ip_t *, char *, size_t);

// compare the specified ip bytes with another ip bytes in the specified buff from offset.
// ip args must be the return value from #xdb_parse_ip.
// returns: -1 if ip1 < ip2, 1 if ip1 > ip2 or 0
int xdb_ip_sub_compare(const bytes_ip_t *, int, const char *, int);

// --- END xdb utils


// --- xdb searcher api

// xdb region info structure
// extern int xdb_region_buffer_wrapper;
// extern int xdb_region_buffer_auto;
struct xdb_region_buffer_entry {
    int type;           // buffer type
    char *value;        // region value
    size_t length;      // buffer length
};
typedef struct xdb_region_buffer_entry xdb_region_buffer_t;

// wrapper the region from a local stack buffer.
// returns: 0 for succeed or failed
int xdb_region_buffer_init(xdb_region_buffer_t *, char *, size_t);

// do the buffer alloc.
// returns: 0 for ok or failed
int xdb_region_buffer_alloc(xdb_region_buffer_t *, int);

void xdb_region_buffer_free(xdb_region_buffer_t *);

// xdb searcher structure
struct xdb_searcher_entry {
    // ip version
    xdb_version_t *version;

    // xdb file handle
    FILE *handle;

    // header info
    const char *header;
    int io_count;

    // vector index buffer cache.
    // preload the vector index will reduce the number of IO operations
    // thus speedup the search process.
    const xdb_vector_index_t *v_index;

    // content buffer.
    // cache the whole xdb content.
    const xdb_content_t *content;
};
typedef struct xdb_searcher_entry xdb_searcher_t;

// xdb searcher new api define
int xdb_new_with_file_only(xdb_version_t *, xdb_searcher_t *, const char *);

int xdb_new_with_vector_index(xdb_version_t *, xdb_searcher_t *, const char *, const xdb_vector_index_t *);

int xdb_new_with_buffer(xdb_version_t *, xdb_searcher_t *, const xdb_content_t *);

void xdb_close(void *);

// xdb searcher search api define
int xdb_search_by_string(xdb_searcher_t *, const string_ip_t *, xdb_region_buffer_t *);

int xdb_search(xdb_searcher_t *, const bytes_ip_t *, int, xdb_region_buffer_t *);

xdb_version_t * xdb_get_version(xdb_searcher_t *);

int xdb_get_io_count(xdb_searcher_t *);
    """
)

source = """
#include "xdb_api.h"
"""

ffibuilder.set_source(
    "ip2region.backends.cffi._xdb",
    source,
    sources=["./dep/binding/c/xdb_searcher.c", "./dep/binding/c/xdb_util.c"],
    include_dirs=["./dep/binding/c"],
    define_macros=[("WIN32_LEAN_AND_MEAN", None)],
)

if __name__ == "__main__":
    ffibuilder.compile()
