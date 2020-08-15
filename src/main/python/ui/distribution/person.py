from typing import List

from PySide2 import QtWidgets

from .transect import Transect
from .dragtransect import DragTransect
from .dragtransectcontainer import DragTransectContainer


class Person(QtWidgets.QWidget):
    def __init__(self, name: str):
        super().__init__()

        self.nameLine = QtWidgets.QLineEdit(self)
        self.nameLine.setText(name)
        self.nameLine.setFixedWidth(self.nameLine.width())

        self.assignedTransectList = DragTransectContainer()
        self.assignedTransectList.contentsChanged.connect(self.updateNumPhotos)

        self.numPhotos = QtWidgets.QLabel(self)
        self.numPhotos.setText("0")
        fm = self.numPhotos.fontMetrics()
        self.numPhotos.setFixedWidth(fm.width("###"))

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.nameLine)
        layout.addWidget(self.assignedTransectList)
        layout.addWidget(self.numPhotos)
        self.setLayout(layout)

    def addTransect(self, transect: Transect):
        self.assignedTransectList.addTransect(transect)

    def removeTransects(self) -> List[DragTransect]:
        return self.assignedTransectList.removeTransects()

    def updateNumPhotos(self):
        self.numPhotos.setText(str(self.assignedTransectList.numPhotos()))
