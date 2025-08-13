# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2025.08.08 23:00:00                  #
# ================================================== #

from typing import Any, Optional, Tuple

from PySide6.QtCore import QTimer

from pygpt_net.core.events import AppEvent, RenderEvent
from pygpt_net.core.tabs.tab import Tab
from pygpt_net.item.ctx import CtxMeta
from pygpt_net.utils import trans


class Tabs:

    TAB_CHAT_MAX_CHARS = 15  # max chars for chat tab title

    def __init__(self, window=None):
        """
        UI tabs controller

        :param window: Window instance
        """
        self.window = window
        self.active_idx = 0
        self.prev_idx = 0
        self.initialized = False
        self.appended = False
        self.current = 0
        self.column_idx = 0
        self.tmp_column_idx = 0
        self.locked = False
        self.create_new_on_tab = True
        self.col = {}

    def setup(self):
        """Setup tabs"""
        self.window.core.tabs.load()
        self.window.controller.notepad.load()
        self.setup_options()
        self.initialized = True

    def setup_options(self):
        """Setup options"""
        state = self.window.core.config.get("layout.split", False)
        self.window.ui.nodes['layout.split'].setChecked(state)
        if not state:
            self.window.ui.splitters['columns'].setSizes([1, 0])

    def debug(self):
        """Debug tabs if enabled"""
        if self.window.controller.dialogs.debug.is_active("tabs"):
            self.window.core.tabs.toggle_debug(True)

    def add(
            self,
            type: int,
            title: str,
            icon: Optional[str] = None,
            child: Any = None,
            data_id: Optional[int] = None,
            tool_id: Optional[str] = None,
    ):
        """
        Add a new tab

        :param type: Tab type
        :param title: Tab title
        :param icon: Tab icon
        :param child: Tab child (child widget)
        :param data_id: Tab data ID (child data ID)
        :param tool_id: Tool ID
        """
        self.window.core.tabs.add(
            type=type,
            title=title,
            icon=icon,
            child=child,
            data_id=data_id,
            tool_id=tool_id
        )

    def append(
            self,
            type: int,
            tool_id: Optional[str] = None,
            idx: int = 0,
            column_idx: int = 0
    ):
        """
        Append tab at tab index

        :param type: Tab type
        :param tool_id: Tool ID
        :param idx: Tab index
        :param column_idx: Column index
        """
        self.appended = True  # lock reload in previous tab
        self.column_idx = column_idx  # switch to column
        tab = self.window.core.tabs.append(
            type=type,
            idx=idx,
            column_idx=column_idx,
            tool_id=tool_id
        )
        self.switch_tab_by_idx(tab.idx, column_idx)  # switch to new tab
        self.debug()

    def reload_titles(self):
        """Reload tab titles"""
        self.window.core.tabs.reload_titles()
        self.debug()

    def update_current(self):
        """Update current tab"""
        curr_tab = self.get_current_tab()
        curr_column = self.get_current_column_idx()
        if curr_column not in self.col:
            self.col[curr_column] = -1
        if curr_tab is not None:
            self.col[curr_column] = curr_tab.pid
        self.debug()

    def reload(self):
        """Reload tabs"""
        self.window.core.tabs.reload()
        event = RenderEvent(RenderEvent.PREPARE)
        self.window.dispatch(event)
        self.debug()

    def reload_after(self):
        """Reload tabs after"""
        for pid in self.window.ui.nodes['output']:
            try:
                if self.window.core.config.get("render.plain") is True:
                    self.window.ui.nodes['output_plain'][pid].setVisible(True)
                    self.window.ui.nodes['output'][pid].setVisible(False)
                else:
                    self.window.ui.nodes['output_plain'][pid].setVisible(False)
                    self.window.ui.nodes['output'][pid].setVisible(True)
            except Exception as e:
                pass
        self.debug()

    def on_tab_changed(
            self,
            idx: int,
            column_idx: int = 0
    ):
        """
        Output tab changed

        :param idx: tab index
        :param column_idx: column index
        """
        tab = self.window.core.tabs.get_tab_by_index(idx, column_idx)
        if tab is None:
            self.appended = False
            return

        if self.appended:
            self.appended = False
            if tab.type == Tab.TAB_CHAT:
                self.current = idx
                if self.create_new_on_tab:
                    meta = self.window.controller.ctx.new()  # new context
                    if meta is not None:
                        self.window.controller.ctx.load(meta.id)  # reload
                self.create_new_on_tab = True

        prev_tab = self.current
        prev_column = self.column_idx

        self.current = idx
        self.column_idx = column_idx
        self.window.controller.ui.mode.update()
        self.window.controller.ui.vision.update()

        # check type
        if tab.type == Tab.TAB_NOTEPAD:
            self.window.controller.notepad.opened_once = True
            self.window.controller.notepad.on_open(idx, column_idx)
        elif tab.type == Tab.TAB_CHAT:
            # get meta for selected tab, if not loaded yet then append meta here
            meta_id = tab.data_id
            if meta_id is None:
                meta_id = self.window.core.ctx.output.prepare_meta(tab)
            meta = self.window.core.ctx.get_meta_by_id(meta_id)
            if meta is not None:
                self.window.controller.ctx.load(meta.id)  # reload renderer
        elif tab.type == Tab.TAB_TOOL_PAINTER:
            if self.window.core.config.get('vision.capture.enabled'):
                self.window.controller.camera.enable_capture()
        elif tab.type == Tab.TAB_TOOL_CALENDAR:
            self.window.controller.calendar.update()
            self.window.controller.calendar.update_ctx_counters()

        if prev_tab != idx or prev_column != column_idx:
            self.window.dispatch(AppEvent(AppEvent.TAB_SELECTED))  # app event

        self.on_changed()
        self.window.controller.ui.update()
        self.update_current()
        self.debug()

    def on_changed(self):
        """On Tab or column changed event (any)"""
        tab = self.get_current_tab()
        if tab is None:
            return
        self.window.controller.audio.on_tab_changed(tab)
        self.debug()

    def get_current_idx(self, column_idx: int = 0) -> int:
        """
        Get current tab index

        :param column_idx: column index
        :return: tab index
        """
        return self.current

    def get_current_column_idx(self) -> int:
        """
        Get current column index

        :return: column index
        """
        return self.column_idx

    def get_current_tab(self) -> Optional[Tab]:
        """
        Get current tab

        :return: tab
        """
        return self.window.core.tabs.get_tab_by_index(self.get_current_idx(), self.column_idx)

    def get_current_type(self) -> Optional[int]:
        """
        Get current tab type

        :return: tab type
        """
        tab = self.window.core.tabs.get_tab_by_index(self.get_current_idx(), self.column_idx)

        if tab is None:
            return None
        return tab.type

    def get_current_pid(self) -> Optional[int]:
        """
        Get current tab PID

        :return: tab PID
        """
        tab = self.window.core.tabs.get_tab_by_index(self.get_current_idx(), self.column_idx)
        if tab is None:
            return None
        return tab.pid

    def get_type_by_idx(self, idx: int) -> Optional[int]:
        """
        Get tab type by index

        :param idx: tab index
        :return: tab type
        """
        tab = self.window.core.tabs.get_tab_by_index(idx, self.column_idx)
        if tab is None:
            return None
        return tab.type

    def get_first_idx_by_type(self, type: int) -> Optional[int]:
        """
        Get first tab index by type

        :param type: tab type
        :return: tab index
        """
        return self.window.core.tabs.get_min_idx_by_type(type, self.column_idx)

    def get_prev_idx_from(self, idx: int) -> Tuple[int, bool]:
        """
        Get previous tab index from given index

        :param idx: tab index
        :return: tuple of previous index and boolean indicating if it exists
        """
        return self.window.core.tabs.get_prev_idx_from(idx, self.column_idx)

    def get_next_idx_from(self, idx: int) -> Tuple[int, bool]:
        """
        Get next tab index from given index

        :param idx: tab index
        :return: tuple of next index and boolean indicating if it exists
        """
        return self.window.core.tabs.get_next_idx_from(idx, self.column_idx)

    def get_after_close_idx(self, idx: int) -> int:
        """
        Get tab index after closing the given index

        :param idx: tab index
        :return: previous tab index if exists, otherwise None
        """
        prev_idx, exists = self.get_prev_idx_from(idx)
        if exists:
            return prev_idx
        next_idx, exists = self.get_next_idx_from(idx)
        if exists:
            return next_idx

    def on_column_changed(self):
        """Column changed event"""
        if self.locked:
            return
        tabs = self.window.ui.layout.get_tabs_by_idx(self.column_idx)
        tabs.set_active(True)

        if self.column_idx == 0:
            second_tabs = self.window.ui.layout.get_tabs_by_idx(1)
        else:
            second_tabs = self.window.ui.layout.get_tabs_by_idx(0)
        second_tabs.set_active(False)
        idx = tabs.currentIndex()
        self.current = idx
        tab = self.window.core.tabs.get_tab_by_index(self.current, self.column_idx)
        if tab is None:
            return

        # redraw second tab if not loaded yet
        if tab.type == Tab.TAB_CHAT and self.column_idx == 1 and not tab.loaded:
            meta = self.window.core.ctx.get_meta_by_id(tab.data_id)
            if meta is not None:
                self.window.controller.ctx.load(meta.id)
            tab.loaded = True

        current_ctx = self.window.core.ctx.get_current()
        if (current_ctx is not None and current_ctx != tab.data_id) or current_ctx is None:
            if tab.type == Tab.TAB_CHAT:
                self.window.controller.ctx.select_on_list_only(tab.data_id)
        self.window.controller.ui.update()
        self.update_current()
        self.debug()

    def on_tab_clicked(
            self,
            idx: int,
            column_idx: int = 0
    ):
        """
        Tab click event

        :param idx: tab index
        :param column_idx: column index
        """
        self.current = idx
        self.column_idx = column_idx
        self.on_column_changed()
        self.on_changed()
        self.update_current()
        self.debug()

    def on_column_focus(self, idx: int):
        """
        Column focus event

        :param idx: column index
        """
        if self.column_idx == idx:
            return
        self.column_idx = idx
        self.on_column_changed()
        self.on_changed()
        self.update_current()
        self.debug()

    def on_tab_dbl_clicked(
            self,
            idx: int,
            column_idx: int = 0
    ):
        """
        Tab double click event

        :param idx: tab index
        :param column_idx: column index
        """
        self.column_idx = column_idx
        self.on_tab_changed(idx, column_idx)
        self.update_current()
        self.debug()

    def on_tab_closed(
            self,
            idx: int,
            column_idx: int = 0
    ):
        """
        Tab close event

        :param idx: tab index
        :param column_idx: column index
        """
        if self.locked:
            return

        previous_current = self.current
        idx_after = None  # <--- next tab index after close to switch to
        if previous_current != idx and self.column_idx == column_idx:
            idx_after = previous_current
            if idx_after > idx:
                idx_after -= 1  # if current is after closed tab, idx will be shifted

        if idx_after is None:
            idx_after = self.get_after_close_idx(idx)  # find next tab index after close

        self.window.core.tabs.remove_tab_by_idx(idx, column_idx)
        if idx_after is not None:
            self.switch_tab_by_idx(idx_after, column_idx)

        self.on_changed()
        self.update_current()
        self.debug()

    def on_tab_moved(
            self,
            idx: int,
            column_idx: int = 0
    ):
        """
        Tab moved event

        :param idx: tab index
        :param column_idx: column index
        """
        if self.locked:
            return
        self.window.core.tabs.update()
        self.update_current()
        self.debug()

    def close(
            self,
            idx: int,
            column_idx: int = 0
    ):
        """
        Close tab

        :param idx: tab index
        :param column_idx: column index
        """
        self.on_tab_closed(idx, column_idx)
        self.update_current()
        self.debug()

    def close_all(
            self,
            type: int,
            column_idx: int = 0,
            force: bool = False
    ):
        """
        Close all tabs

        :param type: tab type
        :param column_idx: column index
        :param force: force close
        """
        if not force:
            self.tmp_column_idx = column_idx
            self.window.ui.dialogs.confirm(
                type='tab.close_all',
                id=type,
                msg=trans('tab.close_all.confirm'),
            )
            return
        column_idx = self.tmp_column_idx
        self.window.core.tabs.remove_all_by_type(type, column_idx)
        self.on_changed()
        self.update_current()
        self.debug()

    def next_tab(self):
        """Switch to next tab"""
        tabs = self.window.ui.layout.get_active_tabs()
        current = tabs.currentIndex()
        all = len(tabs.children())
        next = current + 1
        if next >= all:
            next = 0
        self.switch_tab_by_idx(next)

    def prev_tab(self):
        """Switch to previous tab"""
        tabs = self.window.ui.layout.get_active_tabs()
        current = tabs.currentIndex()
        all = len(tabs.children())
        prev = current - 1
        if prev < 0:
            prev = all - 1
        self.switch_tab_by_idx(prev)

    def switch_tab(self, type: int):
        """
        Switch tab

        :param type: tab type
        """
        idx = self.window.core.tabs.get_min_idx_by_type(type)
        if idx is not None:
            self.switch_tab_by_idx(idx)

    def switch_tab_by_idx(
            self,
            idx: int,
            column_idx: int = 0
    ):
        """
        Switch tab by index

        :param idx: tab index
        :param column_idx: column index
        """
        tabs = self.window.ui.layout.get_tabs_by_idx(column_idx)
        tabs.setCurrentIndex(idx)
        self.on_tab_changed(idx, column_idx)

    def get_current_tab_name(self) -> str:
        """
        Get current tab name

        :return: tab name
        """
        tabs = self.window.ui.layout.get_active_tabs()
        return tabs.tabText(self.current)

    def get_current_tab_name_for_audio(self) -> str:
        """
        Get current tab name for audio description

        :return: tab name
        """
        tab = self.get_current_tab()
        if tab is None:
            return ""

        title = ""
        if tab.type in self.window.core.tabs.titles:
            title = trans(self.window.core.tabs.titles[tab.type])

        # if more than 1 with this type then attach position info
        num = self.window.core.tabs.count_by_type(tab.type)
        if num > 1:
            order = self.window.core.tabs.get_order_by_idx_and_type(tab.idx, tab.type)
            if order != -1:
                title += " #" + str(order)
        if tab.tooltip is not None and tab.tooltip != "":
            title += " - " + tab.tooltip
        return title

    def update_tooltip(self, tooltip: str):
        """
        Update tab tooltip

        :param tooltip: tooltip text
        """
        tabs = self.window.ui.layout.get_active_tabs()
        tabs.setTabToolTip(self.current, tooltip)
        self.debug()

    def rename(
            self,
            idx: int,
            column_idx: int = 0
    ):
        """
        Rename tab (show dialog)

        :param idx: tab idx
        :param column_idx: column idx
        """
        # get tab
        tab = self.window.core.tabs.get_tab_by_index(idx, column_idx)
        if tab is None:
            return
        # set dialog and show
        self.window.ui.dialog['rename'].id = 'tab'
        self.window.ui.dialog['rename'].input.setText(tab.title)
        self.window.ui.dialog['rename'].current = idx
        self.window.ui.dialog['rename'].show()

    def update_name(
            self,
            idx: int,
            name: str,
            close: bool = True
    ):
        """
        Update tab title

        :param idx: tab idx
        :param name: new title
        :param close: close dialog
        """
        self.window.core.tabs.update_title(idx, name, name)
        if close:
            self.window.ui.dialog['rename'].close()
        self.debug()

    def update_current_name(self, name: str):
        """
        Update current tab title

        :param name: new title
        """
        self.update_name(self.current, name)

    def update_title(
            self,
            idx: int,
            title: str
    ):
        """
        Update tab title

        :param idx: tab idx
        :param title: new title
        """
        # check if current tab is chat
        if self.get_current_type() != Tab.TAB_CHAT:
            return
        tabs = self.window.ui.layout.get_active_tabs()
        tooltip = title
        tabs.setTabToolTip(idx, tooltip)
        if len(title) > self.TAB_CHAT_MAX_CHARS:
            title = title[:self.TAB_CHAT_MAX_CHARS] + '...'  # truncate to max 8 chars
        self.window.core.tabs.update_title(idx, title, tooltip)
        self.debug()

    def update_title_current(self, title: str):
        """
        Update current tab title

        :param title: new title
        """
        self.update_title(self.current, title)

    def on_load_ctx(self, meta: CtxMeta):
        """
        Load context

        :param meta: context meta
        """
        # get current tab
        tab = self.get_current_tab()
        if tab is not None and tab.type == Tab.TAB_CHAT:
            tab.data_id = meta.id
        self.update_title_current(meta.name)
        self.debug()

    def open_by_type(self, type: int):
        """
        Open first tab by type

        :param type: tab type
        """
        idx = self.window.core.tabs.get_min_idx_by_type(type)
        if idx is not None:
            self.switch_tab_by_idx(idx)

    def new_tab(self, column_idx: int = 0):
        """
        Handle [+] button

        :param column_idx: column index
        """
        # append at the end of column
        idx = self.window.core.tabs.get_max_idx_by_column(column_idx)
        if idx == -1:
            idx = 0
        self.append(
            type=Tab.TAB_CHAT,
            tool_id=None,
            idx=idx,
            column_idx=column_idx
        )

    def restore_data(self):
        """Restore tab data"""
        data = self.window.core.config.get("tabs.opened", [])
        if not data:
            self.switch_tab_by_idx(0, 0)
            return

        # reverse order, second column is first
        data = dict(reversed(list(data.items())))
        for col_idx in data:
            tab_idx = data[col_idx]
            self.switch_tab_by_idx(int(tab_idx), int(col_idx))

        # set default column to 0
        self.column_idx = 0
        self.on_column_changed()
        self.debug()

    def move_tab(
            self,
            idx: int,
            column_idx: int,
            new_column_idx: int
    ):
        """
        Move tab to another column

        :param idx: tab index
        :param column_idx: column index
        :param new_column_idx: new column index
        """
        self.locked = True
        tab = self.window.core.tabs.get_tab_by_index(idx, column_idx)
        self.window.core.tabs.move_tab(tab, new_column_idx)
        self.locked = False
        # switch to new column
        self.column_idx = new_column_idx
        self.on_column_changed()
        # switch to new tab
        self.switch_tab_by_idx(tab.idx, new_column_idx)
        self.debug()

    def is_current_by_type(self, type: int) -> bool:
        """
        Check if one of current tabs is of given type

        :param type: tab type
        :return: True if one of tab is of given type
        """
        for col in self.col:
            pid = self.col[col]
            tab = self.window.core.tabs.get_tab_by_pid(pid)
            if tab is not None and tab.type == type:
                return True

    def is_current_tool(self, tool_id: str) -> bool:
        """
        Check if one of current tabs is of given tool ID

        :param tool_id: tool ID
        :return: True if one of tab is of given tool ID
        """
        for col in self.col:
            pid = self.col[col]
            tab = self.window.core.tabs.get_tab_by_pid(pid)
            if tab is not None and tab.tool_id == tool_id:
                return True
        return False

    def get_current_by_column(self, column_idx: int) -> Optional[Tab]:
        """
        Get current tab by column index

        :param column_idx: column index
        :return: current tab in given column or None if not found
        """
        tabs = self.window.ui.layout.get_tabs_by_idx(column_idx)
        if tabs is None:
            return None
        idx = tabs.currentIndex()
        return self.window.core.tabs.get_tab_by_index(idx, column_idx)

    def is_tool(self, tool_id: str) -> bool:
        """
        Check if one of any tabs is of given tool ID

        :param tool_id: tool ID
        :return: True if one of tab is of given tool ID
        """
        for col in self.col:
            tabs = self.window.ui.layout.get_tabs_by_idx(col)
            for i in range(tabs.count()):
                tab = self.window.core.tabs.get_tab_by_index(i, col)
                if tab is not None and tab.tool_id == tool_id:
                    return True
        return False

    def get_first_tab_by_tool(self, tool_id: str) -> Tab:
        """
        Get first tab index by tool ID

        :param tool_id: tool ID
        :return: tab index if one of tab is of given tool ID, None otherwise
        """
        for col in self.col:
            tabs = self.window.ui.layout.get_tabs_by_idx(col)
            for i in range(tabs.count()):
                tab = self.window.core.tabs.get_tab_by_index(i, col)
                if tab is not None and tab.tool_id == tool_id:
                    return tab

    def switch_to_first_tab_by_tool(self, tool_id: str):
        """
        Switch to first tab by tool ID

        :param tool_id: tool ID
        """
        tab = self.get_first_tab_by_tool(tool_id)
        if tab is not None:
            self.switch_tab_by_idx(tab.idx, tab.column_idx)

    def get_tool_column(self, tool_id: str) -> int:
        """
        Check if one of current tabs is of given tool ID

        :param tool_id: tool ID
        :return: column index if one of tab is of given tool ID, None otherwise
        """
        for col in self.col:
            pid = self.col[col]
            tab = self.window.core.tabs.get_tab_by_pid(pid)
            if tab is not None and tab.tool_id == tool_id:
                return col

    def switch_to_first_chat(self):
        """Switch to first chat tab"""
        if self.is_current_by_type(Tab.TAB_CHAT):
            return
        # abort if active tab is chat
        if self.get_current_type() == Tab.TAB_CHAT:
            return
        # find first chat tab
        for col in self.col:
            pid = self.col[col]
            tab = self.window.core.tabs.get_tab_by_pid(pid)
            if tab is not None and tab.type == Tab.TAB_CHAT:
                self.switch_tab_by_idx(tab.idx, col)
                return

    def focus_by_type(
            self,
            type: str,
            data_id: Optional[int] = None,
            title: Optional[str] = None,
            meta: Optional[CtxMeta] = None
    ):
        """
        Focus by type and optionally update tab data ID and name

        :param type: tab type
        :param data_id: data ID (optional, for chat tab)
        :param title: new tab name (optional, for chat tab)
        :param meta: context meta (optional, for chat tab)
        """
        # try to focus tab
        if self.get_current_type() != type:

            # find the closest tab in current column (on left side)
            current = self.get_current_tab()
            exists = False
            if current:
                idx, column_idx, exists = self.window.core.tabs.get_closest_idx_by_type_exists(
                    current,
                    type,
                    self.column_idx
                )
            if exists:
                tab = self.window.core.tabs.get_tab_by_index(idx, column_idx)
            else:
                # if not exists in current col, then find first idx in any column
                tab = self.window.core.tabs.get_first_by_type(type)

            if tab:
                # if tab is found in current column, switch to it
                tabs = self.window.ui.layout.get_tabs_by_idx(tab.column_idx)
                if tabs:
                    idx = tab.idx
                    if data_id is not None:
                        tab.data_id = data_id
                        if title is not None:
                            self.update_title_current(title)
                    else:
                        self.on_column_focus(tab.column_idx)
                    if meta is not None:
                        self.on_column_focus(tab.column_idx)
                        self.window.controller.ctx.load(meta.id)
                        QTimer.singleShot(100, lambda: self.window.controller.ctx.load(meta.id))
                        self.on_column_focus(tab.column_idx)
                    tabs.setCurrentIndex(idx)
            else:
                # if not found in current column, then check in second column
                second_column_idx = 1 if self.column_idx == 0 else 0
                # get current tab from second column
                tabs = self.window.ui.layout.get_tabs_by_idx(second_column_idx)
                second_tabs_idx = tabs.currentIndex()
                second_tab = self.window.core.tabs.get_tab_by_index(second_tabs_idx, second_column_idx)
                if second_tab is not None and second_tab.type == type:
                    # switch to second column
                    self.on_column_focus(second_column_idx)
                    tabs.setCurrentIndex(second_tabs_idx)
                    if meta:
                        QTimer.singleShot(100, lambda: self.window.controller.ctx.load(meta.id))

            # if second and split screen disabled, then enable it
            if tab and tab.column_idx == 1:
                if not self.is_split_screen_enabled():
                    self.enable_split_screen(update_switch=True)

        self.debug()

    def is_split_screen_enabled(self) -> bool:
        """
        Check if split screen mode is enabled

        :return: True if split screen is enabled, False otherwise
        """
        return self.window.core.config.get("layout.split", False)


    def on_split_screen_changed(self, state: bool):
        """
        On split screen mode changed

        :param state: True if split screen is enabled
        """
        prev_state = self.is_split_screen_enabled()
        self.window.core.config.set("layout.split", state)
        if prev_state != state:
            if self.window.ui.nodes['layout.split'].box.isChecked() != state:
                self.window.ui.nodes['layout.split'].box.setChecked(state)
            self.window.core.config.save()

    def enable_split_screen(self, update_switch: bool = False):
        """
        Enable split screen mode

        :param update_switch: True if switch should be updated
        """
        if self.is_split_screen_enabled():
            return

        self.window.ui.splitters['columns'].setSizes([1, 1])
        self.window.core.config.set("layout.split", True)
        self.window.core.config.save()

        if update_switch:
            self.window.ui.nodes['layout.split'].box.setChecked(True)

    def disable_split_screen(self):
        """
        Disable split screen mode
        """
        self.window.ui.splitters['columns'].setSizes([1, 0])
        # switch to first column
        self.column_idx = 0
        self.on_column_changed()
        self.window.core.config.set("layout.split", False)
        self.window.core.config.save()

    def toggle_split_screen(self, state):
        """
        Toggle split screen mode

        :param state: True if split screen is enabled
        """
        if state:
            self.enable_split_screen()
        else:
            self.disable_split_screen()