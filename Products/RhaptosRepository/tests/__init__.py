# -*- coding: utf-8 -*-
import sys

if sys.version_info >= (2, 7):
    # improved unittest package from 2.7's standard library
    import unittest
else:
    try:
        # external release of same package for older versions
        import unittest2 as unittest
    except ImportError:
        sys.exit('Error: You have to install unittest2')
