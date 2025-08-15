from momotor.bundles import BundleError


class CircularDependencies(BundleError):
    """ Circular dependencies detected in the steps.

    This exception is raised when the steps of a bundle have circular dependencies.

    Subclass of :py:exc:`momotor.bundles.BundleError`.
    """
    pass


class InvalidDependencies(BundleError):
    """ Invalid dependencies detected in the steps.

    This exception is raised when the steps of a bundle have invalid dependencies, for example,
    when referencing non-existent steps ids or using an invalid syntax.

    Subclass of :py:exc:`momotor.bundles.BundleError`.
    """
    pass
