cdef class Buffer:
    cdef void *data
    cdef list l_free
    cdef int block_size
    cdef int block_count
    cdef int need_pack

    cdef grow(self, int block_count)
    cdef void add(self, void *blocks, int *indices, int count)
    cdef void remove(self, int *indices, int count)
    cdef void pack(self)
    cdef int count(self)
    cdef int size(self)
    cdef void *pointer(self)
