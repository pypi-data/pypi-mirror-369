from miniamf.adapters import register_adapter


def when_imported(mod):
    """
    This function is called immediately after mymodule has been
    imported.  It configures Mini-AMF to encode a list when an instance
    of mymodule.CustomClass is encountered.
    """
    import miniamf

    miniamf.add_type(mod.CustomClass, lambda obj: list(obj))


register_adapter('mymodule', when_imported)
