gmpy2 is an optimized, C-coded Python extension module that supports fast
multiple-precision arithmetic.  gmpy2 is based on the original gmpy module.
gmpy2 adds support for correctly rounded multiple-precision real arithmetic
(using the MPFR library) and complex arithmetic (using the MPC library).

Version 2.2
-----------

gmpy2 2.2.2
-----------

* Many bug fixes.
* Initial support for free-threaded builds.

gmpy2 2.2.1
-----------

* Bug fix: use C int instead of C char for some internal code.
* Bug fix: add xmpz.bit_count method.

gmpy2 2.2.0
-----------

gmpy2 2.2.0 is now available with support for Python 3.7 to 3.13.

* Support for thread-safe contexts and context methods has been improved.
* Interoperability with Cython extensions has been updated.
* Extensive improvements have been made to the build and testing processes.
* Many bug fixes.
* Extensive documentation cleanup.

Availability
------------

gmpy2 is available at https://pypi.python.org/pypi/gmpy2/

Documentation is available at https://gmpy2.readthedocs.io/en/latest/
