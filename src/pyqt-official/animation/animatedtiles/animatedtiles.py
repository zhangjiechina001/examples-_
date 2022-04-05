#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


from PyQt5.QtCore import (pyqtProperty, pyqtSignal, QEasingCurve, QObject,
                          QParallelAnimationGroup, QPointF, QPropertyAnimation, qrand, QRectF,
                          QState, QStateMachine, Qt, QTimer)
from PyQt5.QtGui import (QBrush, QLinearGradient, QPainter, QPainterPath,
                         QPixmap)
from PyQt5.QtWidgets import (QApplication, QGraphicsItem, QGraphicsPixmapItem,
                             QGraphicsRectItem, QGraphicsScene, QGraphicsView, QGraphicsWidget,
                             QStyle)

import animatedtiles_rc


# PyQt doesn't support deriving from more than one wrapped class so we use
# composition and delegate the property.
class Pixmap(QObject):
    def __init__(self, pix):
        super(Pixmap, self).__init__()

        self.pixmap_item = QGraphicsPixmapItem(pix)
        self.pixmap_item.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def _set_pos(self, pos):
        self.pixmap_item.setPos(pos)

    pos = pyqtProperty(QPointF, fset=_set_pos)


class Button(QGraphicsWidget):
    pressed = pyqtSignal()

    def __init__(self, pixmap, parent=None):
        super(Button, self).__init__(parent)

        self._pix = pixmap

        self.setAcceptHoverEvents(True)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def boundingRect(self):
        return QRectF(-65, -65, 130, 130)

    def shape(self):
        path = QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def paint(self, painter, option, widget):
        print('paint')
        down = option.state & QStyle.State_Sunken

        color_0 = Qt.white if option.state & QStyle.State_MouseOver else Qt.lightGray
        color_1 = Qt.darkGray
        if down:
            color_pen_0, color_1 = color_1, color_0

        r = self.boundingRect()
        grad = QLinearGradient(r.topLeft(), r.bottomRight())
        grad.setColorAt(0, color_0)
        grad.setColorAt(1, color_1)

        painter.setPen(Qt.darkGray)
        painter.setBrush(grad)
        painter.drawEllipse(r)

        color_pen_0 = Qt.darkGray
        color_pen_1 = Qt.lightGray
        if down:
            color_pen_0, color_pen_1 = color_pen_1, color_pen_0
        grad.setColorAt(0, color_pen_0)
        grad.setColorAt(1, color_pen_1)

        painter.setPen(Qt.NoPen)
        painter.setBrush(grad)

        if down:
            painter.translate(2, 2)

        painter.drawEllipse(r.adjusted(5, 5, -5, -5))
        painter.drawPixmap(int(-self._pix.width() / 2), int(-self._pix.height() / 2),
                           self._pix)

    def mousePressEvent(self, ev):
        self.pressed.emit()
        self.update()

    def mouseReleaseEvent(self, ev):
        self.update()


class View(QGraphicsView):
    def resizeEvent(self, event):
        super(View, self).resizeEvent(event)
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)


if __name__ == '__main__':

    import sys
    import math

    app = QApplication(sys.argv)

    kineticPix = QPixmap(':/images/kinetic.png')
    bgPix = QPixmap(':/images/Time-For-Lunch-2.jpg')

    w,h=700,700
    scene = QGraphicsScene(-w//2, -h//2, w, h)

    items = []
    for i in range(64):
        item = Pixmap(kineticPix)
        item.pixmap_item.setOffset(-kineticPix.width() / 2,
                                   -kineticPix.height() / 2)
        item.pixmap_item.setZValue(i)
        scene.addItem(item.pixmap_item)
        items.append(item)

    # Buttons.
    buttonParent = QGraphicsRectItem()
    ellipseButton = Button(QPixmap(':/images/ellipse.png'), buttonParent)
    figure8Button = Button(QPixmap(':/images/figure8.png'), buttonParent)
    randomButton = Button(QPixmap(':/images/random.png'), buttonParent)
    tiledButton = Button(QPixmap(':/images/tile.png'), buttonParent)
    centeredButton = Button(QPixmap(':/images/centered.png'), buttonParent)

    ellipseButton.setPos(-100, -100)
    figure8Button.setPos(100, -100)
    randomButton.setPos(0, 0)
    tiledButton.setPos(-100, 100)
    centeredButton.setPos(100, 100)

    scene.addItem(buttonParent)
    buttonParent.setScale(0.75)
    buttonParent.setPos(200, 200)
    buttonParent.setZValue(100)

    # States.
    rootState = QState()
    ellipseState = QState(rootState)
    figure8State = QState(rootState)
    randomState = QState(rootState)
    tiledState = QState(rootState)
    centeredState = QState(rootState)

    calc_count = len(items) - 1
    # Values.
    for i, item in enumerate(items):
        # Ellipse.
        ellipseState.assignProperty(item, 'pos',
                                    QPointF(math.cos((i / calc_count) * 6.28) * 250,
                                            math.sin((i / calc_count) * 6.28) * 250))

        # Figure 8.
        figure8State.assignProperty(item, 'pos',
                                    QPointF(math.sin((i / calc_count) * 6.28) * 250,
                                            math.sin(((i * 2) / calc_count) * 6.28) * 250))

        # Random.
        randomState.assignProperty(item, 'pos',
                                   QPointF(-250 + qrand() % 500, -250 + qrand() % 500))

        # Tiled.
        tiledState.assignProperty(item, 'pos',
                                  QPointF(((i % 8) - 4) * kineticPix.width() + kineticPix.width() / 2,
                                          ((i // 8) - 4) * kineticPix.height() + kineticPix.height() / 2))

        # Centered.
        centeredState.assignProperty(item, 'pos', QPointF())

    # Ui.
    view = View(scene)
    view.setWindowTitle("Animated Tiles")
    view.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
    view.setBackgroundBrush(QBrush(bgPix))
    view.setCacheMode(QGraphicsView.CacheBackground)
    view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
    view.show()

    states = QStateMachine()
    states.addState(rootState)
    states.setInitialState(rootState)
    rootState.setInitialState(centeredState)

    group = QParallelAnimationGroup()
    for i, item in enumerate(items):
        anim = QPropertyAnimation(item, b'pos')
        anim.setDuration(750 + i * 25)
        anim.setEasingCurve(QEasingCurve.InOutBack)
        group.addAnimation(anim)

    action_state = [(ellipseButton, ellipseState), (figure8Button, figure8State), (randomButton, randomState),
                    (tiledButton, tiledState), (centeredButton, centeredState)]
    for a, s in action_state:
        trans = rootState.addTransition(a.pressed, s)
        trans.addAnimation(group)

    timer = QTimer()
    timer.start(1000)
    timer.setSingleShot(True)
    trans = rootState.addTransition(timer.timeout, ellipseState)
    trans.addAnimation(group)

    states.start()

    sys.exit(app.exec_())
