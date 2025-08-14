cimport cython
cimport numpy as np

import numpy as np
from numpy.lib.stride_tricks import as_strided

# Array with limit 2D
#
# double
#

@cython.boundscheck(False)
cdef np.ndarray[double, ndim=2] ndarray_double():
    return np.empty((0,0), dtype='double')

@cython.boundscheck(False)
cdef np.ndarray[double, ndim=2] ndarray_double_C(double *data, long rows, long cols, long row_stride, long col_stride):
    cdef double[:,:] mem_view = <double[:rows,:cols]>data
    dtype = 'double'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[double, ndim=2] ndarray_double_F(double *data, long rows, long cols, long row_stride, long col_stride):
    cdef double[::1,:] mem_view = <double[:rows:1,:cols]>data
    dtype = 'double'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[double, ndim=2] ndarray_copy_double_C(const double *data, long rows, long cols, long row_stride, long col_stride):
    cdef double[:,:] mem_view = <double[:rows,:cols]>data
    dtype = 'double'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize]))

@cython.boundscheck(False)
cdef np.ndarray[double, ndim=2] ndarray_copy_double_F(const double *data, long rows, long cols, long row_stride, long col_stride):
    cdef double[::1,:] mem_view = <double[:rows:1,:cols]>data
    dtype = 'double'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize]))

#
# long double
#

@cython.boundscheck(False)
cdef np.ndarray[long double, ndim=2] ndarray_long_double():
    return np.empty((0,0), dtype='longdouble')

@cython.boundscheck(False)
cdef np.ndarray[long double, ndim=2] ndarray_long_double_C(long double *data, long rows, long cols, long row_stride, long col_stride):
    cdef long double[:,:] mem_view = <long double[:rows,:cols]>data
    dtype = 'longdouble'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[long double, ndim=2] ndarray_long_double_F(long double *data, long rows, long cols, long row_stride, long col_stride):
    cdef long double[::1,:] mem_view = <long double[:rows:1,:cols]>data
    dtype = 'longdouble'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[long double, ndim=2] ndarray_copy_long_double_C(const long double *data, long rows, long cols, long row_stride, long col_stride):
    cdef long double[:,:] mem_view = <long double[:rows,:cols]>data
    dtype = 'longdouble'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize]))

@cython.boundscheck(False)
cdef np.ndarray[long double, ndim=2] ndarray_copy_long_double_F(const long double *data, long rows, long cols, long row_stride, long col_stride):
    cdef long double[::1,:] mem_view = <long double[:rows:1,:cols]>data
    dtype = 'longdouble'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize]))

#
# float
#

@cython.boundscheck(False)
cdef np.ndarray[float, ndim=2] ndarray_float():
    return np.empty((0,0), dtype='float')

@cython.boundscheck(False)
cdef np.ndarray[float, ndim=2] ndarray_float_C(float *data, long rows, long cols, long row_stride, long col_stride):
    cdef float[:,:] mem_view = <float[:rows,:cols]>data
    dtype = 'float'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[float, ndim=2] ndarray_float_F(float *data, long rows, long cols, long row_stride, long col_stride):
    cdef float[::1,:] mem_view = <float[:rows:1,:cols]>data
    dtype = 'float'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[float, ndim=2] ndarray_copy_float_C(const float *data, long rows, long cols, long row_stride, long col_stride):
    cdef float[:,:] mem_view = <float[:rows,:cols]>data
    dtype = 'float'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize]))

@cython.boundscheck(False)
cdef np.ndarray[float, ndim=2] ndarray_copy_float_F(const float *data, long rows, long cols, long row_stride, long col_stride):
    cdef float[::1,:] mem_view = <float[:rows:1,:cols]>data
    dtype = 'float'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize]))
#
# long  long
#

@cython.boundscheck(False)
cdef np.ndarray[ longlong, ndim=2] ndarray_long_long():
    return np.empty((0,0), dtype='longlong')

