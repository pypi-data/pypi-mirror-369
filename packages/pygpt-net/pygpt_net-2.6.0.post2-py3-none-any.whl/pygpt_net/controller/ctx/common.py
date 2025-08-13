#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2025.07.19 17:00:00                  #
# ================================================== #

from typing import Optional

from PySide6.QtWidgets import QApplication

from pygpt_net.core.tabs.tab import Tab
from pygpt_net.utils import trans
from pygpt_net.item.ctx import CtxMeta
from .summarizer import Summarizer


class Common:
    def __init__(self, window=None):
        """
        Common ctx controller

        :param window: Window instance
        """
        self.window = window
        self.summarizer = Summarizer(window)

    def update_label_by_current(self):
        """Update ctx label from current ctx"""
        mode = self.window.core.ctx.get_mode()

        # if no ctx mode then use current mode
        if mode is None:
            mode = self.window.core.config.get('mode')

        label = trans('mode.' + mode)

        # append assistant name to ctx name label
        if mode == 'assistant':
            id = self.window.core.ctx.get_assistant()
            assistant = self.window.core.assistants.get_by_id(id)
            if assistant is not None:
                # get ctx assistant
                label += ' (' + assistant.name + ')'
            else:
                # get current assistant
                id = self.window.core.config.get('assistant')
                assistant = self.window.core.assistants.get_by_id(id)
                if assistant is not None:
                    label += ' (' + assistant.name + ')'

        # update ctx label
        self.window.controller.ui.update_ctx_label(label)

    def update_label(
            self,
            mode: str,
            assistant_id: Optional[str] = None
    ):
        """
        Update ctx label

        :param mode: Mode
        :param assistant_id: Assistant id
        """
        if mode is None:
            return
        label = trans('mode.' + mode)
        if mode == 'assistant' and assistant_id is not None:
            assistant = self.window.core.assistants.get_by_id(assistant_id)
            if assistant is not None:
                label += ' (' + assistant.name + ')'

        # update ctx label
        self.window.controller.ui.update_ctx_label(label)

    def duplicate(self, meta_id: int):
        """
        Duplicate context by meta id

        :param meta_id: context id
        """
        new_id = self.window.core.ctx.duplicate(meta_id)
        if new_id is not None:
            self.window.core.attachments.context.duplicate(meta_id, new_id)  # copy attachments
            self.window.update_status(
                "Context duplicated, new ctx id: {}".format(new_id)
            )
            self.window.controller.ctx.update(no_scroll=True)

    def dismiss_rename(self):
        """Dismiss rename dialog"""
        self.window.ui.dialog['rename'].close()

    def focus_chat(self, meta: CtxMeta = None):
        """
        Focus chat tab by meta

        :param meta: CtxMeta instance
        """
        data_id = None
        title = None
        if meta:
            data_id = meta.id
            title = meta.name
        self.window.controller.ui.tabs.focus_by_type(Tab.TAB_CHAT, data_id=data_id, title=title, meta=meta)

    def restore_display_filter(self):
        """Restore display filter"""
        self.window.ui.nodes['filter.ctx.radio.all'].setChecked(False)
        self.window.ui.nodes['filter.ctx.radio.pinned'].setChecked(False)
        self.window.ui.nodes['filter.ctx.radio.indexed'].setChecked(False)

        if self.window.core.config.has('ctx.records.filter'):
            filter = self.window.core.config.get('ctx.records.filter')
            self.toggle_display_filter(filter)

            if filter == 'pinned':
                self.window.ui.nodes['filter.ctx.radio.pinned'].setChecked(True)
            elif filter == 'indexed':
                self.window.ui.nodes['filter.ctx.radio.indexed'].setChecked(True)
            else:
                self.window.ui.nodes['filter.ctx.radio.all'].setChecked(True)
        else:
            self.window.ui.nodes['filter.ctx.radio.all'].setChecked(True)
            self.toggle_display_filter('all')

        # restore filters labels
        self.restore_filters_labels()

    def restore_filters_labels(self):
        """Restore filters labels"""
        labels = self.window.core.config.get('ctx.records.filter.labels')
        if labels is not None:
            self.window.core.ctx.filters_labels = labels
            self.window.ui.nodes['filter.ctx.labels'].restore(labels)

    def toggle_display_filter(self, filter: str):
        """
        Toggle display filter

        :param filter: Filter
        """
        filters = {}
        if filter == 'pinned':
            filters['is_important'] = {
                "mode": "=",
                "value": 1,
            }
        elif filter == 'indexed':
            filters['indexed_ts'] = {
                "mode": ">",
                "value": 0,
            }

        self.window.core.config.set("ctx.records.filter", filter)
        self.window.core.ctx.clear_tmp_meta()
        self.window.core.ctx.set_display_filters(filters)
        self.window.controller.ctx.update()

    def copy_id(self, id: int):
        """
        Copy id into clipboard and to iinput

        :param id: context list idx
        """
        value = "@" + str(id)
        self.window.controller.chat.common.append_to_input(value, separator=" ")
        QApplication.clipboard().setText(value)

    def reset(
            self,
            meta_id: int,
            force: bool = False
    ):
        """
        Reset by meta id

        :param meta_id: context id
        :param force: True to force reset
        """
        if not force:
            self.window.ui.dialogs.confirm(
                type='ctx.reset_meta',
                id=meta_id,
                msg=trans('ctx.reset_meta.confirm'),
            )
            return
        self.window.core.ctx.reset_meta(meta_id)
        self.window.core.attachments.context.reset_by_meta_id(meta_id, delete_files=True)
        if self.window.core.ctx.get_current() == meta_id:
            self.window.controller.ctx.load(meta_id)