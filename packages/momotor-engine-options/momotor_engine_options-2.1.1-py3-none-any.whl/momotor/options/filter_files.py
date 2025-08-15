import collections.abc
from momotor.bundles.elements.files import FilesType, File
from momotor.bundles.utils.filters import F

__all__ = ["filter_files", "ifilter_files"]


def file_class_name_filters(class_name) -> collections.abc.Iterable[F]:
    if '#' in class_name:
        class_, name = class_name.split('#', 1)
    else:
        class_, name = class_name, None

    if name:
        yield F(name__glob=name.strip())

    if class_:
        yield F(class_=class_.strip())


def filter_files(files: FilesType, class_name: str) -> FilesType:
    """ Filter a :py:class:`~momotor.bundles.utils.filters.FilterableTuple` of
    :py:class:`~momotor.bundles.elements.files.File` objects on the `name` and `class`
    attributes.

    The `class_name` argument contains the class and name to filter on, in the format
    `<class>`\ ``#``\ `<name>`. The `name` part can contain wildcards, and is optional.

    :param files: List of files to filter
    :param class_name: class/name to filter on
    :return:
    """
    return files.filter(*file_class_name_filters(class_name))


def ifilter_files(files: FilesType, class_name: str) -> collections.abc.Iterable[File]:
    """ Return an iterable that filters a :py:class:`~momotor.bundles.utils.filters.FilterableTuple` of
    :py:class:`~momotor.bundles.elements.files.File` objects on the `name` and `class`
    attributes.

    The `class_name` argument contains the class and name to filter on, in the format
    `<class>`\ ``#``\ `<name>`. The `name` part can contain wildcards, and is optional.

    :param files: List of files to filter
    :param class_name: class/name to filter on
    :return:
    """
    return files.ifilter(*file_class_name_filters(class_name))
