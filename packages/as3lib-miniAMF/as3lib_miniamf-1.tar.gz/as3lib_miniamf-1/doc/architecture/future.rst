==================
Future Development
==================

This software is essentially finished.  Mini-AMF provides complete
support for encoding and decoding AMF versions 0 and 3.  What with the
general deprecation of Flash on the Web, I do not expect that there
will be newer versions of AMF to support.

The older PyAMF_ software also supported types peculiar to
`Adobe Flex`_, had direct support for AMF-based RPC ("remoting"),
and contained adapter classes for integration with several ORMs and
web frameworks.  All of that has been removed, primarily in the name of
making it easier to support Python 3, and secondarily because the
adapter classes were all broken when used with the current versions of
their frameworks.  I have no plans to add any of that back; I think
server integration is properly a separate package, or perhaps several
packages, one per framework.

PyAMF also included a C extension module for speed.  The source code
to this module is still included in Mini-AMF, but it is broken and has
been disabled by default (you can activate it by giving ``setup.py``
the command line option ``--with-accel``).  I may eventually get
around to fixing it.

.. _PyAMF: https://github.com/hydralabs/pyamf
.. _Adobe Flex: https://en.wikipedia.org/wiki/Apache_Flex
