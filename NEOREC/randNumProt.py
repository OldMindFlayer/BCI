# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 07:31:24 2018

@author: Александр
"""


import sys, datetime, random, time
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QHBoxLayout, QListWidget, QListWidgetItem, QToolButton, QLabel, QScrollArea
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt


#https://oauth.vk.com/authorize?client_id=6317197&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=groups&response_type=token&v=5.69&state=123456



class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        
        
        self.resize(200,200)
        self.lblName = QLabel(self)
        self.lblName.setText(str(random.randint(1,4)))
        
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_label)
        self.timer.start(2000)
        
        newfont = QFont("Calibri", 72, QFont.Bold) 
        self.lblName.setFont(newfont)
        self.lblName.setAlignment(Qt.AlignCenter)
        
        self.layout = QGridLayout()
        self.layout.addWidget(self.lblName, 0, 0)
        self.setLayout(self.layout)
    
    def update_label(self):
        self.lblName.setText('_')
        self.lblName.setText(str(random.randint(1,4)))
        
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(random.randint(100,255),random.randint(100,255),random.randint(100,255)))
        self.setPalette(p)
    


#app = QCoreApplication.instance()
#if app is None:
#    app = QApplication(sys.argv)
#
#screen = Window()
#screen.show()
#
#sys.exit(app.exec_())


if __name__ == "__main__":
    def run_app():
        app = QApplication(sys.argv)
        mainWin = Window()
        mainWin.show()
        app.exec_()
    run_app()