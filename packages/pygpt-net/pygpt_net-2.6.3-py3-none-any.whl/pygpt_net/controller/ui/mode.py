#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2025.08.15 03:00:00                  #
# ================================================== #

from pygpt_net.core.types import (
    MODE_AGENT,
    MODE_AGENT_LLAMA,
    MODE_ASSISTANT,
    MODE_EXPERT,
    MODE_IMAGE,
    MODE_LLAMA_INDEX,
    MODE_VISION,
    MODE_COMPUTER,
    MODE_AGENT_OPENAI,
    MODE_COMPLETION,
)
from pygpt_net.core.tabs.tab import Tab
from pygpt_net.core.events import Event
from pygpt_net.utils import trans


class Mode:
    def __init__(self, window=None):
        """
        UI mode switch controller

        :param window: Window instance
        """
        self.window = window

    def update(self):
        """Update mode, model, preset and rest of the toolbox"""

        mode = self.window.core.config.data['mode']

        # presets
        if mode != MODE_ASSISTANT:
            self.window.ui.nodes['presets.widget'].setVisible(True)
        else:
            self.window.ui.nodes['presets.widget'].setVisible(False)

        if mode != MODE_COMPUTER:
            self.window.ui.nodes['env.widget'].setVisible(False)
        else:
            self.window.ui.nodes['env.widget'].setVisible(True)

        # presets: labels
        if mode == MODE_AGENT:
            self.window.ui.nodes['preset.agents.label'].setVisible(True)
            self.window.ui.nodes['preset.experts.label'].setVisible(False)
            self.window.ui.nodes['preset.presets.label'].setVisible(False)
        elif mode == MODE_AGENT_LLAMA:
            self.window.ui.nodes['preset.agents.label'].setVisible(True)
            self.window.ui.nodes['preset.experts.label'].setVisible(False)
            self.window.ui.nodes['preset.presets.label'].setVisible(False)
        elif mode == MODE_AGENT_OPENAI:
            self.window.ui.nodes['preset.agents.label'].setVisible(True)
            self.window.ui.nodes['preset.experts.label'].setVisible(False)
            self.window.ui.nodes['preset.presets.label'].setVisible(False)
        elif mode == MODE_EXPERT:
            self.window.ui.nodes['preset.agents.label'].setVisible(False)
            self.window.ui.nodes['preset.experts.label'].setVisible(True)
            self.window.ui.nodes['preset.presets.label'].setVisible(False)
        else:
            self.window.ui.nodes['preset.agents.label'].setVisible(False)
            self.window.ui.nodes['preset.experts.label'].setVisible(False)
            self.window.ui.nodes['preset.presets.label'].setVisible(True)

        # presets: experts
        if mode == MODE_EXPERT:
            self.window.ui.nodes['preset.editor.description'].setVisible(True)
            self.window.controller.presets.editor.toggle_tab("remote_tools", True)
        else:
            self.window.controller.presets.editor.toggle_tab("remote_tools", False)
            self.window.ui.nodes['preset.editor.description'].setVisible(False)

        if mode == MODE_COMPLETION:
            self.window.ui.nodes['preset.editor.user_name'].setVisible(True)
        else:
            self.window.ui.nodes['preset.editor.user_name'].setVisible(False)

        if mode == MODE_AGENT_OPENAI:
            self.window.ui.nodes['preset.editor.agent_provider_openai'].setVisible(True)
        else:
            self.window.ui.nodes['preset.editor.agent_provider_openai'].setVisible(False)

        # presets: editor
        if mode == MODE_AGENT:
            self.window.controller.presets.editor.toggle_tab("experts", True)
            self.window.ui.nodes['preset.editor.temperature'].setVisible(True)
            self.window.ui.nodes['preset.editor.idx'].setVisible(False)
            self.window.ui.nodes['preset.editor.agent_provider'].setVisible(False)
            self.window.ui.nodes['preset.editor.modes'].setVisible(False)
            self.window.ui.tabs['preset.editor.extra'].setTabText(0, trans("preset.prompt.agent"))
        elif mode == MODE_AGENT_LLAMA:
            self.window.controller.presets.editor.toggle_tab("experts", False)
            self.window.ui.nodes['preset.editor.temperature'].setVisible(False)
            self.window.ui.nodes['preset.editor.idx'].setVisible(True)
            self.window.ui.nodes['preset.editor.agent_provider'].setVisible(True)
            self.window.ui.nodes['preset.editor.modes'].setVisible(False)
            self.window.ui.tabs['preset.editor.extra'].setTabText(0, trans("preset.prompt.agent_llama"))
        elif mode == MODE_AGENT_OPENAI:
            self.window.controller.presets.editor.toggle_tab("experts", True)
            self.window.ui.nodes['preset.editor.temperature'].setVisible(False)
            self.window.ui.nodes['preset.editor.idx'].setVisible(True)
            self.window.ui.nodes['preset.editor.agent_provider'].setVisible(False)
            self.window.ui.nodes['preset.editor.modes'].setVisible(False)
            self.window.ui.tabs['preset.editor.extra'].setTabText(0, trans("preset.prompt.agent_llama"))
        else:
            if mode == MODE_EXPERT:
                self.window.ui.nodes['preset.editor.idx'].setVisible(True)
            else:
                self.window.ui.nodes['preset.editor.idx'].setVisible(False)

            self.window.controller.presets.editor.toggle_tab("experts", False)
            self.window.ui.nodes['preset.editor.temperature'].setVisible(True)
            self.window.ui.nodes['preset.editor.agent_provider'].setVisible(False)
            self.window.ui.nodes['preset.editor.modes'].setVisible(True)
            self.window.ui.tabs['preset.editor.extra'].setTabText(0, trans("preset.prompt"))

        # img options
        if mode == MODE_IMAGE:
            self.window.ui.nodes['dalle.options'].setVisible(True)
        else:
            self.window.ui.nodes['dalle.options'].setVisible(False)

        # agent options
        if mode in [MODE_AGENT]:
            self.window.ui.nodes['agent.options'].setVisible(True)
        else:
            self.window.ui.nodes['agent.options'].setVisible(False)

        # agent llama options
        if mode in [MODE_AGENT_LLAMA, MODE_AGENT_OPENAI]:
            self.window.ui.nodes['agent_llama.options'].setVisible(True)
        else:
            self.window.ui.nodes['agent_llama.options'].setVisible(False)

        # assistants list
        if mode == MODE_ASSISTANT:
            self.window.ui.nodes['assistants.widget'].setVisible(True)
        else:
            self.window.ui.nodes['assistants.widget'].setVisible(False)

        # indexes list
        if mode == MODE_LLAMA_INDEX:
            self.window.ui.nodes['idx.options'].setVisible(True)
        else:
            self.window.ui.nodes['idx.options'].setVisible(False)

        # stream mode
        if mode in [MODE_IMAGE]:

            self.window.ui.nodes['input.stream'].setVisible(False)
        else:
            self.window.ui.nodes['input.stream'].setVisible(True)

        # vision
        show = self.is_vision(mode)
        self.window.ui.menu['menu.video'].menuAction().setVisible(show)
        self.window.ui.nodes['icon.video.capture'].setVisible(show)
        self.window.ui.nodes['attachments.capture_clear'].setVisible(show)

        # attachments
        show = self.are_attachments(mode)
        self.window.ui.tabs['input'].setTabVisible(1, show)

        # uploaded files
        if mode == MODE_ASSISTANT:
            self.window.ui.tabs['input'].setTabVisible(2, True)
            self.window.ui.tabs['input'].setTabVisible(3, False)
        else:
            if mode != MODE_IMAGE:
                self.window.ui.tabs['input'].setTabVisible(2, False)
                self.window.ui.tabs['input'].setTabVisible(3, True)
            else:
                self.window.ui.tabs['input'].setTabVisible(2, False)
                self.window.ui.tabs['input'].setTabVisible(3, False)

        # show/hide extra options in preset editor
        self.window.controller.presets.editor.toggle_extra_options()

        # chat footer
        self.toggle_chat_footer()

    def toggle_chat_footer(self):
        """Toggle chat footer"""
        if self.window.controller.ui.tabs.get_current_type() != Tab.TAB_CHAT:
            self.hide_chat_footer()
        else:
            self.show_chat_footer()

    def is_vision(self, mode: str) -> bool:
        """
        Check if vision is allowed

        :param mode: current mode
        :return: True if vision is allowed
        """
        if self.window.controller.ui.vision.has_vision():
            return True

        if self.window.controller.painter.is_active():
            return True

        # event: UI: vision
        value = False
        event = Event(Event.UI_VISION, {
            'mode': mode,
            'value': value,
        })
        self.window.dispatch(event)
        return event.data['value']

    def are_attachments(self, mode: str) -> bool:
        """
        Check if attachments are allowed

        :param mode: current mode
        :return: True if attachments are allowed
        """
        # event: UI: attachments
        # value = False
        event = Event(Event.UI_ATTACHMENTS, {
            'mode': mode,
            'value': True,
        })
        self.window.dispatch(event)
        return event.data['value']

    def show_chat_footer(self):
        """Show chat footer"""
        self.window.ui.nodes['chat.footer'].setVisible(True)

    def hide_chat_footer(self):
        """Hide chat footer"""
        self.window.ui.nodes['chat.footer'].setVisible(False)