@cython.boundscheck(False)
cdef np.ndarray[longlong, ndim=2] ndarray_long_long_C(long long *data, long rows, long cols, long row_stride, long col_stride):
    cdef long long[:,:] mem_view = <long long[:rows,:cols]>data
    dtype = 'longlong'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[longlong, ndim=2] ndarray_long_long_F(long long *data, long rows, long cols, long row_stride, long col_stride):
    cdef long long[::1,:] mem_view = <long long[:rows:1,:cols]>data
    dtype = 'longlong'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[longlong, ndim=2] ndarray_copy_long_long_C(const long long *data, long rows, long cols, long row_stride, long col_stride):
    cdef long long[:,:] mem_view = <long long[:rows,:cols]>data
    dtype = 'longlong'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize]))

@cython.boundscheck(False)
cdef np.ndarray[longlong, ndim=2] ndarray_copy_long_long_F(const long long *data, long rows, long cols, long row_stride, long col_stride):
    cdef long long[::1,:] mem_view = <long long[:rows:1,:cols]>data
    dtype = 'longlong'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize]))

#
# long
#

@cython.boundscheck(False)
cdef np.ndarray[long, ndim=2] ndarray_long():
    return np.empty((0,0), dtype='long')

@cython.boundscheck(False)
cdef np.ndarray[long, ndim=2] ndarray_long_C(long *data, long rows, long cols, long row_stride, long col_stride):
    cdef long[:,:] mem_view = <long[:rows,:cols]>data
    dtype = 'long'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[long, ndim=2] ndarray_long_F(long *data, long rows, long cols, long row_stride, long col_stride):
    cdef long[::1,:] mem_view = <long[:rows:1,:cols]>data
    dtype = 'long'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[long, ndim=2] ndarray_copy_long_C(const long *data, long rows, long cols, long row_stride, long col_stride):
    cdef long[:,:] mem_view = <long[:rows,:cols]>data
    dtype = 'long'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize]))

@cython.boundscheck(False)
cdef np.ndarray[long, ndim=2] ndarray_copy_long_F(const long *data, long rows, long cols, long row_stride, long col_stride):
    cdef long[::1,:] mem_view = <long[:rows:1,:cols]>data
    dtype = 'long'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize]))

#
# unsigned long long
#
@cython.boundscheck(False)
cdef np.ndarray[unsigned long long, ndim=2] ndarray_ulong_long():
    return np.empty((0,0), dtype='ulong')

@cython.boundscheck(False)
cdef np.ndarray[unsigned long long, ndim=2] ndarray_ulong_long_C(unsigned long long *data, long rows, long cols, long row_stride, long col_stride):
    cdef unsigned long long[:,:] mem_view = <unsigned long long[:rows,:cols]>data
    dtype = 'ulonglong'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[unsigned long long, ndim=2] ndarray_ulong_long_F(unsigned long long *data, long rows, long cols, long row_stride, long col_stride):
    cdef unsigned long long[::1,:] mem_view = <unsigned long long[:rows:1,:cols]>data
    dtype = 'ulonglong'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[unsigned long long, ndim=2] ndarray_copy_ulong_long_C(const unsigned long long *data, long rows, long cols, long row_stride, long col_stride):
    cdef unsigned long long[:,:] mem_view = <unsigned long long[:rows,:cols]>data
    dtype = 'ulonglong'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize]))

@cython.boundscheck(False)
cdef np.ndarray[unsigned long long, ndim=2] ndarray_copy_ulong_long_F(const unsigned long long *data, long rows, long cols, long row_stride, long col_stride):
    cdef unsigned long long[::1,:] mem_view = <unsigned long long[:rows:1,:cols]>data
    dtype = 'ulonglong'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize]))

#
# unsigned long
#

@cython.boundscheck(False)
cdef np.ndarray[unsigned long, ndim=2] ndarray_ulong():
    return np.empty((0,0), dtype='ulong')

@cython.boundscheck(False)
cdef np.ndarray[unsigned long, ndim=2] ndarray_ulong_C(unsigned long *data, long rows, long cols, long row_stride, long col_stride):
    cdef unsigned long[:,:] mem_view = <unsigned long[:rows,:cols]>data
    dtype = 'ulong'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[unsigned long, ndim=2] ndarray_ulong_F(unsigned long *data, long rows, long cols, long row_stride, long col_stride):
    cdef unsigned long[::1,:] mem_view = <unsigned long[:rows:1,:cols]>data
    dtype = 'ulong'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[unsigned long, ndim=2] ndarray_copy_ulong_C(const unsigned long *data, long rows, long cols, long row_stride, long col_stride):
    cdef unsigned long[:,:] mem_view = <unsigned long[:rows,:cols]>data
    dtype = 'ulong'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize]))

