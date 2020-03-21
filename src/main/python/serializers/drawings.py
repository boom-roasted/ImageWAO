
import json

from PySide2 import QtWidgets, QtCore, QtGui

import scenegraphics as sg


class GrahphicItemRepresentation:

    def __init__(self, name, geom, pen):
        '''
        Minimum objects required to re-create an item
        drawn in a scene.

        Need name of item (Rect, Ellipse, Line)
        Need geometry of item (QRectF, QLine), 
        and the pen used to draw the item.
        '''
        self.name = name
        self.geom = geom
        self.pen = pen

    @property
    def args(self):
        '''
        Arguments necessary to recreate the graphical
        geometry.
        '''
        if self.name == 'Rect':
            rect = self.geom
            args = [rect.x(), rect.y(), rect.width(), rect.height()]

        elif self.name == 'Ellipse':
            rect = self.geom
            args = [rect.x(), rect.y(), rect.width(), rect.height()]

        elif self.name == 'Line':
            line = self.geom
            args = [line.x1(), line.y1(), line.x2(), line.y2()]

        return args

    @property
    def penColor(self):
        '''
        Pen color in #RRGGBB format
        '''
        return self.pen.color().name()

    @property
    def penWidth(self):
        '''
        Pen width as an integer
        '''
        return self.pen.width()

    @property
    def center(self):
        '''
        Center QPointF of the geometry
        '''
        return self.geom.center()

    def offset(self, x, y):
        '''
        Offset the geometry of this point by a given 
        x and y value.
        '''
        self.geom.translate(QtCore.QPointF(x, y))

    def scale(self, sf):
        '''
        Scales the geometry of this point by a
        scale factor.
        '''
        if self.name in ('Rect', 'Ellipse'):
            x = self.geom.x() * sf
            y = self.geom.y() * sf
            width = self.geom.width() * sf
            height = self.geom.height() * sf
            self.geom.setRect(x, y, width, height)

        elif self.name in 'Line':
            x1 = self.geom.x1() * sf
            y1 = self.geom.y1() * sf
            x2 = self.geom.x2() * sf
            y2 = self.geom.y2() * sf
            self.geom.setP1(QtCore.QPointF(x1, y1))
            self.geom.setP2(QtCore.QPointF(x2, y2))

        self.pen.setWidth(self.pen.width() * sf)


class JSONDrawnItems:
    '''
    Contains methods useful for encoding and
    decoding drawn items on a graphics scene.

    This class allows those items to be "offset"
    when the image they were drawn on is not necessarily
    the image that they should be saved on.

    This happens most commonly when imaged are
    "merged" before they are displayed in the viewer.
    '''

    def __init__(self, reps: GrahphicItemRepresentation):
        '''
        Initialize class using one of the static methods:
        * loadItems, for loading scene items
        * loads, for loading via an encoded JSON string

        Item type, geometry, and pen color/width are tracked.
        '''

        # Internally store the graphical representation
        # of these scene objects. Contains nough information
        # to recreate from primitive objects
        self._reps:GrahphicItemRepresentation = reps

        # To iterate over these representations, we need an
        # iterater tracking variable
        self._index = 0

    @staticmethod
    def loadItems(items):
        '''
        Initialize with a list of QGraphicsItems.
        Supported items:
        QGraphicsRectItem
        QGrahpicsEllipseItem
        QGraphicsLineItem
        '''

        representations = []

        for item in items:

            # Encoded data differs depending on item type
            # Need to save as much data as necessary to re-create item
            if isinstance(item, QtWidgets.QGraphicsRectItem):
                name = 'Rect'
                geom = item.rect()

            elif isinstance(item, QtWidgets.QGraphicsEllipseItem):
                name = 'Ellipse'
                geom = item.rect()

            elif isinstance(item, QtWidgets.QGraphicsLineItem):
                name = 'Line'
                geom = item.line()

            else:
                print(f'Unrecognized item: {item}')
                continue

            # All graphics items have associated pens
            if isinstance(item, QtWidgets.QGraphicsItem):
                pen = item.pen()

            representations.append(GrahphicItemRepresentation(name, geom, pen))
        
        return JSONDrawnItems(representations)

    @staticmethod
    def loads(s):
        '''
        Load an encoded JSON formatted string of drawing items
        as their geometric representation (QRectF, QLine, QEllipse)
        '''

        if s is None:
            return JSONDrawnItems([])
            
        representations = []
        data = json.loads(s)

        for dataItem in data:

            # TODO: Error checking -- enough data in list?
            # correct data in list?
            name = dataItem[0]
            args = dataItem[1]
            penColor = dataItem[2]
            penWidth = dataItem[3]

            # Setup pen
            pen = QtGui.QPen(penColor) # Does this color need to be a QColor?
            pen.setWidth(penWidth)

            if name == 'Rect':
                geom = QtCore.QRectF(*args)
            elif name == 'Ellipse':
                geom = QtCore.QRectF(*args)
            elif name == 'Line':
                geom = QtCore.QLineF(*args)

            representations.append(GrahphicItemRepresentation(name, geom, pen))
        
        return JSONDrawnItems(representations)

    def dumps(self):
        '''
        Return the encoded drawing items as a JSON formatted string
        '''
        if len(self._reps) == 0:
            return None

        encoded = []
        for rep in self._reps:
            encoded.append([rep.name, rep.args, rep.penColor, rep.penWidth])

        return json.dumps(encoded)

    def addToScene(self, scene:QtWidgets.QGraphicsScene):
        '''
        Adds the internal geometries to a scene,
        returning the list of items
        '''
        items = []
        for rep in self._reps:
            if rep.name == 'Rect':
                item = sg.SceneCountDataRect.create(rep.geom, rep.pen)
            elif rep.name == 'Ellipse':
                item = sg.SceneCountDataEllipse.create(rep.geom, rep.pen)
            elif rep.name == 'Line':
                item = sg.SceneCountDataLine.create(rep.geom, rep.pen)
            else:
                item = None

            if item is not None:
                scene.addItem(item)
                items.append(item)

        return items

    def paintToDevice(self, device, sf=1):
        '''
        Paint the internal geometries to a
        paint device (QImage, QPixmap, etc.)

        Optionally include a scaling factor if
        you are painting to a different size than what
        the drawing was originally drawn on.
        '''
        painter = QtGui.QPainter(device)
        for rep in self._reps:
            painter.setPen(rep.pen)
            rep.scale(sf)
            painter.setPen(rep.pen)
            if rep.name == 'Rect':
                painter.drawRect(rep.geom)
            elif rep.name == 'Ellipse':
                painter.drawEllipse(rep.geom)
            elif rep.name == 'Line':
                painter.drawLine(rep.geom)
        painter.end()

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index == len(self._reps):
            raise StopIteration
        data = self._reps[self._index]
        self._index += 1
        return data

