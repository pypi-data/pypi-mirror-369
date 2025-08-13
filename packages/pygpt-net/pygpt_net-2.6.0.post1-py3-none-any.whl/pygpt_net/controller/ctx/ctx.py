#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2025.08.12 19:00:00                  #
# ================================================== #

from typing import Optional, List

from PySide6.QtCore import QModelIndex, QTimer
from PySide6.QtGui import QStandardItem

from pygpt_net.core.events import Event, AppEvent, RenderEvent
from pygpt_net.item.ctx import CtxItem, CtxMeta

from .common import Common
from .summarizer import Summarizer
from .extra import Extra

from pygpt_net.utils import trans


class Ctx:
    def __init__(self, window=None):
        """
        Context controller

        :param window: Window instance
        """
        self.window = window
        self.common = Common(window)
        self.summarizer = Summarizer(window)
        self.extra = Extra(window)

        # current edit IDs
        self.edit_meta_id = None
        self.edit_item_id = None

        # current group ID
        self.group_id = None
        self.selected = []

    def setup(self):
        """Setup ctx"""
        self.common.restore_display_filter()  # load filters first

        # load ctx list
        self.window.core.ctx.load_meta()

        # if no context yet then create one
        if self.window.core.ctx.count_meta() == 0:
            self.new()
        else:
            # get last ctx from config
            id = self.window.core.config.get('ctx')
            if id is not None and self.window.core.ctx.has(id):
                self.window.core.ctx.set_current(id)
            else:
                # if no ctx then get first ctx
                self.window.core.ctx.set_current(self.window.core.ctx.get_first())

        # restore search string if exists
        if self.window.core.config.has("ctx.search.string"):
            string = self.window.core.config.get("ctx.search.string")
            if string is not None and string != "":
                self.window.ui.nodes['ctx.search'].setText(string)
                self.search_string_change(string)
                # check if current selected ctx is still valid
                if self.window.core.ctx.get_current() is not None:
                    if not self.window.core.ctx.has(self.window.core.ctx.get_current()):
                        self.search_string_clear()
                        # ^ clear search and reload ctx list to prevent creating new ctx

        self.window.ui.nodes['ctx.list'].collapseAll()  # collapse all items at start
        self.restore_expanded_groups()  # restore expanded groups
        self.select_by_current(focus=True)  # scroll to current ctx

        # focus input after loading
        QTimer.singleShot(100, self.window.controller.chat.common.focus_input)


    def update_mode_in_current(self):
        """Update current ctx mode"""
        mode = self.window.core.config.get('mode')
        model = self.window.core.config.get('model')
        id = self.window.core.ctx.get_current()
        if id is not None:
            meta = self.window.core.ctx.get_meta_by_id(id)
            if meta:
                # update mode in current ctx
                self.window.core.ctx.mode = mode
                self.window.core.ctx.model = model
                self.window.core.ctx.last_mode = mode
                self.window.core.ctx.last_model = model
                meta.mode = mode
                meta.model = model
                meta.last_mode = mode
                meta.last_model = model
                self.window.core.ctx.save(id)

    def update(
            self,
            reload: bool = True,
            all: bool = True,
            select: bool = True,
            no_scroll: bool = False
    ):
        """
        Update ctx list

        :param reload: reload ctx list items
        :param all: update all
        :param select: select current ctx
        :param no_scroll: do not scroll to selected item
        """
        # reload ctx list items
        if reload:
            self.update_list(True)

        # select current ctx on list
        if select:
            if no_scroll:  # store scroll position
                self.window.ui.nodes['ctx.list'].store_scroll_position()
            self.select_by_current()
            if no_scroll:  # restore scroll position
                self.window.ui.nodes['ctx.list'].restore_scroll_position()

        # update all
        if all:
            self.window.controller.ui.update()

        # append ctx and thread id (assistants API) to config
        id = self.window.core.ctx.get_current()
        if id is not None:
            self.window.core.config.set('ctx', id)
            self.window.core.config.set('assistant_thread', self.window.core.ctx.get_thread())
            self.window.core.config.save()

        # update calendar ctx list
        self.window.controller.calendar.update(all=False)

        # update additional context attachments
        self.window.controller.chat.attachment.update()

    def select(
            self,
            id: int,
            force: bool = False
    ):
        """
        Select ctx by id

        :param id: context meta id
        :param force: force select
        """
        prev_id = self.window.core.ctx.get_current()
        self.window.core.ctx.set_current(id)
        meta = self.window.core.ctx.get_meta_by_id(id)
        if prev_id != id or force:
            self.load(id)
            self.window.dispatch(AppEvent(AppEvent.CTX_SELECTED))  # app event
        else:
            # only update current group if defined
            if meta is not None:
                self.set_group(meta.group_id)

        self.common.focus_chat(meta)
        # update additional context attachments
        self.window.controller.chat.attachment.update()
        self.set_selected(id)
        self.clean_memory()  # clean memory

    def select_on_list_only(self, id: int):
        """
        Select ctx by id only on list

        :param id: context meta id
        """
        self.window.core.ctx.select(id, restore_model=True)
        self.window.core.ctx.set_current(id)
        self.update_list(True)
        self.select_by_current()
        self.reload_config(all=False)
        self.update()
        self.set_selected(id)

    def select_by_idx(self, idx: int):
        """
        Select ctx by index

        :param idx: context index
        """
        self.select_by_id(self.window.core.ctx.get_id_by_idx(idx))

    def select_by_id(self, id: int):
        """
        Select ctx by index

        :param id: context index
        """
        # lock if generating response is in progress
        if self.context_change_locked():
            return

        self.select(id)
        event = Event(Event.CTX_SELECT, {
            'value': id,
        })
        self.window.dispatch(event)

    def select_by_current(self, focus: bool = False):
        """
        Select ctx by current

        :param focus: focus chat
        """
        id = self.window.core.ctx.get_current()
        meta = self.window.core.ctx.get_meta()
        if id in meta:
            self.select_index_by_id(id)
        if focus:
            self.update()
            index = self.get_child_index_by_id(id)
            if index.isValid():
                self.window.ui.nodes['ctx.list'].scrollTo(index)

    def unselect(self):
        """Unselect ctx"""
        self.set_group(None)
        self.window.ui.nodes['ctx.list'].clearSelection()
        self.clear_selected()

    def set_group(self, group_id: Optional[int] = None):
        """
        Set current selected group

        :param group_id: group ID
        """
        self.group_id = group_id

    def search_focus_in(self):
        """Search focus handler"""
        pass
        # self.select_by_current()

    def new_ungrouped(self):
        """Create new ungrouped ctx"""
        self.group_id = None
        self.new()

    def clean_memory(self):
        """Clean memory"""
        self.window.core.gpt.close()  # clear gpt client

    def new(
            self,
            force: bool = False,
            group_id: Optional[int] = None
    ):
        """
        Create new ctx

        :param force: force context creation
        :param group_id: group ID
        """
        # lock if generating response is in progress
        if not force and self.context_change_locked():
            return

        # use currently selected group if not defined
        if group_id is None:
            if self.group_id is not None and self.group_id > 0:
                group_id = self.group_id
        else:
            self.group_id = group_id

        # check if group exists
        if group_id is not None and not self.window.core.ctx.has_group(group_id):
            group_id = None
            self.group_id = None

        meta = self.window.core.ctx.new(group_id)
        self.window.core.config.set('assistant_thread', None)  # reset assistant thread id
        self.update()

        self.fresh_output(meta)  # render reset

        if not force:  # only if real click on new context button
            self.window.controller.chat.common.unlock_input()
            self.window.controller.chat.common.focus_input()

        # update context label
        mode = self.window.core.ctx.get_mode()
        assistant_id = None
        if mode == 'assistant':
            assistant_id = self.window.core.config.get('assistant')
            self.window.controller.assistant.files.update()  # always update assistant files

        self.common.update_label(mode, assistant_id)
        self.common.focus_chat(meta)

        # update tab title
        if meta is not None:
            self.window.controller.ui.tabs.update_title_current(meta.name)

        # app event
        self.window.dispatch(AppEvent(AppEvent.CTX_CREATED))

        # switch to new context if non-chat tab
        self.select(meta.id)

        # self.window.core.debug.mem("NEW")  # debug memory usage
        return meta

    def add(self, ctx: CtxItem):
        """
        Add ctx item (CtxItem object)

        :param ctx: CtxItem
        """
        self.window.core.ctx.add(ctx)
        self.update()

    def prev(self):
        """Select previous ctx"""
        id = self.window.core.ctx.get_prev()
        if id is not None:
            self.select(id)

    def next(self):
        """Select next ctx"""
        id = self.window.core.ctx.get_next()
        if id is not None:
            self.select(id)

    def last(self):
        """Select last (newest) ctx"""
        id = self.window.core.ctx.get_last_meta()
        if id is not None:
            self.select(id)

    def update_list(self, reload: bool = False):
        """
        Reload current ctx list

        :param reload: reload ctx list items
        """
        self.window.ui.contexts.ctx_list.update(
            'ctx.list',
            self.window.core.ctx.get_meta(reload),
        )

    def refresh(self, restore_model: bool = True):
        """
        Refresh context

        :param restore_model: restore model
        """
        self.load(
            self.window.core.ctx.get_current(),
            restore_model,
        )

    def refresh_output(self):
        """Refresh output"""
        # append ctx to output
        data = {
            "meta": self.window.core.ctx.get_current_meta(),
            "items": self.window.core.ctx.get_items(),
            "clear": True,
        }
        event = RenderEvent(RenderEvent.CTX_APPEND, data)
        self.window.dispatch(event)

    def load(
            self,
            id: int,
            restore_model: bool = True,
            select_idx: Optional[int] = None,
            new_tab: Optional[bool] = False
    ):
        """
        Load ctx data

        :param id: context ID
        :param restore_model: restore model if defined in ctx
        :param select_idx: select index on list after loading
        :param new_tab: open in new tab
        """
        # if new_tab is True then first open new tab
        if new_tab:
            col_idx = self.window.controller.ui.tabs.column_idx
            self.window.controller.ui.tabs.create_new_on_tab = False  # disable create new ctx on tab create
            self.window.controller.ui.tabs.new_tab(col_idx)

        # select ctx by id
        self.window.core.ctx.clear_thread()  # reset thread id
        self.window.core.ctx.select(id, restore_model=restore_model)
        meta = self.window.core.ctx.get_meta_by_id(id)
        if meta is not None:
            self.set_group(meta.group_id)  # set current group if defined

        # reset appended data / prepare new ctx
        if meta is not None:
            self.fresh_output(meta)  # render reset

        self.reload_config()

        # reload ctx list and select current ctx on list, without reloading all
        self.update(reload=False, all=True)

        # update tab title
        if meta is not None:
            self.window.controller.ui.tabs.on_load_ctx(meta)

        # if select by Open on list
        if select_idx is not None:
            self.select(id)
            self.window.ui.nodes['ctx.list'].select_by_idx(select_idx)

    def after_load(
            self,
            id: int,
    ):
        """
        Load ctx data

        :param id: context ID
        """
        # select ctx by id
        meta = self.window.core.ctx.get_meta_by_id(id)
        if meta is not None:
            self.set_group(meta.group_id)  # set current group if defined

        # reset appended data / prepare new ctx
        if meta is not None:
            data = {
                "meta": meta,
            }
            event = RenderEvent(RenderEvent.ON_LOAD, data)
            self.window.dispatch(event)

        self.reload_config()

        # reload ctx list and select current ctx on list, without reloading all
        self.update(reload=False, all=True)

        # update tab title
        if meta is not None:
            self.window.controller.ui.tabs.on_load_ctx(meta)

    def reload_config(self, all: bool = True):
        """
        Reload config

        :param all: reload all
        """
        # get current settings stored in ctx
        thread = self.window.core.ctx.get_thread()
        mode = self.window.core.ctx.get_mode()
        model = self.window.core.ctx.get_model()
        assistant_id = self.window.core.ctx.get_assistant()
        preset = self.window.core.ctx.get_preset()

        # restore thread from ctx
        self.window.core.config.set('assistant_thread', thread)

        if all:
            # clear before output and append ctx to output
            self.refresh_output()

        # switch mode to ctx mode
        if mode is not None:
            self.window.controller.mode.set(mode)  # preset reset here

            # switch preset to ctx preset
            if preset is not None:
                self.window.controller.presets.set(mode, preset)
                self.window.controller.presets.refresh()  # update presets only

            # if ctx mode == assistant then switch assistant to ctx assistant
            if mode == 'assistant':
                # if assistant defined then select it
                if assistant_id is not None:
                    self.window.controller.assistant.select_by_id(assistant_id)
                else:
                    # if empty ctx assistant then get assistant from current selected
                    assistant_id = self.window.core.config.get('assistant')
                self.window.controller.assistant.files.update()  # always update assistant files

            # switch model to ctx model if model is defined in ctx and model is available for this mode
            if model is not None and self.window.core.models.has_model(mode, model):
                self.window.controller.model.set(mode, model)

        # update current ctx label in UI
        self.common.update_label(mode, assistant_id)

    def update_ctx(self):
        """Update current ctx mode if allowed"""
        mode = self.window.core.config.get('mode')

        id = None
        # update ctx mode only if current ctx is allowed for this mode
        if self.window.core.ctx.is_allowed_for_mode(mode, False):  # do not check assistant match
            self.window.core.ctx.update()

            # update current context label
            if mode == 'assistant':
                if self.window.core.ctx.get_assistant() is not None:
                    # get assistant id from ctx if defined in ctx
                    id = self.window.core.ctx.get_assistant()
                else:
                    # or get assistant id from current selected assistant
                    id = self.window.core.config.get('assistant')

        # update ctx label
        self.common.update_label(mode, id)

    def delete(
            self,
            id: int,
            force: bool = False
    ):
        """
        Delete ctx by idx

        :param id: context meta idx on list
        :param force: force delete
        """
        if not force:
            self.window.ui.dialogs.confirm(
                type='ctx.delete',
                id=id,
                msg=trans('ctx.delete.confirm'),
            )
            return

        # delete data from indexes if exists
        try:
            self.delete_meta_from_idx(id)
        except Exception as e:
            self.window.core.debug.log(e)
            print("Error deleting ctx data from indexes", e)

        # delete ctx items from db
        items = self.window.core.ctx.all()
        self.window.core.history.remove_items(items)  # remove txt history items
        self.window.core.attachments.context.delete_by_meta_id(id)
        self.window.core.ctx.remove(id)  # remove ctx from db
        self.remove_selected(id)  # remove from selected list

        # reset current if current ctx deleted
        if self.window.core.ctx.get_current() == id:
            self.window.core.ctx.clear_current()
            event = RenderEvent(RenderEvent.CLEAR_OUTPUT)
            self.window.dispatch(event)
        self.update(no_scroll=True)

        # update tab title
        self.window.controller.ui.tabs.update_title_current("...")

    def delete_meta_from_idx(self, id: int):
        """
        Delete meta from indexes

        :param id: ctx meta id
        """
        meta = self.window.core.ctx.get_meta_by_id(id)
        if meta is None:
            return

        # check if ctx is indexed
        if meta.indexed is not None and meta.indexed > 0:
            for store_id in list(meta.indexes):
                for idx in list(meta.indexes[store_id]):
                    self.window.core.ctx.idx.remove_meta_from_indexed(store_id, id, idx)

    def delete_item(
            self,
            id: int,
            force: bool = False
    ):
        """
        Delete ctx item by id

        :param id: ctx item id
        :param force: force delete
        """
        if not force:
            self.window.ui.dialogs.confirm(
                type='ctx.delete_item',
                id=id,
                msg=trans('ctx.delete.item.confirm'),
            )
            return
        self.window.core.ctx.remove_item(id)
        self.refresh()
        self.update(no_scroll=True)

    def delete_history(self, force: bool = False):
        """
        Delete all ctx / truncate

        :param force: force delete
        """
        if not force:
            self.window.ui.dialogs.confirm(
                type='ctx.delete_all',
                id='',
                msg=trans('ctx.delete.all.confirm'),
            )
            return

        # truncate index db if exists
        try:
            self.window.core.idx.ctx.truncate()
        except Exception as e:
            self.window.core.debug.log(e)
            print("Error truncating ctx index db", e)

        # truncate ctx and history
        self.group_id = None
        self.unselect()
        self.window.core.ctx.truncate()
        self.window.core.history.truncate()
        self.window.core.attachments.context.truncate()
        self.clear_selected()
        self.update()
        self.new()

    def delete_history_groups(self, force: bool = False):
        """
        Delete all ctx / truncate

        :param force: force delete
        """
        if not force:
            self.window.ui.dialogs.confirm(
                type='ctx.delete_all_groups',
                id='',
                msg=trans('ctx.delete.all.confirm'),
            )
            return

        # truncate index db if exists
        try:
            self.window.core.idx.ctx.truncate()
        except Exception as e:
            self.window.core.debug.log(e)
            print("Error truncating ctx index db", e)

        # truncate ctx and history
        self.group_id = None
        self.unselect()
        self.window.core.ctx.truncate()
        self.window.core.history.truncate()
        self.window.core.ctx.truncate_groups()
        self.window.core.attachments.context.truncate()
        self.clear_selected()
        self.update()
        self.new()

    def new_if_empty(self):
        """Create new context if empty"""
        self.group_id = None
        if self.window.core.ctx.count_meta() == 0:
            self.new()

    def rename(self, id: int):
        """
        Ctx name rename by id (show dialog)

        :param id: context id
        """
        meta = self.window.core.ctx.get_meta_by_id(id)
        self.window.ui.dialog['rename'].id = 'ctx'
        self.window.ui.dialog['rename'].input.setText(meta.name)
        self.window.ui.dialog['rename'].current = id
        self.window.ui.dialog['rename'].show()

    def set_important(
            self,
            id: int,
            value: bool = True
    ):
        """
        Set as important

        :param id: context idx
        :param value: important value
        """
        meta = self.window.core.ctx.get_meta_by_id(id)
        if meta is not None:
            meta.important = value
            self.window.core.ctx.save(id)
            self.update(no_scroll=True)
            self.select_by_current()

    def is_important(self, idx: int) -> bool:
        """
        Check if ctx is important

        :param idx: context idx
        :return: True if important
        """
        id = self.window.core.ctx.get_id_by_idx(idx)
        meta = self.window.core.ctx.get_meta_by_id(id)
        if meta is not None:
            return meta.important
        return False

    def set_label(
            self,
            id: int,
            label_id: int
    ):
        """
        Set color label for ctx by idx

        :param id: context idx
        :param label_id: label id
        """
        meta = self.window.core.ctx.get_meta_by_id(id)
        if meta is not None:
            meta.label = label_id
            self.window.core.ctx.save(id)
            self.update(no_scroll=True)

    def update_name(
            self,
            id: int,
            name: str,
            close: bool = True,
            refresh: bool = True
    ):
        """
        Update ctx name

        :param id: context id
        :param name: context name
        :param close: close rename dialog
        :param refresh: refresh ctx list
        """
        if id not in self.window.core.ctx.get_meta():
            return
        self.window.core.ctx.meta[id].name = name
        self.window.core.ctx.set_initialized()
        self.window.core.ctx.save(id)
        if close:
            self.window.ui.dialog['rename'].close()

        if refresh:
            self.update(no_scroll=True)
        else:
            self.update(reload=True, all=False, no_scroll=True)

        # update tab title
        meta = self.window.core.ctx.get_meta_by_id(id)
        if meta is not None:
            if id == self.window.core.ctx.get_current():
                self.window.controller.ui.tabs.update_title_current(meta.name)

    def update_name_current(self, name: str):
        """
        Update current ctx name

        :param name: context name
        """
        self.update_name(self.window.core.ctx.get_current(), name)

    def handle_allowed(self, mode: str) -> bool:
        """
        Check if append to current ctx is allowed for this mode, if not then switch to new context

        :param mode: mode name
        :return: True if allowed
        """
        if not self.window.core.ctx.is_allowed_for_mode(mode):
            self.new(True)  # force new context
            return False
        return True

    def selection_change(self):
        """Select ctx on list change"""
        # TODO: implement this
        # idx = self.window.ui.nodes['ctx.list'].currentIndex().row()
        # self.select(idx)
        selected_idx = self.window.ui.nodes['ctx.list'].currentIndex()
        if selected_idx.isValid():
            id = self.window.core.ctx.get_id_by_idx(selected_idx.row())
        self.window.ui.nodes['ctx.list'].lockSelection()

    def search_string_change(self, text: str):
        """
        Search string changed handler

        :param text: search string
        """
        self.window.core.ctx.clear_tmp_meta()
        self.window.core.ctx.set_search_string(text)
        self.window.core.config.set('ctx.search.string', text)
        self.update(reload=True, all=False)

    def search_string_clear(self):
        """Search string clear"""
        self.window.ui.nodes['ctx.search'].clear()
        self.search_string_change("")  # clear search

    def append_search_string(self, text: str):
        """
        Append search string to input and make search

        :param text: search string
        """
        self.window.ui.nodes['ctx.search'].setText(text)
        self.search_string_change(text)  # make search

    def label_filters_changed(self, labels: List[int]):
        """
        Filters labels change

        :param labels: list of labels
        """
        self.window.core.ctx.clear_tmp_meta()
        self.window.core.ctx.filters_labels = labels
        self.window.core.config.set('ctx.records.filter.labels', labels)
        self.update(reload=True, all=False)

    def prepare_name(self, ctx: CtxItem, force: bool = False):
        """
        Handle context name (summarize first input and output)

        :param ctx: CtxItem
        :param force: force update
        """
        # if ctx is not initialized yet then summarize
        if not self.window.core.ctx.is_initialized() or force:
            self.summarizer.summarize(
                self.window.core.ctx.get_current(),
                ctx,
            )

    def context_change_locked(self) -> bool:
        """
        Check if ctx change is locked

        :return: True if locked
        """
        return self.window.controller.chat.input.generating

    def select_index_by_id(self, id: int):
        """
        Select item by ID on context list

        :param id: ctx meta ID
        """
        index = self.get_child_index_by_id(id)
        self.window.ui.nodes['ctx.list'].unlocked = True  # tmp allow change if locked (enable)
        self.window.ui.nodes['ctx.list'].setCurrentIndex(index)
        self.window.ui.nodes['ctx.list'].unlocked = False  # tmp allow change if locked (disable)

    def find_index_by_id(
            self,
            item: QStandardItem,
            id: int
    ) -> QModelIndex:
        """
        Return index of item with given ID, searching recursively through the model.

        :param item: QStandardItem
        :param id: int
        :return: QModelIndex
        """
        if hasattr(item, 'id') and item.id == id:
            return item.index()
        for row in range(item.rowCount()):
            found_index = self.find_index_by_id(item.child(row), id)
            if found_index.isValid():
                return found_index
        return QModelIndex()

    def find_parent_index_by_id(
            self,
            item: QStandardItem,
            id: int
    ) -> QModelIndex:
        """
        Return index of item with given ID, searching recursively through the model.

        :param item: QStandardItem
        :param id: int
        :return: QModelIndex
        """
        if hasattr(item, 'id') and hasattr(item, 'isFolder') and item.isFolder and item.id == id:
            return item.index()
        for row in range(item.rowCount()):
            found_index = self.find_parent_index_by_id(item.child(row), id)
            if found_index.isValid():
                return found_index
        return QModelIndex()

    def get_parent_index_by_id(self, id: int) -> QModelIndex:
        """
        Return QModelIndex of parent item based on its ID.

        :param id: int
        :return: QModelIndex
        """
        model = self.window.ui.models['ctx.list']
        root = model.invisibleRootItem()
        return self.find_parent_index_by_id(root, id)

    def get_children_index_by_id(
            self,
            parent_id: int,
            child_id: int
    ) -> QModelIndex:
        """
        Return QModelIndex of child item based on its ID and parent ID.

        :param parent_id: int
        :param child_id: int
        :return: QModelIndex
        """
        model = self.window.ui.models['ctx.list']
        parent_index = self.get_parent_index_by_id(parent_id)
        if not parent_index.isValid():
            # no parent found
            return QModelIndex()

        parent_item = model.itemFromIndex(parent_index)
        return self.find_index_by_id(parent_item, child_id)

    def find_child_index_by_id(
            self,
            root_item: QStandardItem,
            child_id: int
    ) -> QModelIndex:
        """
        Find and return QModelIndex of child based on its ID, recursively searching through the model.

        :param root_item: QStandardItem
        :param child_id: int
        :return: QModelIndex
        """
        finder = self.find_child_index_by_id
        for row in range(root_item.rowCount()):
            item = root_item.child(row)
            if hasattr(item, 'id') and hasattr(item, 'isFolder') and not item.isFolder and item.id == child_id:
                return item.index()
            child_index = finder(item, child_id)
            if child_index.isValid():
                return child_index
        return QModelIndex()

    def get_child_index_by_id(self, child_id: int) -> QModelIndex:
        """
        Return QModelIndex of child item based on its ID.

        :param child_id: int
        :return: QModelIndex
        """
        model = self.window.ui.models['ctx.list']
        root_item = model.invisibleRootItem()
        return self.find_child_index_by_id(root_item, child_id)

    def store_expanded_groups(self):
        """
        Store expanded groups in ctx list
        """
        expanded = []
        for group_id in self.window.ui.nodes['ctx.list'].expanded_items:
            expanded.append(group_id)
        self.window.core.config.set('ctx.list.expanded', expanded)
        self.window.core.config.save()

    def restore_expanded_groups(self):
        """
        Restore expanded groups in ctx list
        """
        expanded = self.window.core.config.get('ctx.list.expanded')
        if expanded is not None:
            for group_id in expanded:
                self.window.ui.nodes['ctx.list'].expand_group(group_id)

    def save_all(self):
        """Save visible ctx list items"""
        self.store_expanded_groups()

    def move_to_group(
            self,
            meta_id: int,
            group_id: int,
            update: bool = True
    ):
        """
        Move ctx to group

        :param meta_id: int
        :param group_id: int
        :param update: update ctx list
        """
        self.window.core.ctx.update_meta_group_id(meta_id, group_id)
        self.group_id = group_id
        if update:
            self.update(no_scroll=True)

    def remove_from_group(self, meta_id):
        """
        Remove ctx from group

        :param meta_id: int
        """
        self.window.core.ctx.update_meta_group_id(meta_id, None)
        self.group_id = None
        self.update(no_scroll=True)

    def new_group(
            self,
            meta_id: Optional[int] = None
    ):
        """
        Open new group dialog

        :param meta_id: int
        """
        self.window.ui.dialog['create'].id = 'ctx.group'
        self.window.ui.dialog['create'].input.setText("")
        self.window.ui.dialog['create'].current = meta_id
        self.window.ui.dialog['create'].show()
        self.window.ui.dialog['create'].input.setFocus()

    def create_group(
            self,
            name: Optional[str] = None,
            meta_id: Optional[int] = None
    ):
        """
        Make directory

        :param name: name of directory
        :param meta_id: int
        """
        if name is None:
            self.window.update_status(
                "[ERROR] Name is empty."
            )
            return
        group = self.window.core.ctx.make_group(name)
        id = self.window.core.ctx.insert_group(group)
        if id is not None:
            if meta_id is not None:
                self.move_to_group(meta_id, id, update=False)
            self.update()
            self.window.update_status(
                "Group '{}' created.".format(name)
            )
            self.window.ui.dialog['create'].close()

            # select new group
            self.select_group(id)
            self.group_id = id

    def rename_group(
            self,
            id: int,
            force: bool = False
    ):
        """
        Rename group

        :param id: group ID
        :param force: force rename
        """
        if not force:
            group = self.window.core.ctx.get_group_by_id(id)
            if group is None:
                return
            self.window.ui.dialog['rename'].id = 'ctx.group'
            self.window.ui.dialog['rename'].input.setText(group.name)
            self.window.ui.dialog['rename'].current = id
            self.window.ui.dialog['rename'].show()

    def update_group_name(
            self,
            id: int,
            name: str,
            close: bool = True
    ):
        """
        Update group name

        :param id: group ID
        :param name: group name
        :param close: close rename dialog
        """
        group = self.window.core.ctx.get_group_by_id(id)
        if group is not None:
            group.name = name
            self.window.core.ctx.update_group(group)
            if close:
                self.window.ui.dialog['rename'].close()
            self.update(
                reload=True,
                all=False,
                select=False,
                no_scroll=True
            )
            self.select_group(id)

    def get_group_name(self, id: int) -> str:
        """
        Get group name by ID

        :param id: group ID
        :return: group name
        """
        group = self.window.core.ctx.get_group_by_id(id)
        if group is not None:
            return group.name
        return ""

    def select_group(self, id: int):
        """
        Select group

        :param id: group ID
        """
        self.group_id = id
        index = self.get_parent_index_by_id(id)
        self.window.ui.nodes['ctx.list'].unlocked = True  # tmp allow change if locked (enable)
        self.window.ui.nodes['ctx.list'].setCurrentIndex(index)
        self.window.ui.nodes['ctx.list'].unlocked = False  # tmp allow change if locked (disable)

    def delete_group(
            self,
            id: int,
            force: bool = False
    ):
        """
        Delete group only

        :param id: group ID
        :param force: force delete
        """
        if not force:
            self.window.ui.dialogs.confirm(
                type='ctx.group.delete',
                id=id,
                msg=trans('confirm.ctx.delete')
            )
            return
        group = self.window.core.ctx.get_group_by_id(id)
        if group is not None:
            self.window.core.ctx.remove_group(group, all=False)
            if self.group_id == id:
                self.group_id = None
            self.update(no_scroll=True)

    def delete_group_all(
            self,
            id: int,
            force: bool = False
    ):
        """
        Delete group with all items

        :param id: group ID
        :param force: force delete
        """
        if not force:
            self.window.ui.dialogs.confirm(
                type='ctx.group.delete.all',
                id=id,
                msg=trans('confirm.ctx.delete.all')
            )
            return
        group = self.window.core.ctx.get_group_by_id(id)
        if group is not None:
            self.window.core.ctx.remove_group(group, all=True)
            if self.group_id == id:
                self.group_id = None
            self.update()

    def reload(self):
        """Reload ctx"""
        self.window.core.ctx.reset()
        self.setup()
        self.update()
        self.refresh()

    def reload_after(self):
        """After reload"""
        self.new_if_empty()

    def add_selected(self, id: int):
        """
        Add selection ID to selected list

        :param id: context meta ID
        """
        if id not in self.selected:
            self.selected.append(id)
    def remove_selected(self, id: int):
        """
        Remove selection ID from selected list

        :param id: context meta ID
        """
        if id in self.selected:
            self.selected.remove(id)

    def set_selected(self, id: int):
        """
        Set selected ID in selected list

        :param id: context meta ID
        """
        self.selected = [id] if id is not None else []

    def set_selected_by_idx(self, idx: int):
        """
        Set selected ID by index

        :param idx: context meta index
        """
        id = self.window.core.ctx.get_id_by_idx(idx)
        if id is not None:
            self.set_selected(id)

    def clear_selected(self):
        """Clear selected list"""
        self.selected = []


    def fresh_output(self, meta: CtxMeta):
        """
        Fresh output for new context

        :param meta: CtxItem
        """
        # render reset
        data = {
            "meta": meta,
        }
        event = RenderEvent(RenderEvent.FRESH, data)
        self.window.dispatch(event)
        data = {
            "meta": meta,
        }
        event = RenderEvent(RenderEvent.ON_LOAD, data)
        self.window.dispatch(event)