@cython.boundscheck(False)
cdef np.ndarray[unsigned long, ndim=2] ndarray_copy_ulong_F(const unsigned long *data, long rows, long cols, long row_stride, long col_stride):
    cdef unsigned long[::1,:] mem_view = <unsigned long[:rows:1,:cols]>data
    dtype = 'ulong'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize]))

#
# int
#

@cython.boundscheck(False)
cdef np.ndarray[int, ndim=2] ndarray_int():
    return np.empty((0,0), dtype='int')

@cython.boundscheck(False)
cdef np.ndarray[int, ndim=2] ndarray_int_C(int *data, long rows, long cols, long row_stride, long col_stride):
    cdef int[:,:] mem_view = <int[:rows,:cols]>data
    dtype = 'int'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[int, ndim=2] ndarray_int_F(int *data, long rows, long cols, long row_stride, long col_stride):
    cdef int[::1,:] mem_view = <int[:rows:1,:cols]>data
    dtype = 'int'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[int, ndim=2] ndarray_copy_int_C(const int *data, long rows, long cols, long row_stride, long col_stride):
    cdef int[:,:] mem_view = <int[:rows,:cols]>data
    dtype = 'int'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize]))

@cython.boundscheck(False)
cdef np.ndarray[int, ndim=2] ndarray_copy_int_F(const int *data, long rows, long cols, long row_stride, long col_stride):
    cdef int[::1,:] mem_view = <int[:rows:1,:cols]>data
    dtype = 'int'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize]))

#
# unsigned int
#

@cython.boundscheck(False)
cdef np.ndarray[unsigned int, ndim=2] ndarray_uint():
    return np.empty((0,0), dtype='uint')

@cython.boundscheck(False)
cdef np.ndarray[unsigned int, ndim=2] ndarray_uint_C(unsigned int *data, long rows, long cols, long row_stride, long col_stride):
    cdef unsigned int[:,:] mem_view = <unsigned int[:rows,:cols]>data
    dtype = 'uint'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[unsigned int, ndim=2] ndarray_uint_F(unsigned int *data, long rows, long cols, long row_stride, long col_stride):
    cdef unsigned int[::1,:] mem_view = <unsigned int[:rows:1,:cols]>data
    dtype = 'uint'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[unsigned int, ndim=2] ndarray_copy_uint_C(const unsigned int *data, long rows, long cols, long row_stride, long col_stride):
    cdef unsigned int[:,:] mem_view = <unsigned int[:rows,:cols]>data
    dtype = 'uint'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize]))

@cython.boundscheck(False)
cdef np.ndarray[unsigned int, ndim=2] ndarray_copy_uint_F(const unsigned int *data, long rows, long cols, long row_stride, long col_stride):
    cdef unsigned int[::1,:] mem_view = <unsigned int[:rows:1,:cols]>data
    dtype = 'uint'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize]))

#
# short
#

@cython.boundscheck(False)
cdef np.ndarray[short, ndim=2] ndarray_short():
    return np.empty((0,0), dtype='short')

@cython.boundscheck(False)
cdef np.ndarray[short, ndim=2] ndarray_short_C(short *data, long rows, long cols, long row_stride, long col_stride):
    cdef short[:,:] mem_view = <short[:rows,:cols]>data
    dtype = 'short'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[short, ndim=2] ndarray_short_F(short *data, long rows, long cols, long row_stride, long col_stride):
    cdef short[::1,:] mem_view = <short[:rows:1,:cols]>data
    dtype = 'short'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[short, ndim=2] ndarray_copy_short_C(const short *data, long rows, long cols, long row_stride, long col_stride):
    cdef short[:,:] mem_view = <short[:rows,:cols]>data
    dtype = 'short'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize]))

@cython.boundscheck(False)
cdef np.ndarray[short, ndim=2] ndarray_copy_short_F(const short *data, long rows, long cols, long row_stride, long col_stride):
    cdef short[::1,:] mem_view = <short[:rows:1,:cols]>data
    dtype = 'short'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize]))

