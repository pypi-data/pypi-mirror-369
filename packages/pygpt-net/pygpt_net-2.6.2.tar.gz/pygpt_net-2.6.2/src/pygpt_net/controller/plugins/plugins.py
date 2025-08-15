#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2025.07.26 18:00:00                  #
# ================================================== #

from typing import List, Dict, Any

from PySide6.QtGui import QAction

from pygpt_net.core.types import (
    MODE_AGENT,
)
from pygpt_net.controller.plugins.presets import Presets
from pygpt_net.controller.plugins.settings import Settings
from pygpt_net.core.events import Event
from pygpt_net.item.ctx import CtxItem
from pygpt_net.utils import trans


class Plugins:
    def __init__(self, window=None):
        """
        Plugins controller

        :param window: Window instance
        """
        self.window = window
        self.settings = Settings(window)
        self.presets = Presets(window)
        self.enabled = {}

    def setup(self):
        """Set up plugins"""
        self.setup_menu()
        self.setup_ui()

        try:
            self.window.core.plugins.clean_presets()  # clean presets (remove invalid keys)
        except Exception as e:
            self.window.core.debug.error(e)

        self.presets.preset_to_current()  # load from presets
        self.reconfigure(silent=True)  # load plugins settings

    def reconfigure(self, silent: bool = False):
        """
        Reconfigure plugins

        :param silent: silent mode
        """
        self.setup_config(silent=silent)
        self.update()
        self.presets.update_menu()

    def setup_ui(self):
        """Set up plugins UI"""
        for id in self.window.core.plugins.get_ids():
            try:
                # setup UI
                self.window.core.plugins.get(id).setup_ui()
            except AttributeError:
                pass

        # show/hide UI elements
        self.handle_types()

        # tmp dump locales
        # self.window.core.plugins.dump_locales()

    def setup_menu(self):
        """Set up plugins menu"""
        for id in self.window.core.plugins.get_ids():
            if id in self.window.ui.menu['plugins']:
                continue
            name = self.window.core.plugins.get_name(id)
            tooltip = self.window.core.plugins.get_desc(id)
            self.window.ui.menu['plugins'][id] = QAction(name, self.window, checkable=True)
            self.window.ui.menu['plugins'][id].triggered.connect(
                lambda checked=None, id=id: self.toggle(id))
            self.window.ui.menu['plugins'][id].setToolTip(tooltip)
            self.window.ui.menu['menu.plugins'].addAction(self.window.ui.menu['plugins'][id])

    def setup_config(self, silent: bool = False):
        """
        Enable plugins from config

        :param silent: silent mode
        """
        for id in self.window.core.plugins.get_ids():
            if id in self.window.core.config.get('plugins_enabled'):
                if self.window.core.config.data['plugins_enabled'][id]:
                    self.enable(id)
                else:
                    self.disable(id, silent=silent)
            else:
                self.disable(id, silent=silent)

    def update(self):
        """Update plugins menu"""
        for id in self.window.ui.menu['plugins']:
            self.window.ui.menu['plugins'][id].setChecked(False)

        for id in self.enabled:
            if self.enabled[id]:
                self.window.ui.menu['plugins'][id].setChecked(True)

        self.handle_types()
        self.window.controller.ui.mode.update()  # refresh active elements
        self.window.controller.ui.vision.update()  # vision camera

    def enable(self, id: str):
        """
        Enable plugin

        :param id: plugin id
        """
        if self.window.core.plugins.is_registered(id):
            self.enabled[id] = True
            self.window.core.plugins.enable(id)

            # dispatch plugin enable event
            event = Event(Event.ENABLE, {
                'value': id,
            })
            self.window.dispatch(event)

            # update audio menu
            if self.has_type(id, 'audio.input') or self.has_type(id, 'audio.output'):
                self.window.controller.audio.update()

        self.update_info()
        self.update()

    def disable(self, id: str, silent: bool = False):
        """
        Disable plugin

        :param id: plugin id
        :param silent: silent mode
        """
        if self.window.core.plugins.is_registered(id):
            self.enabled[id] = False
            self.window.core.plugins.disable(id)

            if not silent:
                # dispatch plugin disable event
                event = Event(Event.DISABLE, {
                    'value': id,
                })
                self.window.dispatch(event, all=True)  # dispatch to all plugins, including disabled now

                # update audio menu
                if self.has_type(id, 'audio.input') or self.has_type(id, 'audio.output'):
                    self.window.controller.audio.update()

        self.update_info()
        self.update()

    def is_enabled(self, id: str):
        """
        Check if plugin is enabled

        :param id: plugin id
        :return: True if enabled
        :rtype: bool
        """
        if self.window.core.plugins.is_registered(id):
            if id in self.enabled:
                return self.enabled[id]
        return False

    def toggle(self, id: str):
        """
        Toggle plugin

        :param id: plugin id
        """
        if self.window.core.plugins.is_registered(id):
            if self.is_enabled(id):
                self.disable(id)
            else:
                self.enable(id)

        self.handle_types()
        self.window.controller.ui.update_tokens()  # refresh tokens
        self.window.controller.ui.mode.update()  # refresh active elements
        self.window.controller.ui.vision.update()  # vision camera
        self.window.controller.attachment.update()  # attachments update
        self.presets.save_current()  # save settings in current preset

    def set_by_tab(self, idx: int):
        """
        Set current plugin by tab index

        :param idx: tab index
        """
        plugin_idx = 0
        for id in self.window.core.plugins.get_ids():
            if self.window.core.plugins.has_options(id):
                if plugin_idx == idx:
                    self.settings.current_plugin = id
                    break
            plugin_idx += 1
        current = self.window.ui.models['plugin.list'].index(idx, 0)
        self.window.ui.nodes['plugin.list'].setCurrentIndex(current)

    def get_tab_idx(self, plugin_id: str) -> int:
        """
        Get plugin tab index

        :param plugin_id: plugin id
        :return: tab index
        """
        plugin_idx = None
        i = 0
        for id in self.window.core.plugins.get_ids():
            if id == plugin_id:
                plugin_idx = i
                break
            i += 1
        return plugin_idx

    def unregister(self, id: str):
        """
        Unregister plugin

        :param id: plugin id
        """
        self.window.core.plugins.unregister(id)
        if id in self.enabled:
            self.enabled.pop(id)

    def destroy(self):
        """Destroy plugins workers"""

        # send force stop event
        event = Event(Event.FORCE_STOP, {})
        self.window.dispatch(event)

        for id in self.window.core.plugins.get_ids():
            try:
                # destroy plugin workers
                self.window.core.plugins.destroy(id)
            except AttributeError:
                pass

    def has_type(self, id: str, type: str):
        """
        Check if plugin has type
        :param id: plugin ID
        :param type: type to check
        :return: True if has type
        """
        if self.window.core.plugins.is_registered(id):
            if type in self.window.core.plugins.get(id).type:
                return True
        return False

    def is_type_enabled(self, type: str) -> bool:
        """
        Check if plugin type is enabled

        :param type: plugin type
        :return: True if enabled
        """
        enabled = False
        for id in self.window.core.plugins.get_ids():
            if type in self.window.core.plugins.get(id).type and self.is_enabled(id):
                enabled = True
                break
        return enabled

    def handle_types(self):
        """Handle plugin type"""
        for type in self.window.core.plugins.allowed_types:

            enabled = self.is_type_enabled(type)

            if type == 'audio.input':
                self.window.controller.audio.handle_audio_input(enabled)

            elif type == 'audio.output':
                self.window.controller.audio.handle_audio_output(enabled)

            elif type == 'schedule':
                if enabled:
                    self.window.ui.plugin_addon['schedule'].setVisible(True)
                    # get tasks count by throwing "get option" event
                    num = 0
                    data = {
                        'name': 'scheduled_tasks_count',
                        'value': num,
                    }
                    event = Event(Event.PLUGIN_OPTION_GET, data)
                    self.window.dispatch(event)
                    if 'value' in event.data:
                        num = event.data['value']
                    # update tray menu
                    self.window.ui.tray.update_schedule_tasks(num)
                else:
                    self.window.ui.plugin_addon['schedule'].setVisible(False)
                    self.window.ui.tray.hide_schedule_menu()

    def on_update(self):
        """Called on update"""
        for id in self.window.core.plugins.get_ids():
            if self.is_enabled(id):
                try:
                    self.window.core.plugins.get(id).on_update()
                except AttributeError:
                    pass

    def on_post_update(self):
        """Called on post update"""
        for id in self.window.core.plugins.get_ids():
            if self.is_enabled(id):
                try:
                    self.window.core.plugins.get(id).on_post_update()
                except AttributeError:
                    pass

    def update_info(self):
        """Update plugins info"""
        enabled_list = []
        for id in self.window.core.plugins.get_ids():
            if self.is_enabled(id):
                enabled_list.append(self.window.core.plugins.get(id).name)
        tooltip = " + ".join(enabled_list)

        count_str = ""
        c = 0
        if len(self.window.core.plugins.get_ids()) > 0:
            for id in self.window.core.plugins.get_ids():
                if self.is_enabled(id):
                    c += 1

        if c > 0:
            count_str = "+ " + str(c) + " " + trans('chatbox.plugins')
        self.window.ui.nodes['chat.plugins'].setText(count_str)
        self.window.ui.nodes['chat.plugins'].setToolTip(tooltip)

    def apply_cmds_all(
            self,
            ctx: CtxItem,
            cmds: List[Dict[str, Any]]
    ):
        """
        Apply all commands (inline or not)

        :param ctx: context
        :param cmds: commands
        :return: results
        """
        if self.window.core.config.get("cmd"):
            return self.apply_cmds(ctx, cmds)
        else:
            return self.apply_cmds_inline(ctx, cmds)

    def apply_cmds(
            self,
            ctx: CtxItem,
            cmds: List[Dict[str, Any]],
            all: bool = False,
            execute_only: bool = False
    ):
        """
        Apply commands

        :param ctx: CtxItem
        :param cmds: commands list
        :param all: True to apply all commands, False to apply only enabled commands
        :param execute_only: True to execute commands only, without any additional event
        """
        commands = self.window.core.command.from_commands(cmds)
        if len(commands) == 0:
            return

        # dispatch command execute event
        event = Event(Event.CMD_EXECUTE, {
            'commands': commands,
        })

        # don't change status if only goal update command
        self.log("Executing plugin commands...")
        mode = self.window.core.config.get('mode')
        change_status = True
        if mode == MODE_AGENT:
            if len(cmds) == 1 and cmds[0]["cmd"] == "goal_update":
                change_status = False
        if change_status:
            self.window.update_status(trans('status.cmd.wait'))

        ctx.results = []
        event.ctx = ctx
        self.window.controller.command.dispatch(
            event,
            all=all,
            execute_only=execute_only,
        )
        # reset status if nothing executed
        current = self.window.ui.get_status()
        if current == trans('status.cmd.wait'):
            self.window.update_status("")

        return ctx.results

    def apply_cmds_inline(
            self,
            ctx: CtxItem,
            cmds: List[Dict[str, Any]]
    ):
        """
        Apply inline commands

        :param ctx: CtxItem
        :param cmds: commands list
        """
        commands = self.window.core.command.from_commands(cmds)
        if len(commands) == 0:
            return

        # dispatch inline command event
        event = Event(Event.CMD_INLINE, {
            'commands': commands,
        })

        # don't change status if only goal update command
        self.log("Executing inline plugin commands...")
        mode = self.window.core.config.get('mode')
        change_status = True
        if mode == MODE_AGENT:
            if len(cmds) == 1 and cmds[0]["cmd"] == "goal_update":
                change_status = False
        if change_status:
            self.window.update_status(trans('status.cmd.wait'))

        ctx.results = []
        event.ctx = ctx
        self.window.controller.command.dispatch(event)

        # reset status if nothing executed
        current = self.window.ui.get_status()
        if current == trans('status.cmd.wait'):
            self.window.update_status("")

        return ctx.results

    def reload(self):
        """Reload plugins"""
        self.window.core.plugins.reload_all()  # reload all plugin options
        self.setup()
        self.settings.setup()
        self.update()

    def save_all(self):
        """Save plugin settings"""
        for id in self.window.core.plugins.plugins.keys():
            plugin = self.window.core.plugins.plugins[id]
            options = plugin.setup()  # get plugin options

            # add plugin to global config data if not exists
            if id not in self.window.core.config.get('plugins'):
                self.window.core.config.data['plugins'][id] = {}

            # update config with current values
            for key in options:
                self.window.core.config.data['plugins'][id][key] = self.window.core.plugins.plugins[id].options[key]['value']

            # remove key from config if plugin option not exists
            for key in list(self.window.core.config.data['plugins'].keys()):
                if key not in self.window.core.plugins.plugins:
                    self.window.core.config.data['plugins'].pop(key)

        # save preset
        self.window.controller.plugins.presets.save_current()

        # save config
        self.window.core.config.save()

    def log(self, data: Any):
        """
        Log data to debug

        :param data: Data to log
        """
        self.window.core.debug.info(data)
