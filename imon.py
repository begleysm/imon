#!/usr/bin/python3

# Filename: imon.py

"""imon (Image Monitor) is a simple tool that will watch a directory and continually show the most recent image."""

import sys
import glob
import os

from PyQt5.QtCore import Qt, QEvent, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy, QFileDialog, QLabel, QStatusBar, QToolBar
from PyQt5.QtGui import QPixmap, QIcon

__author__ = 'Sean Begley'
__copyright__ = "Copyright 2019, Sean Begley"

__license__ = "GPLv3"
__version__ = '0.1'
__maintainer__ = "Sean Begley"
__email__ = "begleysm@gmail.com"
__status__ = "Development"

# REFERENCES
# https://realpython.com/python-pyqt-gui-calculator/
# https://stackoverflow.com/questions/43569167/pyqt5-resize-label-to-fill-the-whole-window#43570124
# https://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds-in-python#474543
# https://stackoverflow.com/questions/39327032/how-to-get-the-latest-file-in-a-folder-using-python#39327156


class IMonUi(QMainWindow):
    """Main Window."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle('imon: Image Monitor')
        self.setMinimumSize(1024, 768)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setWindowIcon(QIcon('default.png'))

        # create variables
        self.watchdir = ''
        self.image_types = ('*.bmp', '*.gif', '*jpg', '*.jpeg', '*.png', '*.pbm', '*.pgm', '*.ppm', '*.xbm', '*.xpm',
                            '*.svg')
        self.wasMaximized = True

        # create border widgets
        self._createstatusbar()
        self._createtoolbar()

        # create central widget
        self.display = QLabel()
        self.display.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.display.pixmap = QPixmap('default.png')
        self.display.setPixmap(self.display.pixmap)
        self.display.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.display)

        self.installEventFilter(self)

        self.status_message = '{0: <100}'.format(os.path.dirname(os.path.realpath(__file__)) + '/default.png') + '  ' +\
                              '{0: <50}'.format(
                                  str(self.display.pixmap.width()) + 'x' + str(self.display.pixmap.height())) + '  ' +\
                              '{0: <50}'.format(str(f'{os.path.getsize("default.png") / 1000000:.2f}') + 'MB')
        self.status.showMessage(self.status_message)
        self.setStatusBar(self.status)

        # create timer action to update image
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateimage)
        self.timer.start(100)

    def updateimage(self):
        img = get_latest_image(self.watchdir, self.image_types)
        if img != '':
            # update display
            self.display.pixmap = QPixmap(img)
            self.display.setPixmap(self.display.pixmap)
            self.display.setPixmap(self.display.pixmap.scaled(self.centralWidget().size(), Qt.KeepAspectRatio))

            # update status bar
            self.status_message = '{0: <100}'.format(img) + '  ' +\
                '{0: <50}'.format(str(self.display.pixmap.width()) + 'x' + str(self.display.pixmap.height())) + '  ' +\
                '{0: <50}'.format(str(f'{os.path.getsize(img) / 1000000:.2f}') + 'MB')
            self.status.showMessage(self.status_message)
            self.setStatusBar(self.status)

    def _createtoolbar(self):
        self.tools = QToolBar()
        self.addToolBar(self.tools)
        self.tools.addAction('Exit', self.close)
        self.tools.addAction('Select Watch Directory', self._selectdir)
        self.tools.addAction('Fullscreen', self._gofullscreen)

    def _createstatusbar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def _selectdir(self):
        self.watchdir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

    def _gofullscreen(self):
        if self.isMaximized() == True:
            self.wasMaximized = True
        else:
            self.wasMaximized = False
        self.showFullScreen()
        self.tools.hide()
        self.status.hide()

    def eventFilter(self, source, event):
        if source is self and event.type() == QEvent.Resize:
            self.display.setPixmap(self.display.pixmap.scaled(self.centralWidget().size(), Qt.KeepAspectRatio))
        return super(IMonUi, self).eventFilter(source, event)

    def keyPressEvent(self, e):
        # TODO: when running showMaximized after being fullscreen, it behaves like showNormal
        if e.key() == Qt.Key_Escape:
            if self.isFullScreen():
                if self.wasMaximized == True:
                    self.showMaximized()
                    self.tools.show()
                    self.status.show()
                else:
                    self.showNormal()
                    self.tools.show()
                    self.status.show()
        if e.key() == Qt.Key_F11:
            if self.isFullScreen():
                if self.wasMaximized == True:
                    self.showMaximized()
                    self.tools.show()
                    self.status.show()
                else:
                    self.showNormal()
                    self.tools.show()
                    self.status.show()
            else:
                self._gofullscreen()


def get_latest_image(dirpath, types):
    latest_file = ''
    list_of_files = []
    if os.path.exists(os.path.dirname(dirpath)):
        for files in types:
            list_of_files.extend(glob.glob(dirpath + '/' + files))
        latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


if __name__ == '__main__':

    # create the GUI window
    app = QApplication(sys.argv)
    win = IMonUi()
    win.show()
    win.showMaximized()

    sys.exit(app.exec_())
