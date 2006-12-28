#!/usr/bin/python
# -*- coding: utf8 -*-
#
# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (31 August 2006)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Developed by:
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
#
# This module is working on overview of source and target

from PyQt4 import QtCore, QtGui
from editor.ui.Ui_Overview import Ui_Form
import editor.modules.World as World

class OverviewDock(QtGui.QDockWidget):
    def __init__(self, parent):
        QtGui.QDockWidget.__init__(self, parent)
        self.setObjectName("overviewDock")
        self.setWindowTitle(self.tr("Overview"))
        self.form = QtGui.QWidget(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self.form)
        self.setWidget(self.form)
        
        # set up table appearance and behavior
        self.headerLabels = [self.tr("Index"), self.tr("Source"), self.tr("Target"), self.tr("Status")]
        self.ui.tableOverview.setColumnCount(len(self.headerLabels))
        self.ui.tableOverview.setRowCount(0)
        self.ui.tableOverview.setHorizontalHeaderLabels(self.headerLabels)
        self.ui.tableOverview.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ui.tableOverview.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.ui.tableOverview.horizontalHeader().setSortIndicatorShown(True)
        self.ui.tableOverview.resizeColumnToContents(0)
        self.ui.tableOverview.resizeColumnToContents(3)
        self.ui.tableOverview.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.ui.tableOverview.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Stretch)
        self.ui.tableOverview.horizontalHeader().setHighlightSections(False)
        self.ui.tableOverview.verticalHeader().hide()
        self.applySettings()
        self.fuzzyIcon = QtGui.QIcon("../images/fuzzy.png")
        self.noteIcon = QtGui.QIcon("../images/note.png")
        self.approvedIcon = QtGui.QIcon("../images/approved.png")
        self.blankIcon = QtGui.QIcon()
        self.normalState = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        self.indexMaxLen = 0
        self.units = []
        self.visibleRow = []
        self.lastTarget = None
        
        self.changedSignal = QtCore.SIGNAL("currentCellChanged(int, int, int, int)")
        self.connect(self.ui.tableOverview, self.changedSignal, self.emitCurrentIndex)
        self.connect(self.ui.tableOverview.model(), QtCore.SIGNAL("layoutChanged()"), self.showFilteredItems)
    
    def closeEvent(self, event):
        """
        set text of action object to 'show Overview' before closing Overview
        @param QCloseEvent Object: received close event when closing widget
        """
        QtGui.QDockWidget.closeEvent(self, event)
        self.toggleViewAction().setChecked(False)
        
    def slotNewUnits(self, units):
        """
        set the filter to filterAll, fill the table with units.
        @param units: list of unit class.
        """
        self.ui.tableOverview.setEnabled(bool(units))
        self.indexMaxLen = len(str(len(units)))
        self.filter = World.filterAll
        self.units = units
        self.ui.tableOverview.clear()
        self.ui.tableOverview.setHorizontalHeaderLabels(self.headerLabels)
        self.ui.tableOverview.setSortingEnabled(False)
        self.ui.tableOverview.setRowCount(0)
        
        self.setUpdatesEnabled(False)
        for unit in units:
            if (self.filter & unit.x_editor_state):
                self.addUnit(unit)
        self.ui.tableOverview.setSortingEnabled(True)
        self.ui.tableOverview.sortItems(0)
        self.ui.tableOverview.resizeRowsToContents()
        self.setUpdatesEnabled(True)
        
        if (self.ui.tableOverview.rowCount > 0):
            self.lastTarget = self.ui.tableOverview.item(0, 2).text()

    def filterChanged(self, filter, lenFilter):
        """
        show the items which are in filter.
        @param filter: helper constants for filtering.
        @param lenFilter: len of filtered items.
        """
        if (filter == self.filter):
            return
        self.filter = filter
        self.showFilteredItems()
        
    def addUnit(self, unit):
        """
        add the unit to table.
        @param unit: unit class.
        """
        row = self.ui.tableOverview.rowCount()
        self.ui.tableOverview.setRowCount(row + 1)
        item = QtGui.QTableWidgetItem(self.indexString(row + 1))
        item.setTextAlignment(QtCore.Qt.AlignRight + QtCore.Qt.AlignVCenter)
        item.setFlags(self.normalState)
        item.setData(QtCore.Qt.UserRole, QtCore.QVariant(row))
        unit.x_editor_tableItem = item
        self.ui.tableOverview.setItem(row, 0, item)
        self.markComment(row, unit.getnotes())
        
        item = QtGui.QTableWidgetItem(unit.source)
        item.setFlags(self.normalState)
        self.ui.tableOverview.setItem(row, 1, item)
        
        item = QtGui.QTableWidgetItem(unit.target)
        self.ui.tableOverview.setItem(row, 2, item)
        
        item = QtGui.QTableWidgetItem()
        item.setFlags(self.normalState)
        self.ui.tableOverview.setItem(row, 3, item)
        self.markState(row, unit.x_editor_state)
    
    def emitCurrentIndex(self, row, col, preRow, preCol):
        """
        send targetChanged if unit's taget has changed, and send currentIndex
        with selected unit's index.
        """
        # emit targetChanged if previous item has been edited.
        item = self.ui.tableOverview.item(preRow, 2)
        if hasattr(item, "text"):
            target = item.text()
            if (self.lastTarget != target):
                self.markState(preRow, not World.fuzzy)
                self.emit(QtCore.SIGNAL("targetChanged"), target)
        # emit the index of current unit.
        item = self.ui.tableOverview.item(row, 0)
        
        if (hasattr(item, "data")):
            index = item.data(QtCore.Qt.UserRole).toInt()[0]
            self.emit(QtCore.SIGNAL("filteredIndex"), index)
            self.lastTarget = self.ui.tableOverview.item(row, 2).text()
    
    def updateView(self, unit):
        """
        highlight the table's row, mark comment icon, mark state icon,
        and set the target text according to unit.
        @param unit: unit class
        """
        if (not unit) or (not hasattr(unit, "x_editor_tableItem")):
            return
        row = self.ui.tableOverview.row(unit.x_editor_tableItem)
        
        targetItem = self.ui.tableOverview.item(row, 2)
        targetItem.setText(unit.target)
        
        self.markComment(row, unit.getnotes())
        self.markState(row, unit.x_editor_state)
        
        self.disconnect(self.ui.tableOverview, self.changedSignal, self.emitCurrentIndex)
        self.ui.tableOverview.selectRow(row)
        self.connect(self.ui.tableOverview, self.changedSignal, self.emitCurrentIndex)
        
        self.ui.tableOverview.scrollToItem(unit.x_editor_tableItem)
        self.emitFirstLastUnit()
    
    def markState(self, index, state):
        """
        mark icon indicate state of unit on note column.
        @param index: row in table.
        @param state: unit's state.
        """
        item = self.ui.tableOverview.item(index, 3)
        if (state & World.fuzzy):
            item.setIcon(self.fuzzyIcon)
            item.setToolTip("fuzzy")
        else:
            item.setIcon(self.blankIcon)
            item.setToolTip("")
    
    def applySettings(self):
        """
        set color and font to the table.
        """
        overviewColor = World.settings.value("overviewColor")
        if (overviewColor.isValid()):
            colorObj = QtGui.QColor(overviewColor.toString())
            palette = self.ui.tableOverview.palette()
            palette.setColor(QtGui.QPalette.Active, QtGui.QPalette.ColorRole(QtGui.QPalette.Text), colorObj)
            palette.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.ColorRole(QtGui.QPalette.Text), colorObj)
            self.ui.tableOverview.setPalette(palette)

        font = World.settings.value("overviewFont")
        if (font.isValid()):
            fontObj = QtGui.QFont()
            if (fontObj.fromString(font.toString())):
              self.ui.tableOverview.setFont(fontObj)
              
        font = World.settings.value("overviewHeaderFont")
        if (font.isValid()):
            fontObj = QtGui.QFont()
            if (fontObj.fromString(font.toString())):
              self.ui.tableOverview.horizontalHeader().setFont(fontObj)
              
        self.ui.tableOverview.resizeRowsToContents()
        
    def showFilteredItems(self):
        """
        hide and show the item in the table according to filter.
        calculating the visibleRow for navigation.
        """
        i = 0
        self.visibleRow = []
        for unit in self.units:
            if hasattr(unit, "x_editor_tableItem"):
                item = unit.x_editor_tableItem
                row = self.ui.tableOverview.row(item)
                if (unit.x_editor_state & self.filter):
                    self.ui.tableOverview.showRow(row)
                    self.visibleRow.append(row)
                    item.setData(QtCore.Qt.UserRole, QtCore.QVariant(i))
                    i += 1
                else:
                    self.ui.tableOverview.hideRow(row)
        self.ui.tableOverview.resizeRowsToContents()
        self.emitFirstLastUnit()
    
    def indexString(self, index):
        """converting index which is integer string."""
        return str(index).rjust(self.indexMaxLen) + "  "
    
    def markComment(self, index, note):
        """
        mark icon indicate unit has comment on index column, and add tooltips.
        @param index: row in table.
        @param note: unit's comment as tooltips in index column.
        """
        item = self.ui.tableOverview.item(index, 0)
        if (note):
            item.setIcon(self.noteIcon)
            item.setToolTip(unicode(note))
        else:
            item.setIcon(self.blankIcon)
            item.setToolTip("")
    
    def scrollPrevious(self):
        """move to previous row inside the table."""
        currentRow = self.ui.tableOverview.currentRow()
        if (currentRow > 0):
            currentRow -= 1
            self.ui.tableOverview.selectRow(currentRow)
    
    def scrollNext(self):
        """move to next row inside the table."""
        currentRow = self.ui.tableOverview.currentRow()
        if (currentRow < len(self.visibleRow) - 1):
            currentRow += 1
            self.ui.tableOverview.selectRow(currentRow)
    
    def scrollFirst(self):
        """move to first row of the table."""
        self.ui.tableOverview.selectRow(0)
    
    def scrollLast(self):
        """move to last row of the table."""
        self.ui.tableOverview.selectRow(len(self.visibleRow) - 1)
    
    def emitFirstLastUnit(self):
        currentRow = self.ui.tableOverview.currentRow()
        lenSelItem = len(self.ui.tableOverview.selectedItems())
        firstUnit = (currentRow == 0) or (lenSelItem == 0)
        lastUnit = (currentRow >= len(self.visibleRow) -1)
        self.emit(QtCore.SIGNAL("toggleFirstLastUnit"), firstUnit, lastUnit)
    
if __name__ == "__main__":
    import sys, os
    # set the path for QT in order to find the icons
    QtCore.QDir.setCurrent(os.path.join(sys.path[0], "..", "ui"))
    app = QtGui.QApplication(sys.argv)
    overview = OverviewDock(None)
    overview.show()
    sys.exit(app.exec_())
