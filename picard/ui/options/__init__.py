# -*- coding: utf-8 -*-
#
# Picard, the next-generation MusicBrainz tagger
# Copyright (C) 2006 Lukáš Lalinský
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

from PyQt4 import QtCore, QtGui
from picard.api import IOptionsPage
from picard.component import Component, ExtensionPoint
from picard.config import Option
from picard.ui.options import (
    about,
    advanced,
    cdlookup,
    general,
    metadata,
    naming,
    proxy,
    scripting,
    tags,
)

class OptionsDialog(QtGui.QDialog):

    options = [
        Option("persist", "options_position", QtCore.QPoint(),
               QtCore.QVariant.toPoint),
        Option("persist", "options_size", QtCore.QSize(560, 400),
               QtCore.QVariant.toSize),
        Option("persist", "options_splitter", QtCore.QByteArray(),
               QtCore.QVariant.toByteArray),
    ]

    def add_pages(self, parent, parent_item):
        pages = [page for page in self.pages if page.get_page_info()[2] == parent]
        pages.sort(lambda a, b: cmp(a.get_page_info()[3], b.get_page_info()[3]))

        for provider in pages:
            info = provider.get_page_info()
            name = info[0]
            page = provider.get_page_widget()
            item = QtGui.QTreeWidgetItem(parent_item)
            item.setText(0, name)
            if page:
                self.item_to_page[item] = page
                self.page_to_item[info[1]] = item
                self.ui.pages_stack.addWidget(page)
            else:
                item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.add_pages(info[1], item)

    def __init__(self, parent, pages, default_page):
        QtGui.QDialog.__init__(self, parent)

        from picard.ui.ui_options import Ui_Dialog
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.pages = pages

        self.ui.pages_tree.setHeaderLabels([""])
        self.ui.pages_tree.header().hide()
        self.connect(self.ui.pages_tree,
                     QtCore.SIGNAL("itemSelectionChanged()"), self.switch_page)

        self.default_page = default_page
        self.item_to_page = {}
        self.page_to_item = {}
        self.add_pages(None, self.ui.pages_tree)

        if default_page is not None:
            item = self.page_to_item[default_page]
        else:
            item = self.ui.pages_tree.topLevelItem(0)
        self.ui.pages_tree.setCurrentItem(item)

        self.restoreWindowState()

    def switch_page(self):
        items = self.ui.pages_tree.selectedItems()
        if items:
            page = self.item_to_page[items[0]]
            self.ui.pages_stack.setCurrentWidget(page)

    def accept(self):
        for page in self.pages:
            page.save_options()
        self.saveWindowState()
        QtGui.QDialog.accept(self)

    def closeEvent(self, event):
        self.saveWindowState()
        event.accept()

    def saveWindowState(self):
        self.config.persist["options_position"] = self.pos()
        self.config.persist["options_size"] = self.size()
        self.config.persist["options_splitter"] = self.ui.splitter.saveState()

    def restoreWindowState(self):
        self.move(self.config.persist["options_position"])
        self.resize(self.config.persist["options_size"])
        self.ui.splitter.restoreState(self.config.persist["options_splitter"])


class OptionsDialogProvider(Component):

    pages = ExtensionPoint(IOptionsPage)

    def get_options_dialog(self, parent=None, default_page=None):
        self.dlg = OptionsDialog(parent, self.pages, default_page)
        return self.dlg

