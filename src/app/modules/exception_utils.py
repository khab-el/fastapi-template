from __future__ import annotations

import typing as t


def leaf_generator(exc: ExceptionGroup, tbs: t.Iterable = None):
    """Parse exception group."""
    if tbs is None:
        tbs = []

    tbs.append(exc.__traceback__)
    if isinstance(exc, BaseExceptionGroup):
        for e in exc.exceptions:
            yield from leaf_generator(e, tbs)
    else:
        # exc is a leaf exception and its traceback
        # is the concatenation of the traceback
        # segments in tbs.

        # Note: the list returned (tbs) is reused in each iteration
        # through the generator. Make a copy if your use case holds
        # on to it beyond the current iteration or mutates its contents.

        yield exc, tbs
    tbs.pop()
