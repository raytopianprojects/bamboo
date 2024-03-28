"""Instantiates global DirectNotify used in bamboo."""

__all__ = ['directNotify', 'giveNotify']

from bamboo.directnotify import DirectNotify

#: The global :class:`~.DirectNotify.DirectNotify` object.
directNotify = DirectNotify()

#: Shorthand function for adding a DirectNotify category to a given class
#: object.  Alias of `.DirectNotify.DirectNotify.giveNotify`.
giveNotify = directNotify.giveNotify