#
# unsigned short
#

@cython.boundscheck(False)
cdef np.ndarray[unsigned short, ndim=2] ndarray_ushort():
    return np.empty((0,0), dtype='ushort')

@cython.boundscheck(False)
cdef np.ndarray[unsigned short, ndim=2] ndarray_ushort_C(unsigned short *data, long rows, long cols, long row_stride, long col_stride):
    cdef unsigned short[:,:] mem_view = <unsigned short[:rows,:cols]>data
    dtype = 'ushort'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[unsigned short, ndim=2] ndarray_ushort_F(unsigned short *data, long rows, long cols, long row_stride, long col_stride):
    cdef unsigned short[::1,:] mem_view = <unsigned short[:rows:1,:cols]>data
    dtype = 'ushort'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[unsigned short, ndim=2] ndarray_copy_ushort_C(const unsigned short *data, long rows, long cols, long row_stride, long col_stride):
    cdef unsigned short[:,:] mem_view = <unsigned short[:rows,:cols]>data
    dtype = 'ushort'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize]))

@cython.boundscheck(False)
cdef np.ndarray[unsigned short, ndim=2] ndarray_copy_ushort_F(const unsigned short *data, long rows, long cols, long row_stride, long col_stride):
    cdef unsigned short[::1,:] mem_view = <unsigned short[:rows:1,:cols]>data
    dtype = 'ushort'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize]))

#
# signed char
#

@cython.boundscheck(False)
cdef np.ndarray[signed char, ndim=2] ndarray_schar():
    return np.empty((0,0), dtype='int8')

@cython.boundscheck(False)
cdef np.ndarray[signed char, ndim=2] ndarray_schar_C(signed char *data, long rows, long cols, long row_stride, long col_stride):
    cdef signed char[:,:] mem_view = <signed char[:rows,:cols]>data
    dtype = 'int8'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[signed char, ndim=2] ndarray_schar_F(signed char *data, long rows, long cols, long row_stride, long col_stride):
    cdef signed char[::1,:] mem_view = <signed char[:rows:1,:cols]>data
    dtype = 'int8'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[signed char, ndim=2] ndarray_copy_schar_C(const signed char *data, long rows, long cols, long row_stride, long col_stride):
    cdef signed char[:,:] mem_view = <signed char[:rows,:cols]>data
    dtype = 'int8'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize]))

@cython.boundscheck(False)
cdef np.ndarray[signed char, ndim=2] ndarray_copy_schar_F(const signed char *data, long rows, long cols, long row_stride, long col_stride):
    cdef signed char[::1,:] mem_view = <signed char[:rows:1,:cols]>data
    dtype = 'int8'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize]))

#
# unsigned char
#

@cython.boundscheck(False)
cdef np.ndarray[unsigned char, ndim=2] ndarray_uchar():
    return np.empty((0,0), dtype='uint8')

@cython.boundscheck(False)
cdef np.ndarray[unsigned char, ndim=2] ndarray_uchar_C(unsigned char *data, long rows, long cols, long row_stride, long col_stride):
    cdef unsigned char[:,:] mem_view = <unsigned char[:rows,:cols]>data
    dtype = 'uint8'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[unsigned char, ndim=2] ndarray_uchar_F(unsigned char *data, long rows, long cols, long row_stride, long col_stride):
    cdef unsigned char[::1,:] mem_view = <unsigned char[:rows:1,:cols]>data
    dtype = 'uint8'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[unsigned char, ndim=2] ndarray_copy_uchar_C(const unsigned char *data, long rows, long cols, long row_stride, long col_stride):
    cdef unsigned char[:,:] mem_view = <unsigned char[:rows,:cols]>data
    dtype = 'uint8'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize]))

@cython.boundscheck(False)
cdef np.ndarray[unsigned char, ndim=2] ndarray_copy_uchar_F(const unsigned char *data, long rows, long cols, long row_stride, long col_stride):
    cdef unsigned char[::1,:] mem_view = <unsigned char[:rows:1,:cols]>data
    dtype = 'uint8'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize]))

#
# complex double
#

@cython.boundscheck(False)
cdef np.ndarray[double complex, ndim=2] ndarray_complex_double():
    return np.empty((0,0), dtype='complex128')

