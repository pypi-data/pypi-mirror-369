__all__ = ['annotate_docstring']


def annotate_docstring(*args, **kwargs):
    """ Decorator to help write better docstrings.

    The arguments of the decorator are applied using :py:meth:`str.format`
    to the __doc__ of the function, class or method decorated.

    Examples:

    .. code:: python

       @annotate_docstring(placeholder='test')
       def some_function():
           \"\"\" This is a {placeholder}. \"\"\"
           pass

       @annotate_docstring(placeholder='test')
       class SomeClass:
          \"\"\" This is a {placeholder}. \"\"\"

           @annotate_docstring(placeholder='test')
           def some_method(self):
               \"\"\" This is a {placeholder}. \"\"\"
               pass

    In the example above, all docstrings will read:

    .. code:: text

       This is a test.

    :param args: the arguments for :py:meth:`str.format`
    :param kwargs: the keyword arguments for :py:meth:`str.format`
    :return: the decorated object with annotated doc string
    """

    def decorator(obj):
        if obj.__doc__ is not None:
            obj.__doc__ = obj.__doc__.format(*args, **kwargs)

        return obj

    return decorator
