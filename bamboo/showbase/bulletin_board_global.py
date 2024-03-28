"""Instantiates the global :class:`~.BulletinBoard.BulletinBoard` object."""

__all__ = ['bulletinBoard']

from . import bulletin_board

#: The global :class:`~.BulletinBoard.BulletinBoard` object.
bulletinBoard = bulletin_board.BulletinBoard()
