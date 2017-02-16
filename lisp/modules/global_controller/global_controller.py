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


from lisp.core.module import Module
from lisp.modules.global_controller.global_controller_settings import MidiControllerSettings, OscControllerSettings
from lisp.ui.settings.app_settings import AppSettings


class GlobalController(Module):
    """module provides global controls through protocol plugins"""
    def __init__(self):

        AppSettings.register_settings_widget(MidiControllerSettings)
        AppSettings.register_settings_widget(OscControllerSettings)
