
import os
from pathlib import Path

from PySide2 import QtCore, QtWidgets, QtGui

from transects import TransectSaveData, TransectSaveDatas
from base import QWorker, config
from base.primatives import CountDataSet

from .enums import UserRoles


class TotalsModel(QtCore.QAbstractListModel):

    loadStarted = QtCore.Signal()
    loadProgress = QtCore.Signal(int)
    loadFinished = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self._data = TransectSaveDatas()
        self._parentDir = None
        self.inTransect = False

        self._loadWorker = None
        self._threadpool = QtCore.QThreadPool()

    def rowCount(self, index=QtCore.QModelIndex()):
        ''' Returns the number of rows the model holds. '''
        if self.inTransect:
            return self._data.numImages()
        else:
            return len(self._data.groupedDict())

    def data(self, index, role=QtCore.Qt.DisplayRole):
        '''
        Depending on the index and role given, return data.
        If not returning data, return None (equv. to Qt's QVariant)
        '''
        if not index.isValid():
            return None

        if index.row() < 0:
            return None

        if role == QtCore.Qt.DisplayRole:
            if self.inTransect:
                return self._data.animalsAt(index.row())
            else:
                return self._data.summaryAt(index.row())

        if role == UserRoles.AbsolutePath:
            if self.inTransect:
                _folderName = self._data.allImages()[index.row()]
            else:
                _folderName = list(self._data.groupedDict().keys())[index.row()]

            return str(Path(self._parentDir) / _folderName)
        return None

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        '''
        No headers are displayed.
        '''
        if (role == QtCore.Qt.SizeHintRole):
            return QtCore.QSize(1, 1)

        return None

    def flags(self, index):
        ''' Set the item flag at the given index. '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemFlags(
            QtCore.QAbstractListModel.flags(self, index)
            # | QtCore.Qt.ItemIsEditable
        )

    def refresh(self):
        self.readDirectory(self._parentDir)

    def readDirectory(self, fp):
        ''' Populates model from directory. `fp`: any Path()-able type'''
        self._parentDir = str(fp)
        fp = Path(fp)

        # Error checks
        if not fp.exists():
            raise ValueError(f'Cannot read data from path that does not exist: {fp}')
        if not fp.is_dir():
            raise ValueError(f'Can only read from dir, not file: {fp}')
        
        # If the .marked/ folder exists, this is a single transect
        markedFolder = fp / config.markedImageFolder
        if markedFolder.exists():

            self.inTransect = True

            # If the save file exists, read it
            saveFile = fp / config.markedDataFile
            if saveFile.exists():
                saveDatas = TransectSaveDatas()
                saveDatas.load(saveFile)
                # saveData = TransectSaveData.load(saveFile)
                # dataSet = saveData.countDataSet()
                # self._resetData(dataSet)
                self._resetData(saveDatas)
            else:
                self._resetData(TransectSaveDatas())

        # Otherwise, try to find all .marked/ folders within this dir
        else:

            self.inTransect = False

            markedFolderMatchString = Path(config.markedImageFolder).name
            subfolders = subfolders= [f for f in os.scandir(fp) if f.is_dir()]
            filesToLoad = []
            for dirname in list(subfolders):
                allfolders = fast_scandir(dirname)
                markedFolders = [d for d in allfolders if d.name == markedFolderMatchString]
                for markedFolder in markedFolders:
                    saveFile = Path(markedFolder) / Path(config.markedDataFile).name
                    if saveFile.exists():
                        filesToLoad.append((dirname.name, saveFile))
            if filesToLoad:
                self._loadFiles(filesToLoad)
            else:
                self._resetData(TransectSaveDatas())

    def _loadFiles(self, filesToLoad):
        '''
        Loads files from `filesToLoad` list of (topLevelGroup, fp)
        '''
        saveDatas = TransectSaveDatas()
        for topLevel, saveFile in filesToLoad:
            saveDatas.load(saveFile, groupName=topLevel)
            # ds = saveData.countDataSet(topLevel=topLevel)
            # dataSet += ds
        self._resetData(saveDatas)

    def _resetData(self, data):
        self.beginResetModel()
        self._data = data.sorted()
        self.endResetModel()

    def export(self):
        ''' Exports all data. Rn just copies data to clipboard. '''
        clipboard = QtWidgets.QApplication.instance().clipboard()
        txt = self._data.clipboardText()
        clipboard.setText(txt)
        QtWidgets.QMessageBox.information(
            self.parent(), 'Copied!',
            'Count information copied to the clipboard!'
            '\nPaste into Excel or a notepad to view it.')

    def indexOfName(self, name):
        ''' Returns the first index matching the given name '''
        if self.inTransect:
            row = self._data.indexOfImageName(name)
        else:
            row = self._data.indexOfGroupName(name)

        if row is not None:
            return self.index(row, 0)
        return None

def fast_scandir(dirname):
    '''
    Quickly scans all subfolders recursively.
    Faster than `os.walk` and much faster than `glob`.
    Returns list of os.DirEntry() objects.
    '''
    subfolders= [f for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname))
    return subfolders


