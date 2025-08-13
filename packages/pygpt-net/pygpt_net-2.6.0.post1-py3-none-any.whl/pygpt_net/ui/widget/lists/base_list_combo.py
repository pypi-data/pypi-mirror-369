#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2025.08.02 20:00:00                  #
# ================================================== #

from PySide6.QtWidgets import QHBoxLayout, QWidget, QComboBox

from pygpt_net.ui.widget.option.combo import SeparatorComboBox, NoScrollCombo


class BaseListCombo(QWidget):
    def __init__(self, window=None, id: str = None):
        """
        Base list combo

        :param window: main window
        :param id: option id
        """
        super(BaseListCombo, self).__init__(window)
        self.window = window
        self.id = id
        self.current_id = None
        self.keys = []
        self.real_time = False
        self.combo = NoScrollCombo()
        self.combo.currentIndexChanged.connect(self.on_combo_change)
        self.initialized = False
        self.locked = False

        # add items
        self.update()

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.combo)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.fit_to_content()
        self.initialized = True

    def update(self):
        """Prepare items"""
        self.combo.clear()  # Clear combo before updating with new items
        if isinstance(self.keys, list):
            for item in self.keys:
                if isinstance(item, dict):
                    for key, value in item.items():
                        self.combo.addItem(value, key)
                else:
                    self.combo.addItem(item, item)
        elif isinstance(self.keys, dict):
            for key, value in self.keys.items():
                if key.startswith("separator::"):
                    self.combo.addSeparator(value)
                else:
                    self.combo.addItem(value, key)

    def set_value(self, value):
        """
        Set value

        :param value: value
        """
        self.locked = True
        index = self.combo.findData(value)
        if index != -1:
            self.combo.setCurrentIndex(index)
        self.locked = False

    def get_value(self):
        """
        Get value

        :return: value
        """
        return self.current_id

    def has_key(self, name: str) -> bool:
        """
        Check if combo has key

        :param name: key name
        :return:
        """
        if isinstance(self.keys, list):
            for key in self.keys:
                if isinstance(key, dict):
                    if name in key:
                        return True
                elif name == key:
                    return True
        elif isinstance(self.keys, dict):
            if name in self.keys:
                return True
        return False

    def set_keys(self, keys):
        """
        Set keys

        :param keys: keys
        """
        self.locked = True
        self.keys = keys
        self.update()  # Auto-clear handled in update
        self.locked = False

    def on_combo_change(self, index):
        """
        On combo change

        :param index: combo index
        """
        if not self.initialized or self.locked:
            return
        self.current_id = self.combo.itemData(index)

    def fit_to_content(self):
        """Fit to content"""
        self.combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)