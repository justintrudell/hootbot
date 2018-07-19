import itertools


def grouper(iterable, n):
    """
    Splits an iterable into groups of 'n'.
    :param iterable: The iterable to be split.
    :param n: The amount of items desired in each group.
    :return: Yields the input list as a new list, itself containing lists of 'n' items.
    """
    """Splits a list into groups of three."""
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk
