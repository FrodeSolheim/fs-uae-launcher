from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals


import weakref
from fsui.qt import Qt, QSize, QAbstractListModel, QModelIndex
from fsui.qt import QListView, QStandardItemModel, QStandardItem
from fsui.qt import QColor, QPixmap, QFrame
import fsui

from fsui.qt.Widget import Widget


class Model(QAbstractListModel):

    def __init__(self, parent):
        QAbstractListModel.__init__(self, parent)
        self.parent = weakref.ref(parent)
        self.count = 0

    #def set_item_count(self, count):
    #    self.count = count

    def rowCount(self, parent):
        #print("returning count", self.count, "for parent", parent)
        #return self.count
        return self.parent().get_item_count()

    def data(self, index, role):
        row = index.row()
        #print("data for", index, "role", role)
        #if role == Qt.SizeHintRole:
        #    return QSize(26, 26)
        if role == Qt.DecorationRole:
            icon = self.parent().get_item_icon(row)
            if icon:
                return icon.qpixmap
            # return icon
        elif role == Qt.DisplayRole:
            return self.parent().get_item_text(row)
        #return QVariant()


class IconView(QListView, Widget):

    def __init__(self, parent):
        if hasattr(parent, "get_container"):
            QListView.__init__(self, parent.get_container())
        else:
            QListView.__init__(self, parent)

        self.setViewMode(QListView.IconMode)
        self.setMovement(QListView.Free)
        self.setFlow(QListView.LeftToRight)
        self.setIconSize(QSize(48, 48))
        self.setWrapping(True)
        self.setWordWrap(True)
        # self.setGridSize(QSize(100, 100))
        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet("QListView {background-color: #aaaaaa; }")

        self.setSpacing(30)
        # self.setAutoFillBackground(True)
        # p = self.palette()
        # p.setColor(self.backgroundRole(), QColor(0xaa, 0xaa, 0xff))
        # self.setPalette(p)

        #self.setSelectionModel()
        #self.model = QStandardItemModel(self)
        self.model = Model(self)
        self.setModel(self.model)
        #self.itemSelectionChanged.connect(self.__selection_changed)
        selection_model = self.selectionModel()

        selection_model.selectionChanged.connect(self.__selection_changed)
        self.activated.connect(self.__activated_signal)
        self.resize(600, 400)

    def __activated_signal(self, index):
        index = index.row()
        self.on_activate_item(index)

    def __selection_changed(self):
        indices = self.selectionModel().selectedIndexes()
        if len(indices) == 0:
            print("FIXME: deselect")
        else:
            model_index = indices[0]
            self.on_select_item(model_index.row())

    def get_item_icon(self, index):
        # return QPixmap(48, 48)
        # return QPixmap("/home/frode/git/fs-uae/fs-uae-launcher/icon/fs-uae"
        #                "-launcher/48.png")
        return fsui.Image("")

    def get_item_text(self, index):
        return ""

    def set_default_icon(self, image):
        pass

    def set_index(self, index):
        if index is None:
            index = -1
        # print(self.rootIndex)
        # idx = QModelIndex.createIndex(index)
        idx = self.model.index(index, 0)
        self.setCurrentIndex(idx)

    def select_item(self, index):
        self.set_index(index)

    def on_select_item(self, index):
        pass

    def on_activate_item(self, index):
        pass

    def update(self):
        count = self.get_item_count()
        self.dataChanged(
            self.model.createIndex(0, 0),
            self.model.createIndex(count, 0))
