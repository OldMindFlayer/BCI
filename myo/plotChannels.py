# -*- coding: utf-8 -*-
"""
Created on Sat Dec  1 15:09:51 2018

@author: Alex
"""

import sys
import os
import numpy as np
import h5py
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog

from labellines import labelLines

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import pyplot as plt


class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # a figure instance to plot on
        self.figure = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some button connected to `plot` method
        self.button = QPushButton('Plot')
        self.button.clicked.connect(self.plot)

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def interpolateRow(self, y):
        nans = np.isnan(y)
        if sum(~nans) == 0:
            y = np.nan
        else:
            y[nans] = np.interp(nans.nonzero()[0],
                                (~nans).nonzero()[0], y[~nans])
        return y

    def interpolatePN(self, y, empty_fill_val=0):
        np.apply_along_axis(self.interpolateRow, 0, y)
        return y

    def on_xlims_change(self, axes):
        xlim=self.ax.get_xlim()
        xlen=xlim[1]-xlim[0]
        for t in self.legend:
            t.set_position((-0.02*xlen, t.get_position()[1]))
        
    def plot(self):

        self.figure.clear()
        # create an axis
        self.ax = self.figure.add_subplot(111)

        # discards the old graph

        self.ax.clear()

        fname, _ = QFileDialog.getOpenFileName(
            self, "Open file for plotting", "", "Nfblab expierement files (*.h5)")

        self.setWindowTitle(fname.split(os.path.sep)[-1])

        if fname:

            with h5py.File(fname, 'r+') as f1:
                data = np.array(f1['protocol1']['raw_data'])[:, :]

            print(data.shape)
            
            self.legend=[]

            if len(data.shape) > 1:

                self.setWindowTitle(fname.split(os.path.sep)[-1])

                offset = 0
                for p in range(data.shape[1]):
                    toplot = data[:, p]-np.mean(data[:, p])
                    if np.sum(np.isnan(toplot)) == toplot.shape:
                        toplot=np.zeros(toplot.shape)
                    offs = np.abs(np.min(toplot))
                    lastline, = self.ax.plot(toplot+offset+offs)
                    self.legend.append(self.ax.text(0, offset+offs+toplot[0], p, color=lastline.get_color(), clip_on=True))
                    offset += (np.max(toplot)-np.min(toplot))

        # refresh canvas
        self.canvas.draw()
        
        self.on_xlims_change(self.ax)
        self.ax.callbacks.connect('xlim_changed', self.on_xlims_change)
        
        
    




# if __name__ == '__main__':
#    app = QApplication.instance()
#    if app is None:
#        app = QApplication(sys.argv)
#
#    mainWin = Window()
#    mainWin.show()
#    sys.exit(app.exec_())


if __name__ == "__main__":
    def run_app():
        app = QApplication(sys.argv)
        mainWin = Window()
        mainWin.show()
        app.exec_()
    run_app()
