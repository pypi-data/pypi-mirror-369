=================
  Class Mapping
=================

Mini-AMF allows you to register aliases for remote Python classes that
can be mapped to their corresponding Actionscript classes.

In this example we use the Python classes below.

.. literalinclude:: examples/class-mapping/example-classes.py
   :linenos:

With the corresponding Actionscript 3.0 classes that were
registered in the Flash Player using the `flash.net.registerClassAlias`
utility:

.. literalinclude:: examples/class-mapping/example-classes.as
   :linenos:


Registering Classes
===================

Classes can be registered and removed using the following tools:

- :func:`miniamf.register_class`
- :func:`miniamf.unregister_class`
- :func:`miniamf.get_class_alias`
- :func:`miniamf.register_package`

Continue reading for examples of these APIs.

Single Class
------------

To register a class alias for a single class::

    >>> miniamf.register_class("org.miniamf.User", User)

Find the alias registered to the class::

    >>> print miniamf.get_class_alias(User)
    org.miniamf.User

And to unregister by alias::

    >>> miniamf.unregister_class("org.miniamf.User")

Or unregister by class::

    >>> miniamf.unregister_class(User)


Multiple Classes
----------------

If you want to register multiple classes at the same time, or all
classes in a module::

    >>> import mymodule
    >>> miniamf.register_package(mymodule, 'org.miniamf')

Now all instances of `mymodule.User` will appear in Actionscript under the
alias 'org.miniamf.User'. Same goes for `mymodule.Permission` - the
Actionscript alias is 'org.miniamf.Permission'. The reverse is also
true, any objects with the correct aliases will now be instances of the
relevant Python class.

This function respects the `__all__` attribute of the module but you can
have further control of what not to auto alias by populating the `ignore`
argument with a list of classes that should be ignored.

This function provides the ability to register the module it is being
called in, an example::

    >>> miniamf.register_package('org.miniamf')

You can also supply a list of classes to register. An example, taking the
example classes::

    >>> miniamf.register_package([User, Permission], 'org.miniamf')
