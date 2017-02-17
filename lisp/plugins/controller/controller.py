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


from lisp.application import Application
from lisp.core.has_properties import Property
from lisp.core.plugin import Plugin
from lisp.cues.cue import Cue, CueAction
from lisp.modules.global_controller.global_controller_common import CommonController
from lisp.plugins.controller.controller_settings import ControllerSettings
from lisp.ui.settings.cue_settings import CueSettingsRegistry


class Controller(Plugin):

    Name = 'Controller'

    def __init__(self):
        super().__init__()
        self.__map = {}
        self.__actions_map = {}
        self.__protocols = {}

        # Register a new Cue property to store settings
        Cue.register_property('controller', Property(default={}))

        # Listen cue_model changes
        Application().cue_model.item_added.connect(self.__cue_added)
        Application().cue_model.item_removed.connect(self.__cue_removed)

        # Register settings-page
        CueSettingsRegistry().add_item(ControllerSettings)

        CommonController().controller_event.connect(self.perform_action)

    def init(self):
        CommonController().notify_new_session.emit()

    def reset(self):
        self.__map.clear()
        self.__actions_map.clear()

        CommonController().notify_new_session.emit()

    def cue_changed(self, cue, property_name, value):
        if property_name == 'controller':
            self.delete_from_map(cue)

            # for protocol in self.__protocols:
            for protocol in CommonController().protocol_types:
                for key, action in value.get(protocol.name.lower(), []):
                    if key not in self.__map:
                        print("cue_changed ", key)
                        self.__map[key] = set()

                    self.__map[key].add(cue)
                    self.__actions_map[(key, cue)] = CueAction(action)

    def delete_from_map(self, cue):
        for key in self.__map:
            self.__map[key].discard(cue)
            self.__actions_map.pop((key, cue), None)

    def perform_action(self, key, wildcards):
        # execute for actual key
        for cue in self.__map.get(key, []):
            cue.execute(self.__actions_map[(key, cue)])

        # execute for wildcard keys
        for wildcard in wildcards:
            for cue in self.__map.get(wildcard, []):
                cue.execute(self.__actions_map[(wildcard, cue)])

    def __cue_added(self, cue):
        cue.property_changed.connect(self.cue_changed)
        self.cue_changed(cue, 'controller', cue.controller)

    def __cue_removed(self, cue):
        cue.property_changed.disconnect(self.cue_changed)
        self.delete_from_map(cue)
