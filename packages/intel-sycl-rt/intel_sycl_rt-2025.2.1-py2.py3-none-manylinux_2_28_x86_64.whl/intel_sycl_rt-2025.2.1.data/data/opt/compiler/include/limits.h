/*
   Copyright (C) 2014 Intel Corporation

   This software and the related documents are Intel copyrighted materials, and
   your use of them is governed by the express license under which they were
   provided to you ("License"). Unless the License provides otherwise, you may
   not use, modify, copy, publish, distribute, disclose or transmit this
   software or the related documents without Intel's prior written permission.

   This software and the related documents are provided as is, with no express
   or implied warranties, other than those that are expressly stated in the
   License.
*/

/* limits.h - Standard header for integer sizes */

/*
   Copyright (c) 2009 Chris Lattner

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in
   all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
   THE SOFTWARE.
*/

// System headers include a number of constants from POSIX in <limits.h>.
// Include it if it exists.

// Use QNX SDK <limits.h> in freestanding mode for QNX 64 bit
#if (__STDC_HOSTED__ || defined(__QNX__)) && \
    defined(__has_include_next) && __has_include_next(<limits.h>)

// The system limits.h may, in turn, try to #include_next GCC's limits.h
#if defined __GNUC__ && !defined _GCC_LIMITS_H_
#define _GCC_LIMITS_H_
#ifndef _LIBC_LIMITS_H_
#define _GCC_NEXT_LIMITS_H
#endif /* _LIBC_LIMITS_H_ */
#include_next <limits.h>
#undef _GCC_NEXT_LIMITS_H
#else
#include_next <limits.h>
#endif /* defined __GNUC__) ... */
#endif /* __STDC_HOSTED__ && ... */

// Do not include Intel(R) compiler provided <limits.h> for QNX,
// use QNX SDK <limits.h> only.
#if !(defined(__INTEL_COMPILER) || defined(__INTEL_LLVM_COMPILER)) || \
    !defined(__QNX__)

// Only put the file inclusion guards around this portion of the include
// file. If there are a bunch of these in the include chain, we want to
// let those all get done by the include_nexts above, and not artificially
// stopped by an include guard.

#ifndef __CLANG_LIMITS_H
#define __CLANG_LIMITS_H

#undef  SCHAR_MIN
#undef  SCHAR_MAX
#undef  UCHAR_MAX
#undef  SHRT_MIN
#undef  SHRT_MAX
#undef  USHRT_MAX
#undef  INT_MIN
#undef  INT_MAX
#undef  UINT_MAX
#undef  LONG_MIN
#undef  LONG_MAX
#undef  ULONG_MAX

#undef  CHAR_BIT
#undef  CHAR_MIN
#undef  CHAR_MAX

// C90/99 5.2.4.2.1
#define SCHAR_MAX __SCHAR_MAX__
#define SHRT_MAX  __SHRT_MAX__
#define INT_MAX   __INT_MAX__
#define LONG_MAX  __LONG_MAX__

#define SCHAR_MIN (-__SCHAR_MAX__-1)
#define SHRT_MIN  (-__SHRT_MAX__ -1)
#define INT_MIN   (-__INT_MAX__  -1)
#define LONG_MIN  (-__LONG_MAX__ -1L)

#define UCHAR_MAX (__SCHAR_MAX__*2  +1)
#define USHRT_MAX (__SHRT_MAX__ *2  +1)
#define UINT_MAX  (__INT_MAX__  *2U +1U)
#define ULONG_MAX (__LONG_MAX__ *2UL+1UL)

#define CHAR_BIT  __CHAR_BIT__

#ifdef __CHAR_UNSIGNED__ /* -funsigned-char */
#define CHAR_MIN 0
#define CHAR_MAX UCHAR_MAX
#else
#define CHAR_MIN SCHAR_MIN
#define CHAR_MAX __SCHAR_MAX__
#endif

// C99 5.2.4.2.1: Added long long
#undef  LLONG_MIN
#undef  LLONG_MAX
#undef  ULLONG_MAX

#define LLONG_MAX  __LONG_LONG_MAX__
#define LLONG_MIN  (-__LONG_LONG_MAX__-1LL)
#define ULLONG_MAX (__LONG_LONG_MAX__*2ULL+1ULL)

#if defined(__GNU_LIBRARY__) ? defined(__USE_GNU) : !defined(__STRICT_ANSI__)

#undef   LONG_LONG_MIN
#undef   LONG_LONG_MAX
#undef   ULONG_LONG_MAX

#define LONG_LONG_MAX  __LONG_LONG_MAX__
#define LONG_LONG_MIN  (-__LONG_LONG_MAX__-1LL)
#define ULONG_LONG_MAX (__LONG_LONG_MAX__*2ULL+1ULL)
#endif

#endif /* !(__INTEL_COMPILER || __INTEL_LLVM_COMPILER) || !__QNX__ */
#endif /* __CLANG_LIMITS_H */