@cython.boundscheck(False)
cdef np.ndarray[double complex, ndim=2] ndarray_complex_double_C(double complex *data, long rows, long cols, long row_stride, long col_stride):
    cdef double complex[:,:] mem_view = <double complex[:rows,:cols]>data
    dtype = 'complex128'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[double complex, ndim=2] ndarray_complex_double_F(double complex *data, long rows, long cols, long row_stride, long col_stride):
    cdef double complex[::1,:] mem_view = <double complex[:rows:1,:cols]>data
    dtype = 'complex128'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[double complex, ndim=2] ndarray_copy_complex_double_C(const double complex *data, long rows, long cols, long row_stride, long col_stride):
    cdef double complex[:,:] mem_view = <double complex[:rows,:cols]>data
    dtype = 'complex128'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize]))

@cython.boundscheck(False)
cdef np.ndarray[double complex, ndim=2] ndarray_copy_complex_double_F(const double complex *data, long rows, long cols, long row_stride, long col_stride):
    cdef double complex[::1,:] mem_view = <double complex[:rows:1,:cols]>data
    dtype = 'complex128'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize]))

#
# complex long double
#

@cython.boundscheck(False)
cdef np.ndarray[long double complex, ndim=2] ndarray_complex_long_double():
    return np.empty((0,0), dtype='clongdouble')

@cython.boundscheck(False)
cdef np.ndarray[long double complex, ndim=2] ndarray_complex_long_double_C(long double complex *data, long rows, long cols, long row_stride, long col_stride):
    cdef long double complex[:,:] mem_view = <long double complex[:rows,:cols]>data
    dtype = 'clongdouble'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[long double complex, ndim=2] ndarray_complex_long_double_F(long double complex *data, long rows, long cols, long row_stride, long col_stride):
    cdef long double complex[::1,:] mem_view = <long double complex[:rows:1,:cols]>data
    dtype = 'clongdouble'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[long double complex, ndim=2] ndarray_copy_complex_long_double_C(const long double complex *data, long rows, long cols, long row_stride, long col_stride):
    cdef long double complex[:,:] mem_view = <long double complex[:rows,:cols]>data
    dtype = 'clongdouble'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize]))

@cython.boundscheck(False)
cdef np.ndarray[long double complex, ndim=2] ndarray_copy_complex_long_double_F(const long double complex *data, long rows, long cols, long row_stride, long col_stride):
    cdef long double complex[::1,:] mem_view = <long double complex[:rows:1,:cols]>data
    dtype = 'clongdouble'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize]))

#
# complex float
#

@cython.boundscheck(False)
cdef np.ndarray[float complex, ndim=2] ndarray_complex_float():
    return np.empty((0,0), dtype='complex64')

@cython.boundscheck(False)
cdef np.ndarray[float complex, ndim=2] ndarray_complex_float_C(float complex *data, long rows, long cols, long row_stride, long col_stride):
    cdef float complex[:,:] mem_view = <float complex[:rows,:cols]>data
    dtype = 'complex64'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[float complex, ndim=2] ndarray_complex_float_F(float complex *data, long rows, long cols, long row_stride, long col_stride):
    cdef float complex[::1,:] mem_view = <float complex[:rows:1,:cols]>data
    dtype = 'complex64'
    cdef int itemsize = np.dtype(dtype).itemsize
    return as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize])

@cython.boundscheck(False)
cdef np.ndarray[float complex, ndim=2] ndarray_copy_complex_float_C(const float complex *data, long rows, long cols, long row_stride, long col_stride):
    cdef float complex[:,:] mem_view = <float complex[:rows,:cols]>data
    dtype = 'complex64'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="C"), strides=[row_stride*itemsize, col_stride*itemsize]))

@cython.boundscheck(False)
cdef np.ndarray[float complex, ndim=2] ndarray_copy_complex_float_F(const float complex *data, long rows, long cols, long row_stride, long col_stride):
    cdef float complex[::1,:] mem_view = <float complex[:rows:1,:cols]>data
    dtype = 'complex64'
    cdef int itemsize = np.dtype(dtype).itemsize
    return np.copy(as_strided(np.asarray(mem_view, dtype=dtype, order="F"), strides=[row_stride*itemsize, col_stride*itemsize]))
