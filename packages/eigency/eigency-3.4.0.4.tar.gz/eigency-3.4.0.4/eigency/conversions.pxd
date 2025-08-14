cimport numpy as np


# Array with limit 2D
cdef api np.ndarray[long double, ndim=2] ndarray_long_double()
cdef api np.ndarray[long double, ndim=2] ndarray_long_double_C(long double *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[long double, ndim=2] ndarray_long_double_F(long double *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[long double, ndim=2] ndarray_copy_long_double_C(const long double *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[long double, ndim=2] ndarray_copy_long_double_F(const long double *data, long rows, long cols, long outer_stride, long inner_stride)

cdef api np.ndarray[double, ndim=2] ndarray_double()
cdef api np.ndarray[double, ndim=2] ndarray_double_C(double *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[double, ndim=2] ndarray_double_F(double *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[double, ndim=2] ndarray_copy_double_C(const double *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[double, ndim=2] ndarray_copy_double_F(const double *data, long rows, long cols, long outer_stride, long inner_stride)

cdef api np.ndarray[float, ndim=2] ndarray_float()
cdef api np.ndarray[float, ndim=2] ndarray_float_C(float *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[float, ndim=2] ndarray_float_F(float *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[float, ndim=2] ndarray_copy_float_C(const float *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[float, ndim=2] ndarray_copy_float_F(const float *data, long rows, long cols, long outer_stride, long inner_stride)

cdef api np.ndarray[long long, ndim=2] ndarray_long_long()
cdef api np.ndarray[long long, ndim=2] ndarray_long_long_C(long long *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[long long, ndim=2] ndarray_long_long_F(long long *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[long long, ndim=2] ndarray_copy_long_long_C(const long long *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[long long, ndim=2] ndarray_copy_long_long_F(const long long *data, long rows, long cols, long outer_stride, long inner_stride)

cdef api np.ndarray[long, ndim=2] ndarray_long()
cdef api np.ndarray[long, ndim=2] ndarray_long_C(long *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[long, ndim=2] ndarray_long_F(long *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[long, ndim=2] ndarray_copy_long_C(const long *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[long, ndim=2] ndarray_copy_long_F(const long *data, long rows, long cols, long outer_stride, long inner_stride)

cdef api np.ndarray[unsigned long long, ndim=2] ndarray_ulong_long()
cdef api np.ndarray[unsigned long long, ndim=2] ndarray_ulong_long_C(unsigned long long *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[unsigned long long, ndim=2] ndarray_ulong_long_F(unsigned long long *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[unsigned long long, ndim=2] ndarray_copy_ulong_long_C(const unsigned long long *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[unsigned long long, ndim=2] ndarray_copy_ulong_long_F(const unsigned long long *data, long rows, long cols, long outer_stride, long inner_stride)

cdef api np.ndarray[unsigned long, ndim=2] ndarray_ulong()
cdef api np.ndarray[unsigned long, ndim=2] ndarray_ulong_C(unsigned long *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[unsigned long, ndim=2] ndarray_ulong_F(unsigned long *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[unsigned long, ndim=2] ndarray_copy_ulong_C(const unsigned long *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[unsigned long, ndim=2] ndarray_copy_ulong_F(const unsigned long *data, long rows, long cols, long outer_stride, long inner_stride)

cdef api np.ndarray[int, ndim=2] ndarray_int()
cdef api np.ndarray[int, ndim=2] ndarray_int_C(int *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[int, ndim=2] ndarray_int_F(int *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[int, ndim=2] ndarray_copy_int_C(const int *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[int, ndim=2] ndarray_copy_int_F(const int *data, long rows, long cols, long outer_stride, long inner_stride)

cdef api np.ndarray[unsigned int, ndim=2] ndarray_uint()
cdef api np.ndarray[unsigned int, ndim=2] ndarray_uint_C(unsigned int *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[unsigned int, ndim=2] ndarray_uint_F(unsigned int *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[unsigned int, ndim=2] ndarray_copy_uint_C(const unsigned int *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[unsigned int, ndim=2] ndarray_copy_uint_F(const unsigned int *data, long rows, long cols, long outer_stride, long inner_stride)

cdef api np.ndarray[short, ndim=2] ndarray_short()
cdef api np.ndarray[short, ndim=2] ndarray_short_C(short *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[short, ndim=2] ndarray_short_F(short *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[short, ndim=2] ndarray_copy_short_C(const short *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[short, ndim=2] ndarray_copy_short_F(const short *data, long rows, long cols, long outer_stride, long inner_stride)

cdef api np.ndarray[unsigned short, ndim=2] ndarray_ushort()
cdef api np.ndarray[unsigned short, ndim=2] ndarray_ushort_C(unsigned short *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[unsigned short, ndim=2] ndarray_ushort_F(unsigned short *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[unsigned short, ndim=2] ndarray_copy_ushort_C(const unsigned short *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[unsigned short, ndim=2] ndarray_copy_ushort_F(const unsigned short *data, long rows, long cols, long outer_stride, long inner_stride)

cdef api np.ndarray[signed char, ndim=2] ndarray_schar()
cdef api np.ndarray[signed char, ndim=2] ndarray_schar_C(signed char *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[signed char, ndim=2] ndarray_schar_F(signed char *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[signed char, ndim=2] ndarray_copy_schar_C(const signed char *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[signed char, ndim=2] ndarray_copy_schar_F(const signed char *data, long rows, long cols, long outer_stride, long inner_stride)

cdef api np.ndarray[unsigned char, ndim=2] ndarray_uchar()
cdef api np.ndarray[unsigned char, ndim=2] ndarray_uchar_C(unsigned char *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[unsigned char, ndim=2] ndarray_uchar_F(unsigned char *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[unsigned char, ndim=2] ndarray_copy_uchar_C(const unsigned char *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[unsigned char, ndim=2] ndarray_copy_uchar_F(const unsigned char *data, long rows, long cols, long outer_stride, long inner_stride)

cdef api np.ndarray[long double complex, ndim=2] ndarray_complex_long_double()
cdef api np.ndarray[long double complex, ndim=2] ndarray_complex_long_double_C(long double complex *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[long double complex, ndim=2] ndarray_complex_long_double_F(long double complex *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[long double complex, ndim=2] ndarray_copy_complex_long_double_C(const long double complex *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[long double complex, ndim=2] ndarray_copy_complex_long_double_F(const long double complex *data, long rows, long cols, long outer_stride, long inner_stride)

cdef api np.ndarray[double complex, ndim=2] ndarray_complex_double()
cdef api np.ndarray[double complex, ndim=2] ndarray_complex_double_C(double complex *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[double complex, ndim=2] ndarray_complex_double_F(double complex *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[double complex, ndim=2] ndarray_copy_complex_double_C(const double complex *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[double complex, ndim=2] ndarray_copy_complex_double_F(const double complex *data, long rows, long cols, long outer_stride, long inner_stride)

cdef api np.ndarray[float complex, ndim=2] ndarray_complex_float()
cdef api np.ndarray[float complex, ndim=2] ndarray_complex_float_C(float complex *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[float complex, ndim=2] ndarray_complex_float_F(float complex *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[float complex, ndim=2] ndarray_copy_complex_float_C(const float complex *data, long rows, long cols, long outer_stride, long inner_stride)
cdef api np.ndarray[float complex, ndim=2] ndarray_copy_complex_float_F(const float complex *data, long rows, long cols, long outer_stride, long inner_stride)
