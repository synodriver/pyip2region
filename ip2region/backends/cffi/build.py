import glob
import sys

from cffi import FFI

ffibuilder = FFI()
ffibuilder.cdef(
    """
// extern int xdb_header_info_length;
// extern int xdb_vector_index_rows;
// extern int xdb_vector_index_cols;
// extern int xdb_vector_index_size;
// extern int xdb_segment_index_size;
// extern int xdb_vector_index_length;

typedef struct  { ...; } xdb_header_t;

xdb_header_t * xdb_load_header(FILE *);
xdb_header_t *  xdb_load_header_from_file(char *);
void xdb_close_header(void *);

typedef struct  { ...; } xdb_vector_index_t;

xdb_vector_index_t * xdb_load_vector_index(FILE *);
xdb_vector_index_t *  xdb_load_vector_index_from_file(char *);
void xdb_close_vector_index(void *);

typedef struct{
    unsigned int length;
    char *buffer;
}xdb_content_t;

xdb_content_t * xdb_load_content(FILE *);
xdb_content_t * xdb_load_content_from_file(char *);
void xdb_close_content(void *);

typedef struct {...;} xdb_searcher_t;
int xdb_new_with_file_only(xdb_searcher_t *, const char *);
int xdb_new_with_vector_index(xdb_searcher_t *, const char *, const xdb_vector_index_t *);
int xdb_new_with_buffer(xdb_searcher_t *, const xdb_content_t *);
void xdb_close(void *);
int xdb_search_by_string(xdb_searcher_t *, const char *, char *, size_t);
int xdb_search(xdb_searcher_t *, unsigned int, char *, size_t);
int xdb_get_io_count(xdb_searcher_t *);

unsigned int  xdb_get_uint(const char *, int);
int xdb_get_ushort(const char *, int);
int xdb_check_ip(const char *, unsigned int *);
void xdb_long2ip(unsigned int, char *);
unsigned int xdb_mip(unsigned long, unsigned long);
   // long xdb_now()
    """
)

source = """
#include "xdb_searcher.h"
"""

ffibuilder.set_source(
    "ip2region.backends.cffi._xdb",
    source,
    sources=["./dep/binding/c/xdb_searcher.c"],
    include_dirs=["./dep/binding/c"],
)

if __name__ == "__main__":
    ffibuilder.compile()
