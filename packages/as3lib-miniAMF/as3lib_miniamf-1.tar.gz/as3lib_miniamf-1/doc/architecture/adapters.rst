*********************
  Adapter Framework 
*********************

.. topic:: Introduction

   The Adapter Framework allows Mini-AMF to integrate nicely with other Python
   libraries. This includes setting up type conversions, class mappings, etc.


Adapters Overview
=================

We currently have adapters for some of Python's extended data structure types:

- :py:mod:`array`
- :py:mod:`collections`
- :py:mod:`decimal`
- :py:mod:`sets`
- :py:mod:`weakref`

Extended types are converted to basic data types that AMF can serialize.  An
``array.array``, for instance, will arrive on the far end as a ``list``.


How It Works
============

The adapter framework hooks into Python's module loader, so you do not need
to explicitly load adapter modules.  When you import both ``miniamf`` and a
library that Mini-AMF provides adapters for, the adapters will be
activated.  You can do this in either order:

.. code-block:: python

   import array
   import miniamf

or

.. code-block:: python

   import miniamf
   import array


Building Your Own Adapter
=========================

Your custom module:

.. literalinclude:: examples/adapters/mymodule.py
   :linenos:

Glue code:

.. literalinclude:: examples/adapters/myadapter.py
   :linenos:
