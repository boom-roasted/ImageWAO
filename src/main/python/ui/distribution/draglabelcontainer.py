from PySide2 import QtWidgets, QtGui, QtCore

from .draglabel import DragLabel


class DragLabelContainer(QtWidgets.QWidget):
    """The widget that can accept the drag and
    drop events from DragLabels.
    """

    def __init__(self):
        super().__init__()

        newPalette = self.palette()
        newPalette.setColor(QtGui.QPalette.Window, QtCore.Qt.blue)
        self.setPalette(newPalette)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(DragLabel(self, "hello"))
        layout.addWidget(DragLabel(self, "another one"))
        self.setLayout(layout)

        self.setStyleSheet("DragLabelContainer { border: blue }")
        self.setAcceptDrops(True)

        self.setMinimumSize(400, 100)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        if event.mimeData().hasFormat("text/plain"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent):
        pass

    def dropEvent(self, event: QtGui.QDropEvent):
        if event.mimeData().hasText():
            mime = event.mimeData()
            name = mime.text()

            self.layout().addWidget(DragLabel(self, name))

            if event.source() in self.children():
                event.setDropAction(QtCore.Qt.MoveAction)
            else:
                event.setDropAction(QtCore.Qt.CopyAction)

            event.accept()
        else:
            event.ignore()
