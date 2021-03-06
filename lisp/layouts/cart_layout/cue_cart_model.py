# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
#
# Linux Show Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Linux Show Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>.

from sortedcontainers import SortedDict

from lisp.core.model import ModelException
from lisp.core.model_adapter import ModelAdapter


class CueCartModel(ModelAdapter):
    def __init__(self, model, rows, columns):
        super().__init__(model)

        self.__cues = SortedDict()
        self.__rows = rows
        self.__columns = columns

    def flat(self, index):
        """If index is multidimensional return a flatted version.

        :rtype: int
        """
        try:
            page, row, column = index
            page *= self.__rows * self.__columns
            row *= self.__columns
            return page + row + column
        except TypeError:
            return index

    def first_empty(self):
        """Return the first empty index."""
        n = -1
        for n, index in enumerate(self.__cues.keys()):
            if n != index:
                return n

        return n + 1

    def item(self, index):
        index = self.flat(index)
        return self.__cues.get(index)

    def insert(self, item, index):
        index = self.flat(index)

        if index not in self.__cues:
            item.index = index

        self.add(item)

    def pop(self, index):
        index = self.flat(index)

        cue = self.__cues[index]
        self.model.remove(cue)
        return cue

    def move(self, old_index, new_index):
        old_index = self.flat(old_index)
        new_index = self.flat(new_index)

        if new_index not in self.__cues:
            self.__cues[new_index] = self.__cues.pop(old_index)
            self.__cues[new_index].index = new_index
            self.item_moved.emit(old_index, new_index)
        else:
            raise ModelException('index already used {}'.format(new_index))

    def page_edges(self, page):
        start = self.flat((page, 0, 0))
        end = self.flat((page, self.__rows, self.__columns))
        return start, end

    def remove_page(self, page, lshift=True):
        start, end = self.page_edges(page)
        for index in range(start, end + 1):
            cue = self.__cues.get(index)
            if cue is not None:
                self.remove(cue)

        if lshift:
            page_size = self.__rows * self.__columns
            for index in self.__cues.irange(minimum=end + 1):
                new_index = index - page_size
                self.__cues[new_index] = self.__cues.pop(index)
                self.__cues[new_index].index = new_index

    def iter_page(self, page):
        """Iterate over the cues of the given page"""
        start, stop = self.page_edges(page)
        for index in self.__cues.irange(start, stop):
            yield self.__cues[index]

    def _item_added(self, item):
        if item.index == -1 or item.index in self.__cues:
            item.index = self.first_empty()

        self.__cues[item.index] = item
        self.item_added.emit(item)

    def _item_removed(self, item):
        self.__cues.pop(item.index)
        self.item_removed.emit(item)

    def _model_reset(self):
        self.__cues.clear()
        self.model_reset.emit()

    def __iter__(self):
        return iter(self.__cues.values())
